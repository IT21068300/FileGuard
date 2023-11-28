import os
import sqlite3
from lib.Config import *
from lib.DBOperate import *
from lib.Policy import setRule
from lib.FileOperate import *
from lib.MyStat import *
from PrintReport import pReport
import time
import shutil

def checkChange(c, allfile):
    for file in allfile:
        fdata = filedb
        file = file.encode('UTF-8', 'ignore').decode('UTF-8')
        fdata['PATH'] = file
        fdata['Rule_Type'], fdata['Rule_Check'] = setRule(file)
        if not fdata['Rule_Check'] == '':
            a = queryFileData(c, 'FILEDB', fdata['PATH'])
            if a is None:  # Not in initdb
                fdata = collectFileData(fdata)
                if not fdata is None:
                    if 'l' not in fdata['Rule_Check']:
                        fdata['Record'] = 'a'
                        print('New file:', fdata['PATH'])
                        c.execute(SQLinsert('FILEDB', fdata))
                    else:
                        fdata['Record'] = 'c'
                        c.execute(SQLinsert('FILEDB', fdata))

            else:
                flag = 1
                fdata = collectFileData(fdata)
                if not fdata is None:
                    originStat = Mystat(a[1]).__dict__  # Get the original stat
                    newStat = Mystat(fdata['STAT']).__dict__  # Newly obtained stat
                    for i in fdata['Rule_Check']:
                        if i in StatMap:
                            if originStat[StatMap[i]] != newStat[StatMap[i]]:
                                print('Modified file:', fdata['PATH'])
                                fdata['Record'] = 'm'
                                c.execute(SQLupdate('FILEDB', fdata['PATH'], fdata))
                                flag = 0
                                break
                    if flag:
                        fdata['Record'] = 'c'
                        c.execute(SQLupdate('FILEDB', fdata['PATH'], fdata))
    SQLQuery = "DELETE FROM FILEDB WHERE Record='c'"
    c.execute(SQLQuery)

if __name__ == '__main__':
    now = time.time()
    checkDBName = formatTime(now) + '.db'
    checkTxtName = formatTime(now) + '.txt'
    checkDBPath = os.path.join(dataDir, checkDBName)
    checkTxtPath = os.path.join(dataDir, checkTxtName)

    # Check if the initial database exists
    if os.path.exists(initDB_Path):
        print(f"Initial database '{initDB_Path}' exists.")
    else:
        print(f"Initial database '{initDB_Path}' not found. Please check the path.")
        exit(1)  # Exit the script if the initial database is not found

    # Remove the existing database before copying the initial one
    if os.path.exists(checkDBPath):
        os.remove(checkDBPath)

    # Copy the initial database to create a new one
    shutil.copy(initDB_Path, checkDBPath)
    print('Database created successfully')

    # Connect to the new database
    connect = sqlite3.connect(checkDBPath)
    c = connect.cursor()
     # Create the FILEDB table if it doesn't exist
    c.execute("""
    CREATE TABLE IF NOT EXISTS FILEDB (
        PATH  char(600) PRIMARY KEY  NOT NULL,
        STAT   char NOT NULL,
        MD5        char,
        Rule_Type  char,
        Rule_Check char,
        Record char(1));
    """)

    # Commit the table creation
    connect.commit()

    allfile = getDirData()
    checkChange(c, allfile)  # Pass the cursor to the function
    print(time.time() - now)
    connect.commit()

    # Vacuum and close the connection
    connect.execute("VACUUM")
    c.close()
    connect.close()

    # Generate and send the report
    pReport(checkDBPath, checkTxtPath)

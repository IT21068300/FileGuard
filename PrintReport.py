import re
from lib.Config import *
from lib.FormatInfo import *
from lib.MyStat import MystatFormated
import sqlite3
import re

Objects = {}
RuleHead = ''

def getReportTxt():
    Report = {}
    with open('data/rp', 'r', encoding='utf-8') as f:
        txt = f.read()
        f.close()
    a = re.findall('\(\d-(?P<name>\w+)\)(.*?)\(\d-(?P=name)\)', txt, re.S | re.M)
    for i in a:
        Report[i[0]] = i[1]
    return Report

def getData(datapath):
    global Objects
    connCheck = sqlite3.connect(datapath)
    cCheck = connCheck.cursor()
    connInit = sqlite3.connect(initDB_Path)
    cInit = connInit.cursor()
    cCheck.execute("select Rule_Type from FILEDB group by Rule_Type;")
    Rule_Type = cCheck.fetchall()
    for i in Rule_Type:
        Objects[i[0]] = {}
        cCheck.execute("select Record from FILEDB where Rule_Type='%s' group by Record;" % i[0])
        Record = cCheck.fetchall()
        for j in Record:
            Objects[i[0]][j[0]] = []
            cCheck.execute("select PATH, STAT, MD5 from FILEDB where Rule_Type='%s' and Record='%s'" % (i[0], j[0]))
            Result = cCheck.fetchall()
            for k in Result:
                row = {}
                row['PATH'] = k[0]
                row['NEW'] = {}
                row['ORIGIN'] = {}
                if j[0] == 'm':
                    row['NEW']['STAT'] = MystatFormated(k[1]).__dict__
                    row['NEW']['MD5'] = k[2]
                    cInit.execute("select STAT, MD5 from FILEDB where PATH='%s'" % row['PATH'])
                    origin = cInit.fetchall()[0]
                    row['ORIGIN']['STAT'] = MystatFormated(origin[0]).__dict__
                    row['ORIGIN']['MD5'] = origin[1]
                elif j[0] == 'a':
                    row['NEW']['STAT'] = MystatFormated(k[1]).__dict__
                    row['NEW']['MD5'] = k[2]
                elif j[0] == 'o':
                    row['NEW']['STAT'] = MystatFormated(k[1]).__dict__
                    row['NEW']['MD5'] = k[2]
                    row['ORIGIN']['STAT'] = MystatFormated(k[1]).__dict__
                    row['ORIGIN']['MD5'] = k[2]
                Objects[i[0]][j[0]].append(row)
    cInit.close()
    connInit.close()
    cCheck.close()
    connCheck.close()
    return Objects

def getReportSummary(ReportSummary):
    username = getUser()
    hostname = getHostName()
    hostip = getHostIp()
    timenow = formatTime(time.time())
    ReportSummary = re.sub('\$\(HName\)', hostname, ReportSummary)
    ReportSummary = re.sub('\$\(HostIP\)', hostip, ReportSummary)
    ReportSummary = re.sub('\$\(user\)', username, ReportSummary)
    ReportSummary = re.sub('\$\(time\)', timenow, ReportSummary)
    return ReportSummary

def getRuleSummary(RuleSummary):
    count = 0
    for i in Objects:
        row = '  '
        RuleName = i
        row = row + RuleName.ljust(32, " ")
        row = row + '0'.ljust(18, ' ')
        if 'a' in Objects[i]:
            l = len(Objects[i]['a'])
            count = count + l
            row = row + str(l).ljust(9, ' ')
        else:
            row = row + '0'.just(9, ' ')

        if 'o' in Objects[i]:
            l = len(Objects[i]['o'])
            count = count + l
            row = row + str(l).ljust(9, ' ')
        else:
            row = row + '0'.ljust(9, ' ')

        if 'm' in Objects[i]:
            l = len(Objects[i]['m'])
            count = count + l
            row = row + str(l).ljust(9, ' ')
        else:
            row = row + '0'.ljust(9, ' ')
        row = row + '\n'
        RuleSummary = RuleSummary + row + '\n'
    RuleSummary = RuleSummary + 'Total violations found:' + str(count) + '\n'
    return RuleSummary

def getRuleHead(RuleName):
    return re.sub('\$\(RuleName\)', RuleName, RuleHead, re.M)

def getRuleDetail():
    RulesDetail = ''
    for Rule in Objects:
        group = getRuleHead(Rule)
        for i in Objects[Rule]:
            group = group + recordmap[i] + ':\n'
            for j in Objects[Rule][i]:
                row = '"' + j['PATH'] + '"\n'
                group = group + row
        RulesDetail = RulesDetail + group
    return RulesDetail

def getChangeDetail(ChangeDetail):
    ChangeDetails = ''
    for Rule in Objects:
        group = getRuleHead(Rule)
        for i in Objects[Rule]:
            for j in Objects[Rule][i]:
                ObjectHeader = re.sub('\$\(PATH\)', j['PATH'], ChangeDetail, re.M)
                ObjectHeader = re.sub('\$\(change\)', recordmap[i], ObjectHeader, re.M)
                group = group + ObjectHeader
                for st in j['NEW']['STAT']:
                    if i == 'm':
                        row = '  ' + st.ljust(21, ' ') + \
                              j['ORIGIN']['STAT'][st].ljust(35, ' ') + \
                              j['NEW']['STAT'][st].ljust(35, ' ') + '\n'
                    elif i == 'a':
                        row = '  ' + st.ljust(21, ' ') + \
                              '---'.ljust(35, ' ') + \
                              j['NEW']['STAT'][st].ljust(35, ' ') + '\n'
                    elif i == 'o':
                        row = '  ' + st.ljust(21, ' ') + \
                              j['ORIGIN']['STAT'][st].ljust(35, ' ') + \
                              '---'.ljust(35, ' ') + '\n'
                    group = group + row
                if i == 'm':
                    row = '  ' + 'MD5'.ljust(21, ' ') + \
                          j['ORIGIN']['MD5'].ljust(35, ' ') + \
                          j['NEW']['MD5'].ljust(35, ' ') + '\n'
                elif i == 'a':
                    row = '  ' + 'MD5'.ljust(21, ' ') + \
                          '---'.ljust(35, ' ') + \
                          j['NEW']['MD5'].ljust(35, ' ') + '\n'
                elif i == 'o':
                    row = '  ' + 'MD5'.ljust(21, ' ') + \
                          j['ORIGIN']['MD5'].ljust(35, ' ') + \
                          '---'.ljust(35, ' ') + '\n'
                group = group + row
        ChangeDetails = ChangeDetails + group
    return ChangeDetails

def printReport(output_file):
    global RuleHead
    Report = getReportTxt()
    RuleHead = Report['RuleHead']
    Report['ReportSummary'] = getReportSummary(Report['ReportSummary'])
    Report['RuleSummary'] = getRuleSummary(Report['RuleSummary'])
    Report['RuleDetail'] = getRuleDetail()
    Report['ChangeDetail'] = getChangeDetail(Report['ChangeDetail'])
    ReportTxt = Report['ReportSummary'] + Report['RuleSummary'] + Report['RuleDetail'] + Report['ChangeDetail']
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(ReportTxt)
        f.close()

if __name__ == '__main__':
    input_file = dataDir + '/test.db'
    output_file = dataDir + '/test.txt'
    Objects = getData(input_file)
    printReport(output_file)

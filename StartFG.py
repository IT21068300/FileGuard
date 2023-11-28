import os
import subprocess
from lib.Config import initDB_Path

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def welcome_screen():
    welcome_message = """
**************************************************
*                                                *
*            Welcome to FileGuard 1.0            *
*                                                *
**************************************************

██╗░░░░░░█████╗░░█████╗░███╗░░░██╗██╗███╗░░░███╗
██║░░░░░██╔══██╗██╔══██╗████╗░░██║██║████╗░████║
██║░░░░░██║░░██║██║░░█║██╔██╗░██║██║██╔████╔██║
██║░░░░░██║░░██║██║░░██║██║╚██╗██║██║██║╚██╔╝██║
███████╗╚█████╔╝╚█████╔╝██║░╚████║██║██║░╚═╝░██║
╚══════╝░╚════╝░░╚════╝░╚═╝░░╚═══╝╚═╝╚═╝░░░░░╚═╝

Thank you for choosing FileGuard 1.0!
Your Security Monitoring Tool built with Sqlite3 and Python.
"""

    print(welcome_message)
    print("To get started, follow the prompts:")
    print("Stay secure with FileGuard!\n")

def main():
    welcome_screen()

    # Check if it's the first time running
    if not os.path.exists(initDB_Path):
        print("This seems to be your first time running FileGuard.")
        print("Running Init.py to initialize the initial database...\n")
        run_command("sudo python3 Init.py")
        print("\nInitialization complete! Please come back after system changes.")
        exit()

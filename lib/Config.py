import os

# Project Directory
ProjectDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))

# Data Storage Directory
dataDir = os.path.join(ProjectDir, 'data')

# Initial Database Path
initDB_Path = os.path.join(dataDir, 'init.db')

# Configuration File Storage Directory
etcDir = os.path.join(ProjectDir, 'etc')

# Policy Configuration Directory
PolicyDir = os.path.join(ProjectDir, 'Policy')

# Configuration File Path
policyPath = os.path.join(PolicyDir, 'Policy.txt')


import socket
import getpass

def getHostIp():
    """
    Query the local IP address
    :return: IP address
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def getUser():
    """
    Get the current username
    :return: Username
    """
    return getpass.getuser()

def getHostName():
    """
    Get the hostname of the system
    :return: Hostname
    """
    return socket.gethostname()

from socket import inet_aton

from lxml import etree
from prettytable import PrettyTable as Table


VERSION = "Gyuto 0.1.2"


def command(func):
    """Decorate a function to automatically be a subcommand
    
    This is a stub for possible future use
    """

    def wrapped():
        pass
    return wrapped


def parse_file(target):
    return etree.parse(target)


def sort_hosts(hosts):
    """Return a sorted list of host IP addresses"""

    return sorted(hosts, key=inet_aton)


def identify_format(tree):
    """Return the format of the XML file, or "unknown"
    
    Possible return values are:
     - "nmap"
     - "nessus"
     - "nexpose"
     - "qualys"
     - "unknown"

    Notes:
     - The return value should be safe to eval()
     - There must be a more efficient way to do the testing...
    """

    QUALYS = '<!DOCTYPE SCAN SYSTEM "https://qualysguard.qualys.com/scan-1.dtd">'

    if tree.xpath("/nmaprun"):
        return "nmap"
    elif tree.xpath("/NessusClientData_v2"):
        return "nessus"
    elif tree.xpath("/NexposeReport[@version='2.0']"):
        return "nexpose"
    elif tree.docinfo.doctype == QUALYS:
        return "qualys"
    else:
        return "unknown"


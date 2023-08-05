#!/usr/bin/env python
"""
Gyuto 0.1.2
Slice and dice scan results

Usage:
  gyuto hosts [options] <target>

Options:
  -f --filter=<filter>  Filter by a named filter
  -p --port=<port>      Filter by open port/service
  --os=<os>             Filter by operating system
  --cpe=<cpe>           Filter by CPE string
  --pid=<pid>           Filter by plugin ID
  --cve=<cve>           Filter by CVE ID
  --cvssmin=<cvssmin>   Filter by CVSS score
  -h --help             Show this help screen

Examples:
  gyuto hosts -p 80,443
  gyuto hosts --cve=2011-1575
  gyuto hosts --filter=java-vulns

"""
from docopt import docopt

from gyuto.core import parse_file, identify_format, Table
from gyuto.core.results import PortResult, ServiceResult, SoftwareResult
from gyuto.parsers import nmap, nessus, nexpose


def print_hosts(target):
    tree = parse_file(target)
    fmt = identify_format(tree)
    try:
        parser = eval(fmt)
    except NameError:
        print("gyuto_stats: Format \"{}\" is invalid".format(fmt))
        return
    print("{0} appears to be valid {1} data".format(target, fmt))
    # stuff goes here


def main():
    args = docopt(__doc__)
    # TODO use schema to validate filename
    target = args.get("<target>")
    print_hosts(target)


if __name__ == "__main__":
    main()


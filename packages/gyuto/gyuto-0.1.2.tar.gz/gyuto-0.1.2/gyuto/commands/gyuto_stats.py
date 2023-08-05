#!/usr/bin/env python
"""
Gyuto 0.1.2
Slice and dice scan results

Usage:
  gyuto stats <target>

Options:
  -h --help     Show this help screen
  -v --version  Show version

"""
from docopt import docopt

from gyuto.core import parse_file, identify_format, Table
from gyuto.core.results import PortResult, ServiceResult, SoftwareResult
from gyuto.parsers import nmap, nessus, nexpose


def print_stats(target):
    tree = parse_file(target)
    fmt = identify_format(tree)
    try:
        parser = eval(fmt)
    except NameError:
        print("gyuto_stats: Format \"{}\" is invalid".format(fmt))
        return
    print("{0} appears to be valid {1} data".format(target, fmt))
    start_time, end_time = parser.get_scan_times(tree)
    delta_time = end_time - start_time
    print("Scan start time: {}".format(start_time))
    print("Scan end time: {}".format(end_time))
    print("Scan duration: {}".format(delta_time))
    hosts = parser._get_hosts_list(tree)
    print("Number of hosts scanned: {}".format(len(hosts)))


def main():
    args = docopt(__doc__)
    # TODO use schema to validate filename
    target = args.get("<target>")
    print_stats(target)


if __name__ == "__main__":
    main()


#!/usr/bin/env python
"""
gyuto-search 0.1.2
playing around with different options for API

Usage:
  gyuto search <type> <params> <target>
  gyuto search <query> <target>

Options:
  -h --help     Show this help screen
  -v --version  Show version

Query Parameters:
  host          address, os
  software      name
  vuln          name, plugin, tags, severity

Examples:
  gyuto search host cve=2012-2424 target.xml
  gyuto search "host where address = 192.168.1.1" target.xml

"""
from docopt import docopt

from gyuto.core import parse_file, identify_format, Table
from gyuto.core.results import PortResult, ServiceResult, SoftwareResult
from gyuto.parsers import nmap, nessus, nexpose


def parse_params(params):
    # this is pretty bad...
    #params = params.split("=", 1)
    return params.split("=", 1)


def main():
    args = docopt(__doc__)
    # TODO use schema to validate filename
    target = args.get("<target>")
    print("Command not implemented")


if __name__ == "__main__":
    main()


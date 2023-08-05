#!/usr/bin/env python
"""
Gyuto 0.1.2
Slice and dice scan results

Usage:
  gyuto lookup [options] <query>

Options:
  -h --help             Show this help screen

Examples:
  gyuto lookup cve-2008-4250
  gyuto lookup ms08-067

"""
import pprint
import textwrap
import re

from docopt import docopt
# TODO: from schema import Schema

from gyuto.core import Table
from gyuto.core.resources import get_cvedetails, get_mstn


TABLE_OPTS = {
    "header": False,
    "max_width": 40,
}


CVE = re.compile("CVE-\d\d\d\d-\d\d\d\d", re.IGNORECASE)
MSB = re.compile("MS\d\d-\d\d\d", re.IGNORECASE)


def _print_cvedetails_table(query):
    res = get_cvedetails(query)
    table = Table(**TABLE_OPTS)
    table.max_width[1] = 40
    table.add_row(["CVE ID", res.get("id")])
    table.add_row(["CVSS score", res.get("score")])
    table.add_row(["Date Published", res.get("date_published")])
    table.add_row(["Date Updated", res.get("date_updated")])
    table.add_row(["Summary", res.get("summary")])
    print(table)


def print_cvedetails(query):
    res = get_cvedetails(query)
    print("CVE ID: {}".format(res.get("id")))
    print("Published: {}".format(res.get("date_published")))
    print("Updated: {}".format(res.get("date_updated")))
    print("CVSS score: {}".format(res.get("score")))
    print("Vulnerability Types: {}".format(",".join(res.get("types"))))
    print(textwrap.fill("Summary: {}".format(res.get("summary")), width=80))


def pprint_cvedetails(query):
    results = get_cvedetails(query)
    pprint.pprint(results)


def print_mstn(query):
    # raise NotImplementedError("This function hasn't been written yet!")
    res = get_mstn(query)
    print("CVE ID: {}".format(res.get("id")))
    print("Title: {}".format(res.get("title")))
    print("Published: {}".format(res.get("date_published")))


def main():
    args = docopt(__doc__)
    query = args.get("<query>")
    if CVE.match(query):
        print_cvedetails(query)
    elif MSB.match(query):
        print_mstn(query)
    else:
        print("Invalid Query")
        print(__doc__)


if __name__ == "__main__":
    main()

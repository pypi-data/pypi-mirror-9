#!/usr/bin/env python
"""
Gyuto 0.1.2
Slice and dice scan results

Usage:
  gyuto chart summary <target>
  gyuto chart java <target>

Options:
  -h --help     Show this help screen
  -v --version  Show version

"""
import json
from collections import Counter

from docopt import docopt

from gyuto.core import parse_file, identify_format, Table
from gyuto.core.results import PortResult, ServiceResult, SoftwareResult
from gyuto.core.templates import env
from gyuto.parsers import nmap, nessus, nexpose


def build_csv(data, filename="gyuto_data.csv"):
    """Create basic CSV file from data
    
    "data" should be a dict-type, output lines are of the form "{key},{value}"
    """

    with open(filename, "w") as fout:
        fout.write("name,value\n")
        for k,v in data.iteritems():
            fout.write("{0},{1}\n".format(k,v))


def build_html(filename="gyuto_chart.html"):
    with open(filename, "w") as fout:
        # write out to templates
        template = env.get_template("d3_bar.html")
        fout.write(template.render(title="Gyuto Chart", filename="gyuto_data.csv"))


def chart_java_versions(target):
    tree = parse_file(target)
    # which parser to use?
    fmt = identify_format(tree)
    try:
        parser = eval(fmt)
    except NameError:
        print("Format \"{}\" is invalid".format(fmt))
        return
    versions = parser.get_java_versions(tree)
    counts = Counter([v.version for v in versions])
    build_csv(counts)
    build_html()
    print("Chart data written out to \"gyuto_chart.html\"")


def main():
    args = docopt(__doc__)
    # TODO use schema to validate filename
    target = args.get("<target>")
    if args.get("java"):
        chart_java_versions(target)
    else:
        print("Command not implemented")


if __name__ == "__main__":
    main()


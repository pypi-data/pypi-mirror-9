#!/usr/bin/env python
"""
Gyuto 0.1.2
Slice and dice scan results

Usage:
  gyuto merge [options] <files>...

Options:
  -o --output=<output>  Output filename [default: merged.nessus]
  -t --title=<title>    Output report title [default: Gyuto Merged Report]
  -h --help             Show this help screen
  -v --version          Show version

Note that merge is ONLY supported for Nessus (v2) file formats at this time!
"""
from docopt import docopt

from gyuto.core import parse_file, identify_format, Table
from gyuto.core.results import PortResult, ServiceResult, SoftwareResult
from gyuto.parsers import nmap, nessus, nexpose


def validate(tree):
    if identify_format(tree) != "nessus":
        print("{} is not a valid Nessus v2 file!")
        sys.exit()


def get_merged_tree(files, report_title):
    """Take a list of .nessus file paths and return a merged etree"""

    filepath = files[0]
    merged_tree = parse_file(filepath)
    validate(merged_tree)
    merged_report = merged_tree.find("Report")
    merged_report.attrib["name"] = report_title

    for filepath in files[1:]:
        tree = parse_file(filepath)
        for host in tree.findall(".//ReportHost"):
            hostname = host.attrib.get("name")
            query = ".//ReportHost[@name='{name}']".format(name=hostname)
            existing_host = merged_report.find(query)
            if existing_host is None:
                print(" [*] Adding host: " + hostname)
                merged_report.append(host)
            else:
                for item in host.findall("ReportItem"):
                    query = "ReportItem[@port='{port}'][@pluginID='{pid}']"
                    query = query.format(port=item.attrib.get("port"),pid=item.attrib.get("pluginID"))
                    if existing_host.find(query):
                        print(" [*] Adding finding: " + item.attrib.get("port") + ":" + item.attrib.get("pluginID"))
                        existing_host.append(item)
        print(":: => Done")
    return merged_tree


def merge_nessus(files, output_filename="merged.nessus", report_title="Gyuto Merged Report"):
    """Generate a merged nessus report"""

    merged_tree = get_merged_tree(files, report_title)
    merged_tree.write(output_filename, encoding="utf-8", xml_declaration=True)


def main():
    args = docopt(__doc__)
    # TODO use schema to validate filename
    targets = args.get("<files>")
    output = args.get("--output")
    title = args.get("--title")
    merge_nessus(targets, output_filename=output, report_title=title)


if __name__ == "__main__":
    main()


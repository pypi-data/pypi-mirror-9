#!/usr/bin/env python
"""
Gyuto 0.1.2
Slice and dice scan results

Usage:
  gyuto show summary <target>
  gyuto show results <target>
  gyuto show services <target>
  gyuto show hostnames <target>
  gyuto show java <target>
  gyuto show flash <target>
  gyuto show air <target>
  gyuto show firefox <target>
  gyuto show adobe <target>
  gyuto show plugin <plugin_id> <target>
  gyuto show mshotfix <hotfix_id> <target>

Options:
  -h --help     Show this help screen
  -v --version  Show version

"""
from docopt import docopt

from gyuto.core import parse_file, identify_format, Table
from gyuto.core.results import PortResult, ServiceResult, SoftwareResult
from gyuto.parsers import nmap, nessus, nexpose


GENERATORS = {
        "summary": nmap.summary_by_host,
        "results": nmap.results_by_host,
        }


def print_table(headers, gen):
    table = Table(headers)
    table.padding_width = 1
    table.align = "l"
    for result in gen:
        table.add_row(result)
    print(table)


def print_hostnames(target):
    tree = parse_file(target)
    fmt = identify_format(tree)
    try:
        parser = eval(fmt)
    except NameError:
        print("gyuto_show: Format \"{}\" is invalid".format(fmt))
        return
    gen = parser.get_hostnames(tree)
    table = Table(["Host", "Names"])
    table.padding_width = 1
    table.align = "l"
    for result in gen:
        table.add_row(result)
    print(table)


def print_nmap_results(target, generator):
    tree = parse_file(target)
    gen = GENERATORS.get(generator)(tree)
    table = Table(PortResult._fields)
    table.padding_width = 1
    table.align = "l"
    for result in gen:
        table.add_row(result)
    print(table)


def print_services(target):
    tree = parse_file(target)
    fmt = identify_format(tree)
    try:
        parser = eval(fmt)
    except NameError:
        print("Format \"{}\" is invalid".format(fmt))
        return
    gen = parser.get_services_by_host(tree)
    print_table(ServiceResult._fields, gen)


def print_software_versions(target, software):
    tree = parse_file(target)
    fmt = identify_format(tree)
    try:
        parser = eval(fmt)
    except NameError:
        print("Format \"{}\" is invalid".format(fmt))
        return
    gen = parser.get_air_versions(tree)
    table = Table(SoftwareResult._fields)
    table.padding_width = 1
    table.align = "l"
    for result in gen:
        table.add_row(result)
    print(table)


def print_java_versions(target):
    tree = parse_file(target)
    # which parser to use?
    fmt = identify_format(tree)
    try:
        parser = eval(fmt)
    except NameError:
        print("Format \"{}\" is invalid".format(fmt))
        return
    gen = parser.get_java_versions(tree)
    table = Table(SoftwareResult._fields)
    table.padding_width = 1
    table.align = "l"
    for result in gen:
        table.add_row(result)
    print(table)


def print_flash_versions(target):
    tree = parse_file(target)
    fmt = identify_format(tree)
    try:
        parser = eval(fmt)
    except NameError:
        print("Format \"{}\" is invalid".format(fmt))
        return
    gen = parser.get_flash_versions(tree)
    table = Table(SoftwareResult._fields)
    table.padding_width = 1
    table.align = "l"
    for result in gen:
        table.add_row(result)
    print(table)


def print_firefox_versions(target):
    tree = parse_file(target)
    fmt = identify_format(tree)
    try:
        parser = eval(fmt)
    except NameError:
        print("Format \"{}\" is invalid".format(fmt))
        return
    gen = parser.get_firefox_versions(tree)
    table = Table(SoftwareResult._fields)
    table.padding_width = 1
    table.align = "l"
    for result in gen:
        table.add_row(result)
    print(table)


def print_adobe_versions(target):
    tree = parse_file(target)
    fmt = identify_format(tree)
    try:
        parser = eval(fmt)
    except NameError:
        print("Format \"{}\" is invalid".format(fmt))
        return
    gen = parser.get_adobe_versions(tree)
    table = Table(SoftwareResult._fields)
    table.padding_width = 1
    table.align = "l"
    for result in gen:
        table.add_row(result)
    print(table)


def print_hosts_by_mshotfix(target, hotfix_id):
    tree = parse_file(target)
    fmt = identify_format(tree)
    try:
        parser = eval(fmt)
    except NameError:
        print("Format \"{}\" is invalid".format(fmt))
        return
    for host in parser.get_hosts_by_mshotfix(tree, hotfix_id):
        print("{0} ({1}) - {2}".format(host.hostname, host.address, host.os))


def main():
    args = docopt(__doc__)
    # TODO use schema to validate filename
    target = args.get("<target>")
    if args.get("java"):
        print_java_versions(target)
    elif args.get("flash"):
        print_flash_versions(target)
    elif args.get("firefox"):
        print_firefox_versions(target)
    elif args.get("adobe"):
        print_adobe_versions(target)
    elif args.get("air"):
        print_software_versions(target, "air")
    elif args.get("services"):
        print_services(target)
    elif args.get("summary"):
        print_nmap_results(target, "summary")
    elif args.get("results"):
        print_nmap_results(target, "results")
    elif args.get("hostnames"):
        print_hostnames(target)
    elif args.get("mshotfix"):
        hotfix_id = args.get("<hotfix_id>")
        print_hosts_by_mshotfix(target, hotfix_id)
    else:
        print("Command not implemented")


if __name__ == "__main__":
    main()


#!/usr/bin/env python
"""
Gyuto 0.1.2
Slice and dice scan results

Usage:
  gyuto diff [options] <target1> <target2>

Options:
  -h --help          Show this help screen
  -t --type=<type>   Focus diff on specific aspect of the scans
  --cvssmin=<value>  Filter by vulnerability's CVSS score [default: 0]
  --cvssmax=<value>  Filter by vulnerability's CVSS score [default: 10]
  -V --verbose       Print full data including each affected host

Supported Types:
  host
  port
  vuln
  ms

Examples:
  gyuto diff nessus-scan.xml nexpose-scan.xml

"""
from docopt import docopt

from gyuto.core import *
from gyuto.parsers import nmap, nessus, nexpose, qualys


def _parse_two(target1, target2):
    tree1 = parse_file(target1)
    tree2 = parse_file(target2)
    format1 = identify_format(tree1)
    print("{0} identified as {1}".format(target1, format1))
    format2 = identify_format(tree2)
    print("{0} identified as {1}".format(target2, format2))
    # TODO: evals are safe as long as identify_format has a defined set of safe
    # outputs?
    parser1 = eval(format1)
    parser2 = eval(format2)
    return (tree1, parser1, tree2, parser2)


def _print_hosts(s1, s2):
    left = sorted(list(s1 - s2))
    right = sorted(list(s2 - s1))
    both = sorted(list(s1 & s2))
    for host in left:
        print("[<<] {}".format(host))
    for host in right:
        print("[>>] {}".format(host))
    for host in both:
        print("[==] {}".format(host))


def vuln_diff(target1, target2):
    tree1 = parse_file(target1)
    tree2 = parse_file(target2)
    format1 = identify_format(tree1)
    print("{0} identified as {1}".format(target1, format1))
    format2 = identify_format(tree2)
    print("{0} identified as {1}".format(target2, format2))
    # TODO: evals are safe as long as identify_format has a defined set of safe
    # outputs?
    f1 = eval(format1)
    f2 = eval(format2)
    d1 = f1.get_cve_dict(tree1)
    d2 = f2.get_cve_dict(tree2)
    print("{0} had {1} total CVEs".format(target1, len(d1)))
    print("{0} had {1} total CVEs".format(target2, len(d2)))
    cves = list(set(list(d1.keys()) + list(d2.keys())))
    cves.sort()
    total_left = total_both = total_right = 0
    for cve in cves:
        s1 = set(d1[cve])
        s2 = set(d2[cve])
        left = len(s1 - s2)
        both = len(s1 & s2)
        right = len(s2 - s1)
        print("{0}: {1} {2} {3}".format(cve, left, both, right))
        total_left += left
        total_both += both
        total_right += right
    print("====================")
    print("TOTAL: {0} {1} {2}".format(total_left, total_both, total_right))


def diff_hosts(target1, target2, verbose=False):
    tree1, parser1, tree2, parser2 = _parse_two(target1, target2)
    s1 = set(parser1.get_host_addrs(tree1))
    s2 = set(parser2.get_host_addrs(tree2))
    left = sorted(list(s1 - s2))
    right = sorted(list(s2 - s1))
    both = sorted(list(s1 & s2))
    print("Hosts unique to first: {}".format(len(left)))
    print("Hosts unique to second: {}".format(len(right)))
    print("Hosts found in both: {}".format(len(both)))
    if verbose:
        for host in left:
            print("<< {}".format(host))
        for host in right:
            print(">> {}".format(host))
        for host in both:
            print("== {}".format(host))


def diff_ports(target1, target2, verbose=False):
    tree1, parser1, tree2, parser2 = _parse_two(target1, target2)
    d1 = parser1.map_hosts_by_port(tree1)
    d2 = parser2.map_hosts_by_port(tree2)
    ports = sorted(list(set(list(d1.keys()) + list(d2.keys()))))
    total_left = total_both = total_right = 0
    for port in ports:
        s1 = set(d1[port])
        s2 = set(d2[port])
        left = len(s1 - s2)
        both = len(s1 & s2)
        right = len(s2 - s1)
        print("{0}: {1} {2} {3}".format("/".join([port[0], str(port[1])]), left, both, right))
        if verbose:
            _print_hosts(s1, s2)
        total_left += left
        total_both += both
        total_right += right
    print("====================")
    print("TOTAL: {0} {1} {2}".format(total_left, total_both, total_right))


def diff_cves(target1, target2, cvss_min=0, cvss_max=10, verbose=False):
    tree1, parser1, tree2, parser2 = _parse_two(target1, target2)
    d1 = parser1.get_cve_dict(tree1)
    d2 = parser2.get_cve_dict(tree2)
    print("{0} had {1} total CVEs".format(target1, len(d1)))
    print("{0} had {1} total CVEs".format(target2, len(d2)))
    cves = list(set(list(d1.keys()) + list(d2.keys())))
    cves.sort()
    total_left = total_both = total_right = 0
    for cve in cves:
        s1 = set(d1[cve])
        s2 = set(d2[cve])
        left = len(s1 - s2)
        both = len(s1 & s2)
        right = len(s2 - s1)
        print("{0}: {1} {2} {3}".format(cve, left, both, right))
        if verbose:
            _print_hosts(s1, s2)
        total_left += left
        total_both += both
        total_right += right
    print("====================")
    print("TOTAL: {0} {1} {2}".format(total_left, total_both, total_right))


def diff_mshotfixes(target1, target2, cvss_min=0, cvss_max=10, verbose=False):
    tree1, parser1, tree2, parser2 = _parse_two(target1, target2)
    d1 = parser1.map_hosts_by_mshotfix(tree1, cvss_min)
    d2 = parser2.map_hosts_by_mshotfix(tree2, cvss_min)
    hotfixes = sorted(list(set(list(d1.keys()) + list(d2.keys()))))
    total_left = total_both = total_right = 0
    for hf in hotfixes:
        s1 = set(d1[hf])
        s2 = set(d2[hf])
        left = len(s1 - s2)
        both = len(s1 & s2)
        right = len(s2 - s1)
        print("{0}: {1} {2} {3}".format(hf.upper(), left, both, right))
        if verbose:
            _print_hosts(s1, s2)
        total_left += left
        total_both += both
        total_right += right
    print("====================")
    print("TOTAL: {0} {1} {2}".format(total_left, total_both, total_right))


def main():
    args = docopt(__doc__)
    target1 = args.get("<target1>")
    target2 = args.get("<target2>")
    type_ = args.get("--type")
    cvss_min = args.get("--cvssmin")
    cvss_max = args.get("--cvssmax")
    verbose = args.get("--verbose")
    if type_ == "host":
        diff_hosts(target1, target2, verbose=verbose)
    elif type_ == "port":
        diff_ports(target1, target2, verbose=verbose)
    elif type_ == "ms":
        diff_mshotfixes(target1, target2, cvss_min, cvss_max, verbose=verbose)
    else:
        diff_cves(target1, target2, verbose=verbose)


if __name__ == "__main__":
    main()

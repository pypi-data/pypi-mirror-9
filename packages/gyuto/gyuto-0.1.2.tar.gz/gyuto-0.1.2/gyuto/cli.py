#!/usr/bin/env python
"""
Gyuto 0.1.2
Slice and dice scan results

Usage:
  gyuto [options] <command> [<args>...]

Options:
  -d --debug    Print parsed args/opts and exit
  -o --output   Change output type (default is stdout)
  -h --help     Show this help screen
  -v --version  Show version

Commands:
  identify      Identify report file formats
  stats         Display scan statistics
  show          Display data from report files
  diff          Compare two report files
  chart         Generate a visualization (UNIMPLEMENTED)
  merge         Combine multiple report files (Nessus v2 format only)
  lookup        Get data about a particular CVE or MSB

Supported file formats:
  Nmap XML
  Nessus v2 XML
  Nexpose XML Export 2.0
  Qualys XML (scan-1.dtd)

"""
from docopt import docopt

from gyuto.core import parse_file, identify_format
# from gyuto.parsers import nmap, nessus, nexpose


VERSION = "Gyuto 0.1.2"
CHOICES = ["nmap", "nessus", "nexpose"]
GENERATORS = {
    # "summary": nmap.summary_by_host,
    # "results": nmap.results_by_host,
    }
DISPATCH = {
    # "identify": identify,
    # "show":     show,
    }


def identify(target):
    """
    Usage:
      gyuto identify <target>
    
    """

    tree = parse_file(target)
    print(identify_format(tree))


def dispatch(command):
    pass


def main():
    args = docopt(__doc__, version=VERSION, options_first=True)
    if args["--debug"]:
        print(args)
    elif args["<command>"] == "identify":
        subargs = docopt(identify.__doc__, argv=["identify"]+args["<args>"])
        identify(subargs.get("<target>"))
    elif args.get("<command>") == "stats":
        from gyuto.commands import gyuto_stats
        gyuto_stats.main()
    elif args.get("<command>") == "show":
        from gyuto.commands import gyuto_show
        gyuto_show.main()
    elif args.get("<command>") == "diff":
        from gyuto.commands import gyuto_diff
        gyuto_diff.main()
    elif args.get("<command>") == "chart":
        from gyuto.commands import gyuto_chart
        gyuto_chart.main()
    elif args.get("<command>") == "merge":
        from gyuto.commands import gyuto_merge
        gyuto_merge.main()
    elif args.get("<command>") == "hosts":
        from gyuto.commands import gyuto_hosts
        gyuto_hosts.main()
    elif args.get("<command>") == "lookup":
        from gyuto.commands import gyuto_lookup
        gyuto_lookup.main()
    else:
        print("Currently not implemented")
        # argv = [args["<command>"]] + args["<args>"]
        # dispatch(argv)


if __name__ == "__main__":
    main()

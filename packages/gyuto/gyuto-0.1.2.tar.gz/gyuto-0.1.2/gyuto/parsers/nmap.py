from collections import defaultdict, Counter
from datetime import datetime

from gyuto.core.results import PortResult, ServiceResult


def _get_hosts_list(tree):
    return [h for h in tree.xpath("/nmaprun/host")]


def get_hosts(tree):
    for host in tree.xpath("/nmaprun/host"):
        yield host


def get_host_addr(host):
    return host.xpath("address")[0].attrib.get("addr")


def get_host_addrs(tree):
    return [get_host_addr(h) for h in get_hosts(tree)]


def get_ports(host):
    open_ports = [(p.attrib.get("protocol"), p.attrib.get("portid")) for p in host.xpath("ports/port")]
    return open_ports


def get_host_results(tree):
    for host in tree.xpath("/nmaprun/host"):
        addr = get_host_addr(host)
        # get ports, cpes, cves, etc. etc.
        ports = get_ports(host)
        yield {
            "ip_address": addr,
            "ports": ports,
        }


def summary_by_host(tree):
    """yield HostSummary objects from a nmap xml tree"""

    #yield ("host", "open", "closed", "filtered", "unfiltered")
    for host in tree.xpath("/nmaprun/host"):
        addr = host.xpath("address")[0].attrib.get("addr")
        c = Counter(state.attrib.get("state") for state in host.xpath("ports/port/state"))
        extra = host.xpath("ports/extraports")[0]
        c[extra.attrib.get("state")] += int(extra.attrib.get("count"))
        yield PortResult(
                addr,
                c.get("open", 0),
                c.get("closed", 0),
                c.get("filtered", 0),
                c.get("unfiltered", 0)
            )


def results_by_host(tree):
    """yield HostResult objects from a nmap xml tree"""

    #yield ("host", "open", "closed", "filtered", "unfiltered")
    for host in tree.xpath("/nmaprun/host"):
        addr = host.xpath("address")[0].attrib.get("addr")
        portmap = defaultdict(list)
        for port in host.xpath("ports/port"):
            state = port.xpath("state")[0].attrib.get("state")
            protocol = port.attrib.get("protocol")
            portid = port.attrib.get("portid")
            portmap[state].append(protocol + "/" + portid)
        for extra in host.xpath("ports/extraports"):
            others = "{} others".format(extra.attrib.get("count"))
            portmap[extra.attrib.get("state")].append(others)
        yield PortResult(
                addr,
                "\n".join(portmap.get("open", "")),
                "\n".join(portmap.get("closed", "")),
                "\n".join(portmap.get("filtered", "")),
                "\n".join(portmap.get("unfiltered", "")),
            )


def get_scan_times(tree):
    start_time = datetime.fromtimestamp(float(tree.xpath("/nmaprun/@start")[0]))
    end_time = datetime.fromtimestamp(float(tree.xpath("/nmaprun/runstats/finished/@time")[0]))
    return (start_time, end_time)


def get_services_by_host(tree):
    query = "ports/port"
    for host in get_hosts(tree):
        addr = host.xpath("address")[0].attrib.get("addr")
        for port in host.xpath(query):
            if port.xpath("state")[0].attrib.get("state") != "open":
                continue
            name = port.xpath("service")[0].attrib.get("name")
            protocol = port.attrib.get("protocol")
            portid = port.attrib.get("portid")
            yield ServiceResult(addr, name, protocol, portid)


def hosts_with_open_port(tree, port):
    """yield hosts (ip address strings) with <port> open"""
    
    query = "ports/port[@portid='{p}']/state[@state='open']".format(p=port)
    for host in get_hosts(tree):
        for port in host.xpath(query):
            addr = host.xpath("address")[0].attrib.get("addr")
            yield addr


def get_cve_dict(tree):
    raise NotImplementedError("The nmap parser does not support CVE")

def map_hosts_by_mshotfix(tree, cve_min=0):
    raise NotImplementedError("The nmap parser does not support MS hotfix")

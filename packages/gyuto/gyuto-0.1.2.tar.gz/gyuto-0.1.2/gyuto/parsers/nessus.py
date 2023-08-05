from collections import defaultdict, Counter
from datetime import datetime

from gyuto.core.results import PortResult, ServiceResult, SoftwareResult, HostResult


# TODO: This might be useful for other tools, move to core?
CPE_JAVA = ["cpe:/a:sun:jre", "cpe:/a:oracle:jre"]
CPE_FLASH = ["cpe:/a:adobe:flash_player",]
CPE_ADOBE = ["cpe:/a:adobe:reader",]
CPE_CHROME = ["cpe:/a:google:chrome",]


def _get_hosts_gen(tree):
    for host in tree.xpath("Report/ReportHost"):
        yield host


def _get_hosts_list(tree):
    return [host for host in tree.xpath("Report/ReportHost")]


get_hosts = _get_hosts_gen


def get_addr(host):
    query = "HostProperties/tag[@name='host-ip']/text()"
    try:
        return host.xpath(query)[0]
    except IndexError:
        return host.attrib.get("name")


def get_host_addrs(tree):
    return [get_addr(h) for h in get_hosts(tree)]


def get_hostname(host):
    #query = "HostProperties/tag[@name='host-fqdn' or @name='netbios-name']/text()"
    query = "HostProperties/tag[@name='netbios-name']/text()"
    try:
        return host.xpath(query)[0]
    except IndexError:
        return "Unknown"


def get_fqdn(host):
    query = "HostProperties/tag[@name='host-fqdn']/text()"
    try:
        return [name for name in host.xpath(query)][0]
    except IndexError:
        return "Unknown"


def get_hostnames(tree):
    """Generate a list of hostnames for each host IP address"""

    query = "HostProperties/tag[@name='netbios-name' or @name='host-fqdn']/text()"
    for host in get_hosts(tree):
        addr = get_addr(host)
        names = ",".join([name for name in host.xpath(query)])
        yield (addr, names)

def get_os(host):
    query = "HostProperties/tag[@name='operating-system']/text()"
    try:
        return host.xpath(query)[0]
    except IndexError:
        return "Unknown"


def get_hostresult(host):
    """Create a HostResult object from a host node in the nessus xml"""
    
    return HostResult(
        address=get_addr(host),
        hostname=get_hostname(host),
        fqdn=get_fqdn(host),
        os=get_os(host),
        )


def get_ports(host):
    query = "ReportItem[@pluginFamily='Port scanners']"
    open_ports = [(p.attrib.get("protocol"), p.attrib.get("port")) for p in host.xpath(query)]
    return open_ports


def port_summary_by_host(tree):
    """Generate PortSummary objects from a nessus xml tree"""

    query = "ReportItem[@pluginFamily='Port scanners']"
    yield ("host", "open", "closed", "filtered", "unfiltered")
    for host in tree.xpath("/NessusClientData_v2/Report/ReportHost"):
        addr = host.attrib.get("name")
        c = Counter("open" for port in host.xpath(query))
        yield (
            addr,
            c.get("open", 0),
            c.get("closed", 0),
            c.get("filtered", 0),
            c.get("unfiltered", 0)
        )


def port_results_by_host(tree):
    """Generate PortResult objects from a nessus xml tree"""

    #yield ("host", "open", "closed", "filtered", "unfiltered")
    for host in tree.xpath("/NessusClientData_v2/Report/ReportHost"):
        addr = host.attrib.get("name")
        portmap = defaultdict(list)
        for item in host.xpath("ReportItem[@pluginFamily='Port scanners']"):
            state = "open"
            protocol = item.attrib.get("protocol")
            port = item.attrib.get("port")
            portmap[state].append(protocol + "/" + port)
        yield PortResult(
                addr,
                "\n".join(portmap.get("open", "")),
                "\n".join(portmap.get("closed", "")),
                "\n".join(portmap.get("filtered", "")),
                "\n".join(portmap.get("unfiltered", "")),
            )


def get_scan_times(tree):
    """Return datetimes for when scan began and ended"""

    f = "%a %b %d %H:%M:%S %Y"
    query = "Report/ReportHost/HostProperties/tag[@name='HOST_START']/text()"
    start_time = min([datetime.strptime(t, f) for t in tree.xpath(query)])
    query = "Report/ReportHost/HostProperties/tag[@name='HOST_END']/text()"
    end_time = max([datetime.strptime(t, f) for t in tree.xpath(query)])
    return (start_time, end_time)


def get_services_by_host(tree):
    """Yield ServiceResult objects from a nessus xml tree"""

    query = "ReportItem[@pluginFamily='Port scanners']"
    for host in get_hosts(tree):
        addr = get_addr(host)
        for service in host.xpath(query):
            name = service.attrib.get("svc_name")
            protocol = service.attrib.get("protocol")
            port = service.attrib.get("port")
            yield ServiceResult(addr, name, protocol, port)


def get_services_by_host_(tree):
    for result in get_services_by_host(tree):
        # aggregate results by host
        pass


def get_vulns_by_host(tree):
    for host in get_hosts(tree):
        addr = get_addr(host)
        for vuln in host.xpath("ReportItem"):
            vuln_id = vuln.attrib.get("pluginID")
            description = vuln.attrib.get("pluginName")
            cvss_score = vuln.xpath("cvss_base_score/text()[0]")
            cvss_vector = vuln.xpath("cvss_vector/text()[0]")
            if cvss_score == []: cvss_score = None
            if cvss_vector == []: cvss_vector = None
            yield (addr, vuln_id, description, cvss_score, cvss_vector)


def get_cve_hosts(tree):
    query = "ReportItem/cve/text()"
    for host in get_hosts(tree):
        name = host.attrib.get("name")
        for cve in host.xpath(query):
            yield (host, cve)


def get_hosts_by_cve(tree, cve):
    """Yield hosts that have a specific vulnerability"""

    query = "ReportItem/cve/text()"
    for host in get_hosts(tree):
        addr = get_addr(host)
        for cve2 in host.xpath(query):
            if cve == cve2: # need a better matching algorithm!
                yield addr
                break


def get_hosts_by_mshotfix(tree, hotfix):
    query = "Report/ReportHost/ReportItem/msft[text()='{}']/../.."
    for host in tree.xpath(query.format(hotfix.upper())):
        yield get_hostresult(host)


def get_hosts_from_query(tree, **kwargs):
    """Get hosts that match multiple criteria

    Work In Progress - what is the cleanest method?
    Perhaps chaining multiple functions that search/filter on a single
    criterion each?
    """

    query1 = "ReportItem/cpe[text()='{}']/../.."
    query2 = "?"
    cpe = kwargs.pop("cpe", None)
    cve = kwargs.pop("cve", None)
    cvssmin = kwargs.pop("cvssmin", 0)
    for host in get_hosts(tree):
        for item in hosts.xpath(query1.format(cpe)):
            if item.xpath(query2.format(cvssmin)):
                hosts.append(host)
                break


def map_hosts_by_port(tree):
    """Return a dict mapping TCP and UDP ports to lists of affected hosts

    Affected hosts are hosts with the specified port open
    """

    query = "ReportItem[@pluginFamily='Port scanners']"
    port_map = defaultdict(list)
    for host in get_hosts(tree):
        addr = get_addr(host)
        for service in host.xpath(query):
            name = service.attrib.get("svc_name")
            protocol = service.attrib.get("protocol")
            port = service.attrib.get("port")
            port_map[(protocol.lower(), int(port))].append(addr)
    return port_map


def map_hosts_by_mshotfix(tree, cvss_min=0):
    """Return a dict mapping MS hotfix strings to lists of affected hosts
    
    Affected hosts are hosts missing the described MS hotfix
    """

    query = "ReportItem/msft/text()"
    # could also use ReportItem/xref/text() and search for "MSFT:"
    # or could parse plugin #38153
    hotfix_map = defaultdict(list)
    for host in get_hosts(tree):
        #addr = get_addr(host)
        addr = host.attrib.get("name")
        for hotfix in host.xpath(query):
            hotfix_map[hotfix.lower()].append(addr)
    return hotfix_map


def get_cve_dict(tree):
    """Return a dict mapping CVE IDs to host IP addresses"""

    query = "ReportItem/cve/text()"
    cve_dict = defaultdict(list)
    for host in tree.xpath("Report/ReportHost"):
        name = host.attrib.get("name")
        for cve in host.xpath(query):
            cve_dict[cve].append(name)
    return cve_dict


def get_hosts_by_plugin(tree, plugin):
    query = "ReportItem[@pluginID='{}']".format(plugin)
    for host in get_hosts(tree):
        addr = host.attrib.get("name")
        if host.xpath(query):
            yield addr


def get_plugin(tree, pid):
    query = "ReportItem[@pluginID='{p}']/plugin_output/text()".format(p=pid)
    for host in get_hosts(tree):
        addr = host.attrib.get("name")
        for text in host.xpath(query):
            yield (addr, text)


def get_missing_ms_bulletins(tree):
    query = "ReportItem[@pluginID='38153']/plugin_output/text()"
    # can also look at ReportItem/msft/text() or ReportItem/xref/text() that
    # starts with "MSFT:"
    return


def get_software(tree):
    query = "ReportItem[@pluginID='45590']/plugin_output/text()"
    for host in get_hosts(tree):
        addr = get_addr(host)
        for text in host.xpath(query):
            # this plugin output is going to be a challenge to parse...
            # sometimes only an OS shows up, but it may also be possible for
            # only the apps to show up in the output?
            text = text.split("\n\n")
            for os in text[1].split("\n"):
                yield "os_result"
            for app in text[3].split("\n"):
                yield "app_result"


def get_flash_versions(tree):
    """Yield version(s) of Adobe Flash detected for each host"""

    #yield SoftwareResult._fields
    query = "ReportItem[@pluginID='28211']/plugin_output/text()"
    for host in get_hosts(tree):
        addr = host.attrib.get("name")
        for text in host.xpath(query):
            # parsing the plugin output is super hacky!
            for flash in text.split("\n  -")[1:]:
                flash = flash.split("\n")
                version = flash[1].split(",")[1].strip()
                path = flash[1].split(",")[0].strip()
                # this just tells us if it's ActiveX or a browser plugin
                #plugin_type = flash[0].split(":")[0].strip()
                yield SoftwareResult(addr, version, path)


def get_java_versions(tree):
    """Yield version(s) of Java detected for each host"""

    #yield SoftwareResult._fields
    #query2 = "ReportItem[@pluginID='33545'][1]/plugin_output/text()"
    query = "ReportItem[@pluginID='33545']/plugin_output/text()"
    for host in tree.xpath("Report/ReportHost"):
        addr = host.attrib.get("name")
        #text = host.xpath(query2)
        for text in host.xpath(query):
            for java in text.split("\n\n")[1:]:
                java = java.split("\n")
                version = java[1].split(" : ")[1].strip()
                path = java[0].split(" : ")[1].strip()
                yield SoftwareResult(addr, version, path)


def sort_software_result(result):
    return tuple(int(octet) for octet in result[0].split("."))


def get_java_versions_new(tree):

    query = "ReportItem[@pluginID='33545']/plugin_output/text()"
    results = []
    for host in tree.xpath("Report/ReportHost"):
        addr = host.attrib.get("name")
        for text in host.xpath(query):
            for java in text.split("\n\n")[1:]:
                java = java.split("\n")
                version = java[1].split(" : ")[1].strip()
                path = java[0].split(" : ")[1].strip()
                #yield SoftwareResult(addr, version, path)
                results.append(SoftwareResult(addr, version, path))
    return sorted(results, key=sort_software_result)

get_java_versions = get_java_versions_new


def get_flash_versions_new(tree):

    query = "ReportItem[@pluginID='28211']/plugin_output/text()"
    results = []
    for host in get_hosts(tree):
        addr = host.attrib.get("name")
        for text in host.xpath(query):
            # parsing the plugin output is super hacky!
            for flash in text.split("\n  -")[1:]:
                flash = flash.split("\n")
                version = flash[1].split(",")[1].strip()
                path = flash[1].split(",")[0].strip()
                # this just tells us if it's ActiveX or a browser plugin
                #plugin_type = flash[0].split(":")[0].strip()
                #yield SoftwareResult(addr, version, path)
                results.append(SoftwareResult(addr, version, path))
    return sorted(results, key=sort_software_result)

get_flash_versions = get_flash_versions_new


def get_firefox_versions(tree):

    query = "ReportItem[@pluginID='20862']/plugin_output/text()"
    for host in get_hosts(tree):
        addr = host.attrib.get("name")
        for text in host.xpath(query):
            for app in text.split("\n\n")[1:]:
                app = app.split("\n")
                name = app[0].split(" : ")[1].strip()
                version = app[2].split(" : ")[1].strip()
                path = app[1].split(" : ")[1].strip()
                if "Firefox" in name:
                    yield SoftwareResult(addr, version, path)


def get_air_versions(tree):
    # should this be combined with Flash?

    query = "ReportItem[@pluginID='32504']/plugin_output/text()"
    for host in get_hosts(tree):
        addr = host.attrib.get("name")
        for text in host.xpath(query):
            for app in text.split("\n\n"):
                app = app.strip().split("\n")
                version = app[0].split(" : ")[1].strip()
                path = app[1].split(" : ")[1].strip()
                yield SoftwareResult(addr, version, path)


def get_adobe_versions(tree):
    
    query = "ReportItem[@pluginID='20836']/plugin_output/text()"
    results = []
    for host in get_hosts(tree):
        addr = host.attrib.get("name")
        for text in host.xpath(query):
            for acrobat in text.split("\n\n")[1:]:
                acrobat = acrobat.split("\n")
                version = acrobat[1].split(" : ")[1].strip()
                path = acrobat[0].split(" : ")[1].strip()
                #yield SoftwareResult(addr, version, path)
                results.append(SoftwareResult(addr, version, path))
    return sorted(results, key=sort_software_result)


def get_antivirus(tree):
    
    query = "ReportItem[@pluginID='16193']/plugin_output/text()"
    for host in get_hosts(tree):
        addr = host.attrib.get("name")
        for text in host.xpath(query):
            #TODO does this plugin return output more than one AV product?
            sections = text.split("\n\n")
            product = sections[0].split()[0].strip()
            meta = sections[1].split("\n")
            path = meta[0].split(" : ")[1].strip()
            product_version = meta[1].split(" : ")[1].strip()
            engine_version = meta[2].split(" : ")[1].strip()
            signatures = meta[3].split(" : ")[1].strip()
            yield (addr, product, path, product_version, engine_version,
                    signatures)

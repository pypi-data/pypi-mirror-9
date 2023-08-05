from collections import defaultdict, Counter
from datetime import datetime

from gyuto.core.results import ServiceResult, SoftwareResult


def _get_hosts_list(tree):
    return [h for h in tree.xpath("nodes/node")]


def get_hosts(tree):
    # TODO: maybe parse out the IP address and other attributes here?
    for host in tree.xpath("nodes/node"):
        yield host


def get_host_addrs(tree):
    return [h.attrib.get("address") for h in get_hosts(tree)]


def get_scan_times(tree):
    f = "%Y%m%dT%H%M%S"
    query = "scans/scan/@startTime"
    # TODO: parse timestamp strings better
    start_time = min([datetime.strptime(t[:-3], f) for t in tree.xpath(query)])
    query = "scans/scan/@endTime"
    end_time = max([datetime.strptime(t[:-3], f) for t in tree.xpath(query)])
    return(start_time, end_time)


def get_services_by_host(tree):
    query = "endpoints/endpoint"
    for host in get_hosts(tree):
        addr = host.attrib.get("address")
        for endpoint in host.xpath(query):
            # TODO: we can extract a lot more data from nexpose about services
            # including multiple serivces on a single port/endpoint
            name = endpoint.xpath("services/service")[0].attrib.get("name")
            #name = None if name == [] else name[0] # cludgy, I miss Maybe
            protocol = endpoint.attrib.get("protocol")
            port = endpoint.attrib.get("port")
            yield ServiceResult(addr, name, protocol, port)


def map_hosts_by_port(tree):
    query = "endpoints/endpoint"
    port_map = defaultdict(set)
    for host in get_hosts(tree):
        addr = host.attrib.get("address")
        for endpoint in host.xpath(query):
            # TODO: we can extract a lot more data from nexpose about services
            # including multiple serivces on a single port/endpoint
            name = endpoint.xpath("services/service")[0].attrib.get("name")
            #name = None if name == [] else name[0] # cludgy, I miss Maybe
            protocol = endpoint.attrib.get("protocol")
            port = endpoint.attrib.get("port")
            port_map[(protocol.lower(), int(port))].add(addr)
    return port_map


def get_vulns_by_host_preload(tree):
    
    test_query = ".//tests/test[contains(@status,'vulnerable')]"
    
    # it's way faster to map the vuln ids up front, than to search each time
    vuln_dict = defaultdict(None)
    for vuln in tree.xpath("VulnerabilityDefinitions/vulnerability"):
        vid = vuln.attrib.get("id").lower()
        vuln_dict[vid] = vuln
    
    for host in get_hosts(tree):
        addr = host.attrib.get("address")
        for test in host.xpath(test_query):
            vuln_id = test.attrib.get("id").lower()
            vuln = vuln_dict.get(vuln_id)
            try:
                cvss_score = vuln.attrib.get("cvssScore")
                cvss_vector = vuln.attrib.get("cvssVector")
                description = vuln.attrib.get("title")
            except AttributeError:
                # a Maybe/Option typeclass would rock here...
                cvss_score = cvss_vector = description = None
            yield (addr, vuln_id, cvss_score, cvss_vector, description)


def get_vulns_by_host(tree):

    test_query = ".//tests/test[contains(@status,'vulnerable')]"
    vuln_query = "VulnerabilityDefinitions/vulnerability[@id='{}']"

    for host in get_hosts(tree):
        addr = host.attrib.get("address")
        for test in host.xpath(test_query):
            vuln_id = test.attrib.get("id")
            try:
                # this is slow...
                vuln = tree.xpath(vuln_query.format(vuln_id))[0]
            except IndexError:
                description = None
            else:
                description = vuln.attrib.get("title")
            yield (addr, vuln_id, description)


def get_hosts_by_vuln(tree):

    test_query = ".//tests/test[contains(@status,'vulnerable')]"
    vuln_map = defaultdict(list)
    for host in get_hosts(tree):
        addr = host.attrib.get("addr")
        for vuln in host.xpath(test_query):
            vuln_map[vuln.attrib.get("id")].append(addr)
    return vuln_map


def map_hosts_by_mshotfix(tree, cvss_min=0):

    vuln_query = "VulnerabilityDefinitions/vulnerability[@cvssScore>='{}']".format(cvss_min)
    # print(vuln_query)
    vuln_map = defaultdict(list)
    for vuln in tree.xpath(vuln_query):
        vid = vuln.attrib.get("id").lower()
        for hotfix in vuln.xpath("references/reference[@source='MS']/text()"):
            # so much case insensitivity!!!
            vuln_map[vid].append(hotfix.lower())

    test_query = ".//tests/test[contains(@status,'vulnerable')]"
    hotfix_map = defaultdict(set)
    for host in get_hosts(tree):
        addr = host.attrib.get("address")
        for test in host.xpath(test_query):
            for hotfix in vuln_map[test.attrib.get("id")]:
                vid = test.attrib.get("id")
                # does endpoint/service matter? maybe in the future
                #endpoint = test.xpath("ancestor::endpoint")[0]
                #protocol = endpoint.attrib.get("protocol")
                #port = endpoint.attrib.get("port")
                #service = test.xpath("ancestor::service")[0]
                # debugging
                #print("[*] Found {v} ({hf}) for {host}".format(v=vid,hf=hotfix,host=addr))
                hotfix_map[hotfix].add(addr)
    return hotfix_map


def get_hosts_by_cve(tree, cve):
    """Yield hosts that have a specific vulnerability"""

    match_vuln_ids = set()
    for vuln in tree.xpath("VulnerabilityDefinitions/vulnerability"):
        vid = vuln.attrib.get("id")
        for cve2 in vuln.xpath("references/reference[@source='CVE']/text()"):
            if cve == cve2: # need a better match algorithm!
                match_vuln_ids.add(vid)

    for host in get_hosts(tree):
        addr = host.attrib.get("address")
        for test in host.xpath("tests/test"):
            if test.attrib.get("id") in match_vuln_ids:
                yield addr
                break # break out of inside forloop and resume outside forloop?


def get_cve_dict(tree):
    """Return a dict mapping CVE IDs to host IP addresses"""

    vuln_dict = defaultdict(list)
    for vuln in tree.xpath("VulnerabilityDefinitions/vulnerability"):
        vid = vuln.attrib.get("id")
        for cve in vuln.xpath("references/reference[@source='CVE']/text()"):
            vuln_dict[vid].append(cve)
    cve_dict = defaultdict(list)
    for host in tree.xpath("nodes/node"):
        name = host.attrib.get("address")
        for test in host.xpath("tests/test[contains(@status,'vulnerable')]"):
            for cve in vuln_dict[test.attrib.get("id")]:
                cve_dict[cve].append(name)
    return cve_dict


def get_software(tree):
    """Yield all software detected on each host
    
    Attempt at a generalization of get_java, et al
    """
    
    for host in get_hosts(tree):
        addr = host.attrib.get("address")
        for s in host.xpath("software/fingerprint"):
            vendor = s.attrib.get("vendor")
            product = s.attrib.get("product")
            version = s.attrib.get("version")
            path = "" # nexpose doesn't capture the install path
            # TODO add more fields to SoftwareResult?
            yield (addr, vendor, product, version, path)


def get_flash_versions(tree):
    
    def check(s):
        return s.attrib.get("vendor") == "Adobe" and s.attrib.get("family") == "Flash"

    #yield SoftwareResult._fields
    for host in get_hosts(tree):
        addr = host.attrib.get("address")
        for s in host.xpath("software/fingerprint"):
            if check(s):
                version = s.attrib.get("version")
                yield SoftwareResult(addr, version, "")


def get_java_versions(tree):
    """Yield version(s) of Java detected for each host
    
    Return type should be (addr, version, path) tuple of strings
    Future versions will probably return a more formal SoftwareResult object
    Right now we check for two distinct indicators (see check1 and check2)
    """

    def check1(s):
        return s.attrib.get("vendor") == "Oracle" and "Java" in s.attrib.get("product")
    
    def check2(s):
        return s.attrib.get("family") == "Java"
    
    def check(s):
        return check1(s) or check2(s)

    for host in tree.xpath("nodes/node"):
        addr = host.attrib.get("address")
        for s in host.xpath("software/fingerprint"):
            #print(s.attrib.get("product"))
            if check(s):
                #version = " ".join([s.attrib["product"], s.attrib["version"]])
                version = s.attrib.get("version")
                # nexpose doesn't record the install path :-(
                yield SoftwareResult(addr, version, "")


def get_firefox_versions(tree):
    
    def check(s):
        return s.attrib.get("vendor") == "Mozilla" and s.attrib.get("product") == "Firefox"

    for host in get_hosts(tree):
        addr = host.attrib.get("address")
        for s in host.xpath("software/fingerprint"):
            if check(s):
                version = s.attrib.get("version")
                yield SoftwareResult(addr, version, "")

# for schema info see the following
# https://qualysguard.qualys.com/qwebhelp/fo_help/reports/report_dtd.htm

from collections import defaultdict, Counter

from gyuto.core.results import ServiceResult, SoftwareResult


def get_hosts(tree):
    # TODO: maybe parse out the IP address and other attributes here?
    for host in tree.xpath("/SCAN/IP"):
        yield host


def _get_services_by_host(tree):
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


def _get_vulns_by_host_preload(tree):
    
    test_query = ".//tests/test[contains(@status,'vulnerable')]"
    
    # it's way faster to map the vuln ids up front, than to search each time
    vuln_dict = defaultdict(None)
    for vuln in tree.xpath("VulnerabilityDefinitions/vulnerability"):
        vid = vuln.attrib.get("id")
        vuln_dict[vid] = vuln
    
    for host in get_hosts(tree):
        addr = host.attrib.get("address")
        for test in host.xpath(test_query):
            vuln_id = test.attrib.get("id")
            vuln = vuln_dict.get(vuln_id)
            try:
                cvss_score = vuln.attrib.get("cvssScore")
                cvss_vector = vuln.attrib.get("cvssVector")
                description = vuln.attrib.get("title")
            except AttributeError:
                # a Maybe/Option typeclass would rock here...
                cvss_score = cvss_vector = description = None
            yield (addr, vuln_id, cvss_score, cvss_vector, description)


def _get_vulns_by_host(tree):

    test_query = "tests/test[contains(@status,'vulnerable')]"
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
    pass


def get_hosts_by_cve(tree, cve):
    """Yield hosts that have a specific vulnerability"""

    for host in get_hosts(tree):
        addr = host.attrib.get("value")
        for vuln in host.xpath("VULNS/CAT/VULN"):
            if vuln.attrib.get("cveid") in match_vuln_ids:
                yield addr
                break # break out of inside forloop and resume outside forloop?


def get_cve_dict(tree):
    """Return a dict mapping CVE IDs to host IP addresses"""

    cve_dict = defaultdict(list)
    for host in get_hosts(tree):
        addr = host.attrib.get("value")
        for vuln in host.xpath("VULNS/CAT/VULN"):
            for cve in vuln.xpath("CVE_ID_LIST/CVE_ID/ID"):
                cve_dict[cve.text].append(addr)
    return cve_dict


def _get_software(tree):
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


def _get_flash_versions(tree):
    
    def check(s):
        return s.attrib.get("vendor") == "Adobe" and s.attrib.get("family") == "Flash"

    #yield SoftwareResult._fields
    for host in get_hosts(tree):
        addr = host.attrib.get("address")
        for s in host.xpath("software/fingerprint"):
            if check(s):
                version = s.attrib.get("version")
                yield SoftwareResult(addr, version, "")


def _get_java_versions(tree):
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

    #yield SoftwareResult._fields
    for host in tree.xpath("nodes/node"):
        addr = host.attrib.get("address")
        for s in host.xpath("software/fingerprint"):
            #print(s.attrib.get("product"))
            if check(s):
                #version = " ".join([s.attrib["product"], s.attrib["version"]])
                version = s.attrib.get("version")
                # nexpose doesn't record the install path :-(
                yield SoftwareResult(addr, version, "")


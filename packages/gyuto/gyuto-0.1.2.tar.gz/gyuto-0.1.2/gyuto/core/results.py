from collections import namedtuple


HostResult = namedtuple(
    "HostResult",
    "address hostname fqdn os",)


PortResult = namedtuple(
    "PortResult",
    "host open closed filtered unfiltered",)


ServiceResult = namedtuple(
    "ServiceResult",
    "host name protocol port")


VulnResult = namedtuple(
    "VulnResult",
    "host vuln_id description cvss_score cvss_vector",)


SoftwareResult = namedtuple(
    "SoftwareResult",
    "host version path",)


# TODO: should this be combined with VulnResult?
CVEResult = namedtuple(
    "CVEResult",
    "host cve",)

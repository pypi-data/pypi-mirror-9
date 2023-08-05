#import netaddr


class Scan(object):

    def __init__(self):
        self.start = None
        self.end = None
        self.scanned_ip_count = 0
        self.host_count = 0
        self.port_count = 0
        self.vuln_count = 0


class Host(object):

    def __init__(self, address, **kwargs):
        self.hostname = kwargs.pop("hostname", "Unknown")
        self.fqdn = kwargs.pop("fqdn", "Unknown")
        self.os = kwargs.pop("os", "Unknown")

    def __repr__(self):
        return str(self.address)

import requests
from lxml import html

NVD = "http://web.nvd.nist.gov/view/vuln/detail?vulnId={cve_id}"
CVEDETAILS = "http://cvedetails.com/cve-details.php?t=1&cve_id={cve_id}"
# Alternate URL
# CVEDETAILS = "http://cvedetails.com/cve/{cve_id}/"
MSBDETAILS = "http://cvedetails.com/microsoft-bulletin/{msb_id}/"
MSTN = "https://technet.microsoft.com/library/security/{msb_id}"
CISCO = "http://tools.cisco.com/security/center/swCheckerShowResults.x?versionNamesSelected={ios_version}"


def get_nvd(cve_id):
    cve = {"id": cve_id}
    response = requests.get(NVD.format(cve_id=cve_id))
    # TODO: Validate the request was successful somehow
    body = html.fromstring(response.text)
    cve["summary"] = None
    cve["score"] = None
    return cve


def get_cvedetails(cve_id):
    cve = {
        "id": cve_id,
        "url": CVEDETAILS.format(cve_id=cve_id),
    }
    response = requests.get(CVEDETAILS.format(cve_id=cve_id))
    # TODO: Validate the request was successful somehow
    body = html.fromstring(response.text)
    cve["summary"] = body.xpath(".//div[@class='cvedetailssummary']/text()")[0].strip()
    datenote = body.xpath(".//span[@class='datenote']/text()")[0].split(":")
    cve["date_published"] = datenote[1].split()[0].strip()
    cve["date_updated"] = datenote[2].split()[-1].strip()
    cve["score"] = body.xpath(".//div[@class='cvssbox']/text()")[0].strip()
    cve["types"] = body.xpath(".//span[contains(@class, 'vt_')]/text()")
    cve["references"] = body.xpath(".//table[@id='vulnrefstable']/tr/td/a/@href")
    return cve


def get_msbdetails(msb_id):
    """
    Get MS security bulletin data from cvedetails.com

    Note: does not contain data for bulletins before 2009!
    """

    msb = {"id": msb_id}
    response = requests.get(MSBDETAILS.format(msb_id=msb_id))
    # TODO: Validate the request was successful somehow
    body = html.fromstring(response.text)
    msb["summary"] = body.xpath(".//div[@class='cvedetailssummary']/text()")[0].strip()
    return msb


def get_mstn(msb_id):
    """Get MS security bulletin data from Microsoft TechNet"""

    # raise NotImplementedError("This function hasn't been written yet!")
    msb = {
        "id": msb_id,
        "url": MSTN.format(msb_id=msb_id),
    }
    response = requests.get(MSTN.format(msb_id=msb_id))
    # TODO: Validate the request was successful somehow
    body = html.fromstring(response.text)
    msb["title"] = body.xpath(".//div[@id='mainBody']/h2[@class='subheading']/text()")[0].strip()
    msb["date_published"] = body.xpath(".//div[@id='pubInfo']/p/text()")[0].split(":")[1].strip()
    return msb


def get_cisco_ios(ios_version):
    response = requests.get(CISCO.format(ios_version="12.2(44)SE1"))
    body = html.fromstring(response.text)
    advisories = body.xpath(".//div[@id='vulnerableAdvisoriesContent_0']")[0]
    print(advisories)

# TODO: get Cisco advisory ID ex. "cisco-sa-20110928-nat"
# URL =
# http://www.cisco.com/c/en/us/support/docs/csa/cisco-sa-20110928-nat.html


# TODO: get CWE


if __name__ == "__main__":
    cve = get_cvedetails("2013-4854")
    print(cve.get("summary"))

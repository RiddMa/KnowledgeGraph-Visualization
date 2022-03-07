class Vulnerability:
    def __init__(self, cve_id, vuln_desc, publish_date, last_update_date, cvss_score, cvss_severity, vuln_types,
                 access_complexity, authentication, availability_impact, confidentiality_impact, gained_access,
                 integrity_impact, references):
        self.cve_id = cve_id
        self.vuln_desc = vuln_desc
        self.publish_date = publish_date
        self.last_update_date = last_update_date
        self.cvss_score = cvss_score
        self.cvss_severity = cvss_severity
        self.vuln_types = vuln_types
        self.access_complexity = access_complexity
        self.authentication = authentication
        self.availability_impact = availability_impact
        self.confidentiality_impact = confidentiality_impact
        self.gained_access = gained_access
        self.integrity_impact = integrity_impact
        self.references = references


class Asset:
    pass


class ASoftware(Asset):
    def __init__(self, name):
        self.type = "software"
        self.name = name


class AOS(Asset):
    def __init__(self, name):
        self.type = "os"
        self.name = name


class Attack:
    def __init__(self, name, cwe_id):
        self.name = name
        self.cwe_id = cwe_id


class VulnEntity:
    def __init__(self, vuln, assets, attack):
        self.vuln = vuln
        self.assets = assets
        self.attack = attack

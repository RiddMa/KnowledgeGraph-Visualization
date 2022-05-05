import collections
import json
from enum import auto, unique, Enum

from py2neo import Node, Relationship, NodeMatcher

from db import neo


@unique
class ApiVersion(Enum):
    NVDv1 = 'nvd_v1'
    CVEv1 = 'cve_v1'


# cpe:<cpe_version>:<part>:<vendor>:<product>:<version>:<update>:<edition>:<language>:<sw_edition>:<target_sw>:<target_hw>:<other>
def split_properties(cve_item, api_ver: ApiVersion):
    if api_ver is ApiVersion.NVDv1:
        # vuln_props = cve_item['vuln']
        # vuln_props['timestamp'] = cve_item['timestamp']
        # vuln_props['api_ver'] = api_ver
        vuln_props = {
            'timestamp': cve_item['timestamp'],
            'api_ver': api_ver.value,
            'cve_id': cve_item['vuln']['cve_id'],
            'props': json.dumps(cve_item)
        }

        asset_props = cve_item['assets']
        # asset_props['timestamp'] = cve_item['timestamp']
        # asset_props['api_ver'] = api_ver

        exploit_props = cve_item['exploit'] or {}
        exploit_props['timestamp'] = cve_item['timestamp']
        exploit_props['api_ver'] = api_ver

        return {
            "vuln_props": vuln_props,
            "exploit_props": exploit_props,
            "asset_props": asset_props
        }

    elif api_ver is ApiVersion.CVEv1:
        vuln_props = {
            "cve_id": cve_item["cve_id"],
            "vuln_desc": cve_item["vuln_desc"],
            "publish_date": cve_item["publish_date"],
            "last_update_date": cve_item["last_update_date"],
            "cvss_score": cve_item["cvss_score"],
            "cvss_severity": cve_item["cvss_severity"],
            "access_complexity": cve_item["access_complexity"]["text"],
            "authentication": cve_item["authentication"]["text"],
            "availability_impact": cve_item["availability_impact"]["text"],
            "confidentiality_impact": cve_item["confidentiality_impact"]["text"],
            "gained_access": cve_item["gained_access"],
            "integrity_impact": cve_item["integrity_impact"]["text"],
            "cwe_id": cve_item["cwe_id"],
            # "references": cve_item["references"]
        }

        attack_props = {"vulnerability_types": cve_item["vulnerability_types"]}

        asset_props = []
        for a in cve_item["affected_products"]:
            asset_props.append({
                "type": a["type"],
                "vendor": a["vendor"],
                "name": a["name"],
                "version": a["version"]
            })

        return {
            "vuln_props": vuln_props,
            "attack_props": attack_props,
            "asset_props": asset_props
        }


class Vulnerability:

    def __init__(self, props):
        self.props = props
        self.node = self.get_node() or self.add_node()

    def get_node(self):
        node = NodeMatcher(neo.graph).match(
            "Vulnerability", cve_id=self.props['cve_id']).first()
        return node

    def add_node(self):
        labels = ["Vulnerability"]
        return neo.add_node(labels, self.props)


class Asset:
    """
    self.props has cpe23uri, field{}, reference[], title
    """

    def __init__(self, props):
        self.props = props
        self.node = self.get_node() or self.add_node()

    def get_node(self):  # it's bad!
        node = NodeMatcher(neo.graph).match(
            "Asset",
            cpe23uri=self.props['cpe23uri']).first()
        return node

    def add_node(self):
        labels = ["Asset", self.props["type"]]
        return neo.add_node(labels, self.props)


class Exploit:
    """
    self.props has edb_id, title, author, type, platform, date, code, cve_ids[]
    """

    def __init__(self, props):
        self.props = props
        self.node = self.get_node() or self.add_node()

    def get_node(self):
        node = NodeMatcher(neo.graph).match(
            "Exploit",
            edb_id=self.props['edb_id']).first()
        return node

    def add_node(self):
        labels = ["Exploit"]
        return neo.add_node(labels, self.props)

    def match_cves(self):
        nodes = NodeMatcher(neo.graph).match("Vulnerability").where(f"cve_id in {self.props['cve_ids']}")


class VulnEntity:

    def __init__(self, vuln, attack, assets):
        self.vuln = vuln
        self.assets = assets
        self.attack = attack

    def add_relationship(self):
        tx = neo.graph.begin()
        for a in self.assets:
            tx.create(Relationship(a.node, "HAS", self.vuln.node))
        tx.create(Relationship(self.vuln.node, "CAUSE", self.attack.node))
        tx.commit()

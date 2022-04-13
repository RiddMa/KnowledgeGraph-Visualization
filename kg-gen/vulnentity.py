import collections

from py2neo import Node, Relationship, NodeMatcher

from utils.db import neo, find_dict_one


def split_properties(cve_item):
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
            "Vulnerability", cve_id=self.props["cve_id"]).first()
        return node

    def add_node(self):
        labels = ["Vulnerability"]
        return neo.add_node(labels, self.props)


class Asset:
    """
    self.props has a["type"], a["vendor"], a["name"], a["version"]
    """

    def __init__(self, props):
        self.props = props
        self.node = self.get_node() or self.add_node()

    def get_node(self):  # it's bad!
        node = NodeMatcher(neo.graph).match(
            "Asset",
            type=self.props["type"],
            vendor=self.props["vendor"],
            name=self.props["name"],
            version=self.props["version"]).first()
        return node

    def add_node(self):
        labels = ["Asset", self.props["type"]]
        return neo.add_node(labels, self.props)


# class ASoftware(Asset):
#     def __init__(self, name):
#         self.type = "software"
#         self.name = name
#
#
# class AOS(Asset):
#     def __init__(self, name):
#         self.type = "os"
#         self.name = name


class Attack:
    """
    self.props has a["type"], a["vendor"], a["name"], a["version"]
    """

    def __init__(self, props):
        self.props = props
        self.node = self.get_node() or self.add_node()

    def get_node(self):
        node = NodeMatcher(neo.graph).match(
            "Attack",
            vulnerability_types=self.props["vulnerability_types"]).first()
        return node

    def add_node(self):
        labels = ["Attack"]
        return neo.add_node(labels, self.props)


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

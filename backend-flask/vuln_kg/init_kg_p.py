import json
import ray
import re
from datetime import datetime
from db import MyNeo, mg
from logger_factory import mylogger_p, log_vul_cnt, rel_vul_str, ray_timer_str, rel_exploit_str, log_exploit_cnt
# limit = 100000
from vuln_kg.util import str_percent


@ray.remote
def init_vuln_ray(skip, _limit):
	from db import MyMongo
	from datetime import datetime
	from logger_factory import mylogger
	from vuln_kg.vulnentity import ApiVersion, split_properties, add_vul

	start = datetime.now()
	mylogger_p('timer').info(f'Start init_vuln.skip({skip}) with limit {_limit}')

	_mg = MyMongo()
	cursor = _mg.get_nvd()
	neo = MyNeo()
	cnt = 0
	for doc in cursor.skip(skip).limit(_limit):
		doc = doc['content']
		mylogger_p('init_kg').debug(doc)
		try:
			doc = split_properties(doc, api_ver=ApiVersion.NVDv1)['vuln_props']
			# vuln = Vulnerability(props["vuln_props"])
			add_vul(neo, doc)
			cnt += 1
		except BaseException as e:
			mylogger('init_kg').error(e, exc_info=True)
		if cnt % 50 == 0:
			mylogger_p('init_kg').info(f'Processed {cnt} vulnerabilities')

	_mg.client.close()
	mylogger_p('timer').info(ray_timer_str('init_vuln_ray()', skip, _limit, start))
	return 0


@ray.remote
def init_asset_ray(skip, _limit):
	from db import MyMongo
	from datetime import datetime
	from logger_factory import mylogger_p
	from vuln_kg.vulnentity import add_asset

	start = datetime.now()
	mylogger_p('timer').info(f'Start init_asset.skip({skip}) with limit {_limit}')

	_mg = MyMongo()
	cursor = _mg.get_cpe()
	neo = MyNeo()
	cnt = 0
	for doc in cursor.skip(skip).limit(_limit):
		mylogger_p('init_kg').debug(doc)
		try:
			add_asset(neo, doc)
			# asset = Asset(doc)
			cnt += 1
		except BaseException as e:
			mylogger_p('error').error(e, exc_info=True)
		finally:
			pass
		if cnt % 50 == 0:
			mylogger_p('init_kg').info(f'Processed {cnt} assets')

	_mg.client.close()
	mylogger_p('timer').info(f'init_asset_ray().skip({skip}) with limit {_limit} runtime = {datetime.now() - start}')
	return 0


@ray.remote
def init_asset_family_ray(skip, _limit):
	"""
	Create an asset family node for assets of same <part>:<vendor>:<product>
	# cpe:<cpe_version>:<part>:<vendor>:<product>:<version>:<update>:<edition>:<language>:<sw_edition>:<target_sw>:<target_hw>:<other>

	:param skip:
	:param _limit:
	:return:
	"""
	from py2neo import NodeMatcher
	from db import MyNeo
	start = datetime.now()
	_neo = MyNeo()
	cursor = NodeMatcher(_neo.graph).match("Asset").skip(skip).limit(_limit)
	family_cnt, asset_cnt = 0, 0
	for asset_node in cursor:
		try:
			family_cnt += _neo.add_asset_family_node(asset_node['cpe23uri'])
		except BaseException as e:
			mylogger_p('error').error(e, exc_info=True)
		finally:
			asset_cnt += 1
		if asset_cnt % 50 == 0:
			mylogger_p('init_kg').info(f'Processed {asset_cnt} assets')
			mylogger_p('init_kg').info(f'Created {family_cnt} families')
	mylogger_p('timer').info(
		f'init_asset_family_ray().skip({skip}) with limit {_limit} runtime = {datetime.now() - start}')
	return 0


@ray.remote
def fix_asset_family_ray(skip, _limit):
	"""
	Create an asset family node for assets of same <part>:<vendor>:<product>
	# cpe:<cpe_version>:<part>:<vendor>:<product>:<version>:<update>:<edition>:<language>:<sw_edition>:<target_sw>:<target_hw>:<other>

	:param skip:
	:param _limit:
	:return:
	"""
	from py2neo import NodeMatcher
	from db import MyNeo
	start = datetime.now()
	_neo = MyNeo()
	cursor = NodeMatcher(_neo.graph).match("Asset").skip(skip).limit(_limit)
	family_cnt, asset_cnt = 0, 0
	for asset_node in cursor:
		try:
			family_cnt += _neo.fix_asset_family_label(asset_node['cpe23uri'])
		except BaseException as e:
			mylogger_p('error').error(e, exc_info=True)
		finally:
			asset_cnt += 1
		if asset_cnt % 50 == 0:
			mylogger_p('init_kg').info(f'Processed {asset_cnt} assets')
			mylogger_p('init_kg').info(f'Created {family_cnt} families')
	mylogger_p('timer').info(
		f'fix_asset_family_ray().skip({skip}) with limit {_limit} runtime = {datetime.now() - start}')
	return 0


@ray.remote
def init_exploit_ray(skip, _limit):
	from db import MyMongo
	from datetime import datetime
	from logger_factory import mylogger
	from vuln_kg.vulnentity import add_exploit

	start = datetime.now()
	mylogger_p('timer').info(f'Start init_exploit.skip({skip}) with limit {_limit}')

	_mg = MyMongo()
	cursor = _mg.get_edb()
	neo = MyNeo()
	cnt = 0
	for doc in cursor.skip(skip).limit(_limit):
		doc = doc['content']
		mylogger_p('init_kg').debug(doc)
		try:
			add_exploit(neo, doc)
			# exploit = Exploit(doc)
			cnt += 1
		except BaseException as e:
			mylogger('init_kg').error(e, exc_info=True)
		if cnt % 50 == 0:
			mylogger_p('init_kg').info(f'Processed {cnt} exploits')

	_mg.client.close()
	mylogger_p('timer').info(f'init_exploit_ray().skip({skip}) with limit {_limit} runtime = {datetime.now() - start}')
	return 0


@ray.remote
def create_rel_va_ray(skip, _limit):
	"""
	Create Asset-HAS->Vuln and Vuln-AFFECTS->Asset relationship.
	'va' means vul-asset

	:return:
	"""
	from py2neo import NodeMatcher
	from db import MyNeo
	start = datetime.now()
	neo = MyNeo()
	cursor = NodeMatcher(neo.graph).match("Vulnerability").skip(skip).limit(_limit)
	vul_cnt = 0
	for vuln_node in cursor:
		rel_cnt = 0
		props = json.loads(vuln_node['props'])
		for op_dict in props['assets']:
			try:
				if op_dict['operator'] == 'OR':
					for match in op_dict['cpe_match']:
						if match['vulnerable']:
							pattern = re.sub(r'\*+', '.*', match['cpe23Uri'])
							assets = neo.match_asset(pattern)
							for asset in assets:
								rel_cnt += neo.add_rel_cql_va(cve_id=vuln_node['cve_id'], cpe23uri=asset['cpe23uri'])
			except BaseException as e:
				mylogger_p('init_kg').error(e, exc_info=True)
			finally:
				pass
		vul_cnt += 1
		mylogger_p('init_kg').info(rel_vul_str(rel_cnt, vuln_node["cve_id"]))
		if vul_cnt % 50 == 0:
			mylogger_p('init_kg').info(log_vul_cnt(skip, _limit, vul_cnt))
	neo.close_db()
	mylogger_p('timer').info(f'create_rel_va_ray().skip({skip}) with limit {_limit} runtime = {datetime.now() - start}')
	return 0


@ray.remote
def create_rel_vaf_ray(skip, _limit):
	"""
	Create Asset:Family-HAS->Vuln and Vuln-AFFECTS->Asset:Family relationship.
	'vaf' means vul-asset:family

	:return:
	"""
	from py2neo import NodeMatcher
	from db import MyNeo
	start = datetime.now()
	neo = MyNeo()
	if skip or _limit:
		mylogger_p('timer').info(f'create_rel_vaf_ray().skip({skip}) with limit {_limit} start')
		cursor = NodeMatcher(neo.graph).match("Vulnerability").skip(skip).limit(_limit)
	else:
		mylogger_p('timer').info(f'create_rel_vaf_ray() start')
		cursor = NodeMatcher(neo.graph).match("Vulnerability")
	vul_cnt = 0
	for vuln_node in cursor:
		rel_cnt = 0
		props = json.loads(vuln_node['props'])
		for op_dict in props['assets']:
			try:
				if op_dict['operator'] == 'OR':
					for match in op_dict['cpe_match']:
						if match['vulnerable']:
							rel_cnt += neo.add_rel_cql_vaf(cve_id=vuln_node['cve_id'], cpe23uri=match['cpe23Uri'])
			except BaseException as e:
				mylogger_p('init_kg').error(e, exc_info=True)
			finally:
				pass
		neo.add_rel_cql_vaf_cnt(cve_id=vuln_node['cve_id'])
		vul_cnt += 1
		mylogger_p('init_kg').info(rel_vul_str(rel_cnt, vuln_node["cve_id"]))
		if vul_cnt % 50 == 0:
			mylogger_p('init_kg').info(log_vul_cnt(skip, _limit, vul_cnt))
	neo.close_db()
	mylogger_p('timer').info(ray_timer_str('create_rel_vaf_ray()', skip, _limit, start))
	return 0


@ray.remote
def create_rel_afa_ray(skip, _limit):
	"""
	Ensure Asset:Family-ParentOf->Asset and Asset-ChildOf->Asset:Family relationship.
	'afa' means asset:family-asset

	:return:
	"""
	from py2neo import NodeMatcher
	from db import MyNeo
	start = datetime.now()
	neo = MyNeo()
	if skip or _limit:
		mylogger_p('timer').info(f'create_rel_afa_ray().skip({skip}) with limit {_limit} start')
		cursor = NodeMatcher(neo.graph).match("Vulnerability").skip(skip).limit(_limit)
	else:
		mylogger_p('timer').info(f'create_rel_afa_ray() start')
		cursor = NodeMatcher(neo.graph).match("Vulnerability")
	vul_cnt = 0
	for vuln_node in cursor:
		rel_cnt = 0
		props = json.loads(vuln_node['props'])
		for op_dict in props['assets']:
			try:
				if op_dict['operator'] == 'OR':
					for match in op_dict['cpe_match']:
						if match['vulnerable']:
							rel_cnt += neo.add_rel_cql_afa(asset_uri=match['cpe23Uri'])
			except BaseException as e:
				mylogger_p('init_kg').error(e, exc_info=True)
			finally:
				pass
		vul_cnt += 1
		mylogger_p('init_kg').info(rel_vul_str(rel_cnt, vuln_node["cve_id"]))
		if vul_cnt % 50 == 0:
			mylogger_p('init_kg').info(log_vul_cnt(skip, _limit, vul_cnt))
	neo.close_db()
	mylogger_p('timer').info(ray_timer_str('create_rel_afa_ray()', skip, _limit, start))
	return 0


# def create_rel_va():
#     from py2neo import NodeMatcher
#     from db import MyNeo
#     start = datetime.now()
#     neo = MyNeo()
#     cursor = NodeMatcher(neo.graph).match("Vulnerability").limit(limit)
#     # cursor = NodeMatcher(neo.graph).match("Vulnerability")
#     for vuln_node in cursor:
#         cnt = 0
#         props = json.loads(vuln_node['props'])
#         for op_dict in props['assets']:
#             if op_dict['operator'] == 'OR':
#                 for match in op_dict['cpe_match']:
#                     if match['vulnerable']:
#                         # asset_node = neo.get_node('Asset', cpe23uri=match['cpe23Uri']).first()
#                         pattern = re.sub(r'\*+', '.*', match['cpe23Uri'])
#                         # asset_node = neo.get_node('Asset').where(f"_.cpe23uri =~ {pattern}")
#                         # asset_node = neo.match_asset(pattern)
#                         # if asset_node is not None:
#                         #     cnt += neo.add_relationship_cql(start=asset_node, type_='Has', end=vuln_node)
#                         #     cnt += neo.add_relationship_cql(start=vuln_node, type_='Affects', end=asset_node)
#                         assets = neo.match_asset(pattern)
#                         for asset in assets:
#                             cnt += neo.add_rel_cql_va(cve_id=vuln_node['cve_id'], cpe23uri=asset['cpe23uri'])
#         mylogger_p('init_kg').info(f'Created {cnt} relationships for {vuln_node["cve_id"]}')
#     neo.close_db()
#     mylogger_p('timer').info(f'create_rel_va runtime = {datetime.now() - start}')
#     return 0


@ray.remote
def create_rel_evaf_ray(skip, _limit):
	"""
	Create Exploit-Exploits->Vuln and Vuln-Exploited_by->Exploit, then deduct Exploit-Against->Asset and Asset-Exploited_by->Exploit
	'evaf' means exploit-vul-asset:family

	:return:
	"""

	from db import MyNeo
	from py2neo import NodeMatcher, RelationshipMatcher
	start = datetime.now()
	mylogger_p('timer').info('Start create_rel_evaf_ray()')

	neo = MyNeo()
	if skip or _limit:  # skip may be 0!!!
		mylogger_p('timer').info(f'create_rel_evaf_ray().skip({skip}) with limit {_limit} start')
		cursor = NodeMatcher(neo.graph).match("Exploit").skip(skip).limit(_limit)
	else:
		mylogger_p('timer').info(f'create_rel_evaf_ray() start')
		cursor = NodeMatcher(neo.graph).match("Exploit")
	e_cnt = 0
	for exploit_node in cursor:
		cve_ids = exploit_node['cve_ids']
		r_cnt = 0
		for cve_id_no in cve_ids:
			cve_id = f'CVE-{cve_id_no}'
			vuln_node = neo.get_node('Vulnerability', cve_id=cve_id).first()
			if vuln_node is not None:
				r_cnt += neo.add_rel_cql_ev(edb_id=exploit_node['edb_id'], cve_id=cve_id)
				cpe_list = neo.get_rel_cql_vaf(cve_id=cve_id)
				for rel in cpe_list:
					# for cpe23uri in rel['assets']:
					r_cnt += neo.add_rel_cql_eaf(edb_id=exploit_node['edb_id'], cpe23uri=rel['target'],
					                             assets=rel['assets'], asset_cnt=rel['cnt'])
		mylogger_p('init_kg').info(rel_exploit_str(rel_cnt=r_cnt, edb_id=exploit_node['edb_id']))
		e_cnt += 1
		if e_cnt % 50 == 0:
			mylogger_p('init_kg').info(log_exploit_cnt(skip=skip, _limit=_limit, e_cnt=e_cnt))

	neo.close_db()
	mylogger_p('timer').info(ray_timer_str('create_rel_evaf_ray()', skip, _limit, start))
	return 0


# def create_rel_eva():
#     """
#     Create Exploit-Exploits->Vuln and Vuln-Exploited_by->Exploit,
#     then Deduct Exploit-Against->Asset and Asset-Exploited_by->Exploit
#
#     :return:
#     """
#
#     from db import MyNeo
#     from py2neo import NodeMatcher, RelationshipMatcher
#     start = datetime.now()
#     mylogger_p('timer').info('Start create_rel_ve')
#
#     neo = MyNeo()
#     cursor = NodeMatcher(neo.graph).match("Exploit").limit(limit)
#     rel_matcher = RelationshipMatcher(neo.graph)
#     for exploit_node in cursor:
#         cve_ids = exploit_node['cve_ids']
#         for cve_id_no in cve_ids:
#             cve_id = f'CVE-{cve_id_no}'
#             vuln_node = neo.get_node('Vulnerability', cve_id=cve_id).first()
#             if vuln_node is not None:
#                 neo.add_relationship(start=exploit_node, type_='Exploits', end=vuln_node)
#                 neo.add_relationship(start=vuln_node, type_='Exploited_by', end=exploit_node)
#                 for rel in rel_matcher.match([vuln_node], r_type='Affects'):
#                     pass
#     neo.close_db()
#     mylogger_p('timer').info(f'create_rel_eva runtime = {datetime.now() - start}')
#
#
# def init_vuln_p():
#     from db import MyMongo
#     from vuln_kg.vulnentity import split_properties, Vulnerability, ApiVersion
#     start = datetime.now()
#     mylogger_p('timer').info('Start init_vuln')
#     mg = MyMongo()
#     cursor = mg.get_nvd()
#     for doc in cursor.limit(limit):
#         doc = doc['content']
#         mylogger_p('init_kg').debug(doc)
#         props = split_properties(doc, api_ver=ApiVersion.NVDv1)
#         vuln = Vulnerability(props["vuln_props"])
#
#     mylogger_p('timer').info(f'init_vuln with limit {limit} runtime = {datetime.now() - start}')
#     return 0
#
#
# def init_asset_p():
#     from db import MyMongo
#     from vuln_kg.vulnentity import Asset
#     start = datetime.now()
#     mylogger_p('timer').info('Start init_asset')
#     mg = MyMongo()
#     cursor = mg.get_cpe()
#     for doc in cursor.limit(limit):
#         mylogger_p('init_kg').debug(doc)
#         asset = Asset(doc)
#
#     mylogger_p('timer').info(f'init_asset with limit {limit} runtime = {datetime.now() - start}')
#     return 0
#
#
# def init_exploit_p():
#     from db import MyMongo
#     from vuln_kg.vulnentity import Exploit
#     start = datetime.now()
#     mylogger_p('timer').info('Start init_exploit')
#     mg = MyMongo()
#     cursor = mg.get_edb()
#     for doc in cursor.limit(limit):
#         doc = doc['content']
#         mylogger_p('init_kg').debug(doc)
#
#         exploit = Exploit(doc)
#     mg.client.close()
#     mylogger_p('timer').info(f'init_exploit with limit {limit} runtime = {datetime.now() - start}')
#     return 0

def get_step(num):
	return max(int((num / 16) - 1), 1)


def init_nodes(vuln_num=0, asset_num=0, exploit_num=0):
	"""
	Ensure Vulnerability, Asset, Exploit, Asset:Family nodes exist
	Took around 5min to create or 2min to check the whole db for 1m nodes!

	:param vuln_num:
	:param asset_num:
	:param exploit_num:
	:return:
	"""
	node_start_time = datetime.now()

	if vuln_num and asset_num and exploit_num:
		mylogger_p('init_kg').info('Start Node init in parallel')
		'''Ensure Vulnerability, Asset, Exploit nodes exist'''
		arr = [init_vuln_ray.remote(skip=i, _limit=get_step(vuln_num) + 1) for i in
		       range(0, vuln_num, get_step(vuln_num))]
		arr.extend([init_asset_ray.remote(skip=i, _limit=get_step(asset_num) + 1) for i in
		            range(0, asset_num, get_step(asset_num))])
		arr.extend([init_exploit_ray.remote(skip=i, _limit=get_step(exploit_num) + 1) for i in
		            range(0, exploit_num, get_step(exploit_num))])
		mylogger_p('init_kg').info(arr)
		ray.get(arr)
		'''Ensure Asset:Family nodes exist'''
		family_id = [init_asset_family_ray.remote(skip=i, _limit=get_step(asset_num) + 1) for i in
		             range(0, asset_num, get_step(asset_num))]
		ray.get(family_id)
	# family_id = [fix_asset_family_ray.remote(skip=i, _limit=get_step(asset_num) + 1) for i in
	#              range(0, asset_num, get_step(asset_num))]
	# ray.get(family_id)
	else:
		mylogger_p('init_kg').info('Start Node init in 3 process')
		vuln_id = init_vuln_ray.remote()
		asset_id = init_asset_ray.remote()
		exploit_id = init_exploit_ray.remote()
		ray.get([vuln_id, asset_id, exploit_id])

		family_id = init_asset_family_ray.remote()
		ray.get([family_id])

	mylogger_p('init_kg').info('Finished Node init')
	mylogger_p('timer').info(
		f'ray.get([vuln_id, asset_id, exploit_id]) runtime = {datetime.now() - node_start_time}')


# from multiprocessing import Pool
#
# pool = Pool()
# vuln_id = pool.apply_async(init_vuln_p)
# asset_id = pool.apply_async(init_asset_p)
# exploit_id = pool.apply_async(init_exploit_p)
#
# answer = [asset_id.get(), vuln_id.get(), exploit_id.get()]
# mylogger_p('timer').info(answer)
# mylogger_p('timer').info(f'Pool with limit {limit} runtime = {datetime.now() - global_start}')


def get_node_stats_neo():
	_neo = MyNeo()
	neo_stat = {
		"Vuln": _neo.session.run('match (n:Vulnerability) return count(n)').data()[0]['count(n)'],
		"Asset": {
			"Total": _neo.session.run('match (n:Asset) return count(n)').data()[0]['count(n)'],
			"Application": _neo.session.run('match (n:Application) return count(n)').data()[0]['count(n)'],
			"OS": _neo.session.run('match (n:OperatingSystem) return count(n)').data()[0]['count(n)'],
			"Hardware": _neo.session.run('match (n:Hardware) return count(n)').data()[0]['count(n)'],
		},
		"Exploit": _neo.session.run('match (n:Exploit) return count(n)').data()[0]['count(n)'],
	}
	_neo.close_db()
	return neo_stat


def get_node_stats():
	mg_stat = {
		"Vuln": int(mg.nvd_json.estimated_document_count()),
		"Asset": int(mg.cpe.estimated_document_count()),
		"Exploit": int(mg.edb_json.estimated_document_count()),
	}
	return mg_stat


def init_rels(vuln_num=0, exploit_num=0):
	"""
	Ensure Vulnerability-Affects->Family, Family-Has->Vulnerability relationship exists
	Takes 2min on 160k vuls

	:param vuln_num:
	:param exploit_num:
	:return:
	"""
	rel_start_time = datetime.now()
	ray.init(ignore_reinit_error=True)
	mylogger_p('init_kg').info('Start Relationship init')

	if vuln_num and exploit_num:
		arr = []
		'''Ensure Vulnerability---Family relationships'''
		arr.extend([create_rel_vaf_ray.remote(skip=i, _limit=get_step(vuln_num) + 1) for i in
		            range(0, vuln_num, get_step(vuln_num))])
		'''Ensure Family---Asset relationships'''
		arr.extend([create_rel_afa_ray.remote(skip=i, _limit=get_step(vuln_num) + 1) for i in
		            range(0, vuln_num, get_step(vuln_num))])
		ray.get(arr)
		arr = [create_rel_evaf_ray.remote(skip=i, _limit=get_step(exploit_num) + 1) for i in
		       range(0, exploit_num, get_step(exploit_num))]
		ray.get(arr)
	else:
		rel_vaf = create_rel_vaf_ray.remote()
		rel_afa = create_rel_afa_ray.remote()
		ray.get([rel_vaf, rel_afa])
		rel_evaf = create_rel_evaf_ray.remote()
		ray.get([rel_evaf])

	mylogger_p('init_kg').info('Finished relationship init')
	mylogger_p('timer').info(
		f'init_rels() runtime = {datetime.now() - rel_start_time}')


if __name__ == "__main__":
	global_start = datetime.now()
	mylogger_p('timer').info('Start init')

	ray.init(ignore_reinit_error=True)
	n = MyNeo()
	n.check_node_index()
	n.check_rel_index()
	mylogger_p('db').info('Checked index, good to go')

	# init_nodes()

	mg_stats = get_node_stats()
	mylogger_p('init_kg').info(f"Mongo stat:\n{mg_stats}")
	try:
		# init_nodes(vuln_num=mg_stats['Vuln'], asset_num=mg_stats['Asset'], exploit_num=mg_stats['Exploit'])
		init_rels(vuln_num=mg_stats['Vuln'], exploit_num=mg_stats['Exploit'])
	except BaseException as err:
		mylogger_p('error').error(err, exc_info=True)

	neo_stats = get_node_stats_neo()
	mylogger_p('init_kg').info(f"Neo4j stat:\n{neo_stats}")

	# init_rels(vuln_num=int(stats['Vuln']), exploit_num=int(stats['Exploit']), step=3000)
	# create_rel_va()
	# create_rel_eva()

	mylogger_p('timer').info(f'Runtime = {datetime.now() - global_start}')
	n.close_db()
	mylogger_p('root').info('\n\n\n\n\n\n')

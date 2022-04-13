from pprint import pprint

if __name__ == '__main__':
    nodes = []
    asset_map = {
        "1": {"eid": 1},
        "2": {"eid": 2}
    }
    # pprint([k[1] for k in asset_map])
    nodes.extend([{
        "id": t[0],
        "data": t[1]
    } for t in asset_map.items()])
    pprint(nodes)

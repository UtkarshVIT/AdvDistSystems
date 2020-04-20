from __future__ import print_function
import requests
from flask import Flask, session, request, jsonify
import logging
import md5
from werkzeug.contrib.cache import MemcachedCache
import json
import ConsistentHashRing

import sys

cache = MemcachedCache(['0.0.0.0:11211'])
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
#json_data_file = '{ "nodes": [ {"ip":"172.23.0.3:5000", "key": 3000 }, {"ip":"172.23.0.4:5000", "key": 6000 }, { "ip":"172.23.0.5:5000", "key": 9000 } ] }'
json_data_file = '{"nodes":[{"ip":"152.46.18.69:80","key":3000},{"ip":"152.46.17.205:80","key":6000},{"ip":"152.46.19.28:80","key":9000}]}'
data = json.loads(json_data_file)
hash_ring = ConsistentHashRing.ConsistentHashRing(data["nodes"])
#hash_ring = None

@app.route('/', methods=['GET'])
def handle_get():
    return "Working Perfectly"

@app.route('/route', methods=['GET'])
def handle_route_get():
    key = request.args.get('key')
    node = hash_ring.get_node(key)
    key = hash_ring.gen_key(key)
    url = "http://" + node + "/cache"
    print('RECIEVED GET ROUTE REQ FOR KEY: ', key, ", FORWARDING TO NODE", node)
    res = requests.get(url = url, params = {'key': key}).text
    return res


@app.route('/route', methods=['POST'])
def handle_route_post():
    key = request.form.get('key')
    val = request.form.get('val')
    node = hash_ring.get_node(key)
    key = hash_ring.gen_key(key)
    url = "http://" + node + "/cache"
    print('RECIEVED POST ROUTE REQ FOR KEY: ', key, "VAL:", val,", FORWARDING TO NODE", node)
    requests.post(url = url, data = {'key': key, 'val': val})
    return "OK"

#this method knows the key is here
@app.route('/cache', methods=['GET'])
def handle_cache_get():
    #app.logger.info('Processing GET')
    key = request.args.get('key')
    val = cache.get(key)
    print('RECIEVED GET CACHE REQ FOR KEY:', key, ", VAL FOUND IN CACHE:", val)
    res = val if val is not None else 'N/A'
    return res

#this method sets the key is here
@app.route('/cache', methods=['POST'])
def handle_cache_post():
    #app.logger.info('Processing GET')
    key = request.form.get('key')
    val = request.form.get('val')
    print('RECIEVED POST CACHE REQ FOR KEY:', key, ", VAL:", val)
    cache.set(key, val)
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

# Request handler to update the state of the hash ring
# it takes the IP and they key and inserts in into it's 
# present hash ring
@app.route('/update_ring', methods=['POST'])
def handle_update_ring_post():
    node = request.form.get('ip')
    key = request.form.get('key')
    if hash_ring.contains(key):
        hash_ring.remove_node(key)
    else:
        hash_ring.add_node(node, key)
    return "OK"


# Request handler to fetch the key value pairs in a node
# belonging to a specific range
@app.route('/migrate/<int:key_min>/<int:key_max>', methods=['GET'])
def migrate_keys(key_min, key_max):
    # Construct a list of keys from the key you were given
    # TODO: Delete the retrieved keys
    ls = [str(integer) for integer in range(int(key_min), int(key_max))]
    d = cache.get_dict(*ls)
    all_objects = [(key, d[key]) for key in d.keys() if d[key] is not None]
    resp = {}
    for obj in all_objects:
        resp[obj[0]] = obj[1]
    return jsonify(resp)

# Request handler to bulk update keys in the new node.
@app.route('/bulk_update_keys', methods=['POST'])
def bulk_update_keys():
    dic = json.loads(request.form.get('dic'))
    for key in dic:
        cache.add(key, dic[key])
    return "OK"

# Request handler to orchestrate the addition of node
@app.route('/add_node/<int:key>/<node>')
def add_node(key, node):
    # Find what node you have to copy keys from
    temp = hash_ring._sorted_keys[0]
    target_node = None

    for _sorted_key in hash_ring._sorted_keys:
        print('hey', type(_sorted_key), type(key), type(temp))
        if _sorted_key > key and key > temp: # BUG: Does not handle case where it is between the first and last node (if it should be between 9000 and 3000, how do we handle this case? probably modulo)
            target_node = hash_ring.ring[str(_sorted_key)]
            break
        else:
            temp = _sorted_key
    print('hi', temp, target_node, key, node)
    # Fetch to get the keys value paris from that node in dict format
    url = "http://" + target_node + "/migrate/" + str(temp) + "/" + str(key) 
    dic = requests.get(url = url).json()

    # Send the fetched key-value pairs to the new node
    url = "http://" + node + "/bulk_update_keys"
    requests.post(url = url, data = {'dic': json.dumps(dic)})

    # Update own routing information
    hash_ring.add_node(node, key)
    
    #Broadcast the update in routing information
    for _key in hash_ring.ring.keys(): 
        url = "http://" + hash_ring.ring[_key] + "/update_ring"
        requests.post(url = url, data = {'ip': node, 'key': key})

    return 'OK'

@app.route('/remove_node/<node>', methods=['GET'])
def remove_node(node):
    # Find the node that will receive all of the deleted node's keys
    inv_map = {v: k for k, v in hash_ring.ring.items()}
    for x in inv_map:
        print(x)
    key = int(inv_map[node])
    print(key)   
 
    # Find what node you will have to copy the keys to
    max_key = hash_ring._sorted_keys[0]
    new_node = None
    
    # Find the next key after the target node's
    for _sorted_key in hash_ring._sorted_keys:
        if _sorted_key > key: # BUG: Does not handle case where it is between the first and last node (if it should be between 9000 and 3000, how do we handle this case? probably modulo)
            new_node = hash_ring.ring[str(_sorted_key)]
            max_key = _sorted_key
            break

    # Get all the keys from the target node
    url = "http://" + node + "/migrate/" + str(key) + "/" + str(max_key)
    dic = requests.get(url = url).json()

    # Add the keys 
    url = "http://" + new_node + "/bulk_update_keys"
    requests.post(url = url, data = {'dic': json.dumps(dic)})
    
    # Update routing information
    # hash_ring.remove_node(key)

    # Broadcast the update in routing information
    for _key in hash_ring.ring.keys():
        url = "http://" + hash_ring.ring[_key] + "/update_ring"
        requests.post(url = url, data = {'ip': node, 'key': key})

    return 'OK'

#API to fetch the key value pairs in this node
@app.route('/fetch_keys', methods=['GET'])
def handle_fetch_keys_get():
    ls = [str(integer) for integer in range(0, 10000)]
    d = cache.get_dict(*ls)
    return jsonify([(key, d[key]) for key in d.keys() if d[key] is not None])

#API to fetch the hash ring in this node
@app.route('/hash_ring', methods=['GET'])
def handle_hash_ring_get():
    return hash_ring.get_ring()

#API to fetch the hash ring in this node
@app.route('/hash_ring', methods=['POST'])
def handle_hash_ring_post():
    global hash_ring
    data = json.loads(request.form.get('data'))
    hash_ring = ConsistentHashRing.ConsistentHashRing(data["nodes"])
    print("Recived data", json.loads(request.form.get('data')))
    return "OK"
#TestAPI to return IP address of routed node
@app.route('/route_test', methods=['GET'])
def test_route_destination():
    key = request.args.get('key')
    return hash_ring.get_node(key)

"""def create_hash(key):
    #Given a string key, return a hash value.
    return long(md5.md5(key).hexdigest(), 16)
"""

from __future__ import print_function
import requests
from flask import Flask, session, request, jsonify
import logging
import md5
from werkzeug.contrib.cache import SimpleCache, MemcachedCache
import json
import ConsistentHashRing
import os
import sys

#Global object for handling the cache
cache = None
if os.environ["MODE"] == "DEV":
    cache = SimpleCache()
else:
    cache = MemcachedCache(['0.0.0.0:11211'], default_timeout=0)
#Globabl app object
app = Flask(__name__)

#Enable logging on the server
logging.basicConfig(level=logging.DEBUG)

#Global object for hashring related methods
hash_ring = ConsistentHashRing.ConsistentHashRing()

@app.route('/', methods=['GET'])
def handle_get():
    """Method to check if server is up and running

    Author:
        Utkarsh Sharma
    """
    return "DYNAMO_MOCK: NODE WITH FLASK RUNNING !"

@app.route('/route', methods=['GET'])
def handle_route_get():
    """This method is responsible for routing the GET request to the concerned node. It recieves the
    key as 'key' in the request parameter and using the key it finds the
    correct node for it. It then forwards the request to the concerned node on the /cache path and returns 
    the response from that server back to the client.

    Author:
        Utkarsh Sharma
    """
    key = request.args.get('key')
    node = hash_ring.get_node(key)
    url = "http://" + node + "/cache"
    print('DYNAMO_MOCK: RECIEVED GET ROUTE REQ FOR KEY: ', key, ", FORWARDING TO NODE", node)
    res = requests.get(url = url, params = {'key': key}).text
    return res

@app.route('/route', methods=['POST'])
def handle_route_post():
    """This method is responsible for routing the POST request to the concerned node. It recieves the
    key value pair as 'key' and 'value' in the request parameter and using the key it finds the
    correct node for it. It then forwards the pair to the concerned node on the /cache path and returns 
    the response from that server back to the client.

    Author:
        Utkarsh Sharma
    """
    key = request.form.get('key')
    val = request.form.get('val')
    node = hash_ring.get_node(key)
    url = "http://" + node + "/cache"
    print('DYNAMO_MOCK: RECIEVED POST ROUTE REQ FOR KEY: ', key, "VAL:", val,", FORWARDING TO NODE", node)
    requests.post(url = url, data = {'key': key, 'val': val})
    return "OK"

@app.route('/cache', methods=['GET'])
def handle_cache_get():
    """This method is responsible for serving the GET request for a key. It recieves the
    key as 'key' in the request parameter and using the key it queries the cache for a value. 
    If there is a value in the cache, it returns that value, otherwise it returns N/A

    Author:
        Utkarsh Sharma
    """
    key = request.args.get('key')
    key_hash = str(hash_ring.gen_key(key))
    val = cache.get(key_hash)
    print('DYNAMO_MOCK: RECIEVED GET CACHE REQ FOR KEY:', key, ", VAL FOUND IN CACHE:", val)
    res = val if val is not None else 'N/A'
    return res

@app.route('/cache', methods=['POST'])
def handle_cache_post():
    """This method is responsible for serving the POST request for a key value pair. It recieves the
    key value pair as 'key' and 'value' in the request parameter stores the key value pair in the cache
    and return 'OK'

    Author:
        Utkarsh Sharma
    """
    key = request.form.get('key')
    val = request.form.get('val')
    print('DYNAMO_MOCK: RECIEVED POST CACHE REQ FOR KEY:', key, ", VAL:", val)
    key = str(hash_ring.gen_key(key))
    cache.set(key, val)
    return 'OK'

@app.route('/update_ring', methods=['POST'])
def handle_update_ring_post():
    """Request handler to update the state of the hash ring it takes the IP and they key 
    and inserts in into it's present hash ring

    Author:
        Chris Benfante
    """
    print('DYNAMO_MOCK: RECIEVED UPDATE ROUTING INFO')
    node = request.form.get('ip')
    key = request.form.get('key')
    task = request.form.get('task')
    if task == "remove":
        hash_ring.remove_node(key)
    else:
        hash_ring.add_node(node, key)
    return "OK"

# 
@app.route('/migrate/<int:key_min>/<int:key_max>', methods=['GET'])
def migrate_keys(key_min, key_max):
    """Request handler to fetch the key value pairs in a node belonging to a specific range

    Author:
        Chris Benfante
    """
    # Construct a list of keys from the key you were given
    ls = [str(integer) for integer in range(int(key_min), int(key_max))]
    d = cache.get_dict(*ls)
    all_objects = [(key, d[key]) for key in d.keys() if d[key] is not None]
    all_keys = [key for key in d.keys() if d[key] is not None]
    cache.delete_many(*all_keys)
    resp = {}
    for obj in all_objects:
        resp[obj[0]] = obj[1]
    return jsonify(resp)

@app.route('/bulk_update_keys', methods=['POST'])
def bulk_update_keys():
    """Request handler to to bulk update keys in the node.

    Author:
        Utkarsh Sharma
    """
    dic = json.loads(request.form.get('dic'))
    for key in dic:
        cache.add(key, dic[key])
    return "OK"

@app.route('/add_node/<int:key>/<node>')
def add_node(key, node):
    """Request handler to orchestrate the addition of node. This method orchestrates the migration of 
    keys to new node and broacast update of the hash ring.

    Author:
        Chris Benfante
    """
    # Find what node you have to copy keys from
    hash_ring.get_state()
    temp = 0
    min_key = hash_ring._sorted_keys[0]
    target_node = hash_ring.ring[str(min_key)]

    for _sorted_key in hash_ring._sorted_keys:
        if _sorted_key > key: 
            target_node = hash_ring.ring[str(_sorted_key)]
            break
        else:
            temp = _sorted_key
    print('DYNAMO_MOCK: RECIEVED ADD NODE', node, "key", key)
    print('DYNAMO_MOCK: FETCHING KEYS FROM', target_node)

    # Fetch to get the keys value paris from that node in dict format
    url = "http://" + target_node + "/migrate/" + str(temp) + "/" + str(key) 
    dic = requests.get(url = url).json()
    
    # To handle the case when the range of keys is not continuous. This occurs when the new node
    # is added betwee the last and first node and keys go from (val_low -> MAX_VAL) + (0->val2)
    if key < hash_ring._sorted_keys[0]:
        max_key = hash_ring._sorted_keys[-1]
        url = "http://" + target_node + "/migrate/" + str(max_key) + "/" + str(10000) 
        dic_addnl_keys = requests.get(url = url).json()
        dic.update(dic_addnl_keys)
    print('DYNAMO_MOCK: NUM OF KEYS FETCHED', len(dic))
    
    # Send the fetched key-value pairs to the new node
    url = "http://" + node + "/bulk_update_keys"
    requests.post(url = url, data = {'dic': json.dumps(dic)})

    # Update own routing information
    hash_ring.add_node(node, key)
    print('DYNAMO_MOCK: SENDING UPDATE ROUTING INFO BROADCAST')
    
    #Broadcast the update in routing information
    for _key in hash_ring.ring.keys(): 
        url = "http://" + hash_ring.ring[_key] + "/update_ring"
        requests.post(url = url, data = {'ip': node, 'key': key, 'task': 'add'})

    return 'OK'

@app.route('/remove_node/<node>', methods=['GET'])
def remove_node(node):
    """Request handler to orchestrate the removal of node. This method orchestrates the migration of 
    keys to new node and broacast update of the hash ring.

    Author:
        Chris Benfante
    """
    hash_ring.get_state()
    print('DYNAMO_MOCK: RECIEVED REMOVE NODE', node)
    # Find the node that will receive all of the deleted node's keys
    inv_map = {v: k for k, v in hash_ring.ring.items()}
    for x in inv_map:
        print(x)
    key = int(inv_map[node])
    print(key)   
 
    # Find what node you will have to copy the keys to
    max_key = hash_ring._sorted_keys[0]
    new_node = hash_ring.ring[str(max_key)]
    
    # Find the next key after the target node's
    for _sorted_key in hash_ring._sorted_keys:
        if _sorted_key > key: 
            new_node = hash_ring.ring[str(_sorted_key)]
            max_key = _sorted_key
            break

    # Get all the keys from the target node
    url = "http://" + node + "/migrate/" + str(0) + "/" + str(10000)
    dic = requests.get(url = url).json()
    print('DYNAMO_MOCK: NUM OF KEYS FETCHED', len(dic))
    print('DYNAMO_MOCK: SENDING KEYS TO', new_node)
    
    # Add the keys 
    url = "http://" + new_node + "/bulk_update_keys"
    requests.post(url = url, data = {'dic': json.dumps(dic)})

    # Broadcast the update in routing information
    print('DYNAMO_MOCK: SENDING UPDATE ROUTING INFO BROADCAST')
    
    broadcast_nodes = [ hash_ring.ring[_key] for _key in hash_ring.ring.keys()]

    for _node in broadcast_nodes:
        url = "http://" + _node + "/update_ring"
        requests.post(url = url, data = {'ip': node, 'key': key, "task": 'remove'})

    return 'OK'

@app.route('/fetch_keys', methods=['GET'])
def handle_fetch_keys_get():
    """Request handler to GET the list of all keys on a node
    Author:
        Utkarsh Sharma
    """
    ls = [str(integer) for integer in range(0, 10000)]
    d = cache.get_dict(*ls)
    return jsonify([(key, d[key]) for key in d.keys() if d[key] is not None])

@app.route('/hash_ring', methods=['GET'])
def handle_hash_ring_get():
    """Request handler to GET hash ring status
    Author:
        Utkarsh Sharma
    """
    return hash_ring.get_ring()

@app.route('/hash_ring', methods=['POST'])
def handle_hash_ring_post():
    """Request handler for POST hash ring. It updates the hash ring with the data sent as the 
    parameter 'data' in the request.
    Author:
        Chris Benfante
    """
    global hash_ring
    data = json.loads(request.form.get('data'))
    hash_ring = ConsistentHashRing.ConsistentHashRing(data["nodes"])
    print("DYNAMO_MOCK: RECIEVED POST UPDATE HASH RING", json.loads(request.form.get('data')))
    return "OK"

@app.route('/route_test', methods=['GET'])
def test_route_destination():
    """Request to know the node responsible for storing the key.
    Author:
        Chris Benfante
    """
    key = request.args.get('key')
    return hash_ring.get_node(key)

@app.route('/clear_cache', methods=['GET'])
def clear_cache():
    """Request handler for clearing the cache on a node.
    Author:
        Chris Benfante
    """
    cache.clear()
    return "OK"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
from __future__ import print_function
import requests
from flask import Flask, session, request, jsonify
import logging
import md5
from werkzeug.contrib.cache import SimpleCache
import json
import ConsistentHashRing

import sys

cache = SimpleCache()
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
hash_ring = None

with open('./config.json') as json_data_file:
    data = json.load(json_data_file)
    hash_ring = ConsistentHashRing.ConsistentHashRing(data["nodes"])

@app.route('/route', methods=['GET'])
def handle_route_get():
    
    node = hash_ring.get_node(request.args.get('key'))

    url = "http://" + node + "/cache"
    print('####NODE', hash_ring.ring, node, url, request.args.get('key'))
    res = requests.get(url = url, params = {'key': request.args.get('key')}).text
    print('hey', res)
    return res


@app.route('/route', methods=['POST'])
def handle_route_post():
    key = request.form.get('key')
    val = request.form.get('val')
    node = hash_ring.get_node(key)
    url = "http://" + node + "/cache"
    requests.post(url = url, data = {'key': key, 'val': val})
    return "OK"

#this method knows the key is here
@app.route('/cache', methods=['GET'])
def handle_cache_get():
    #app.logger.info('Processing GET')
    print('>?>>>entered here')
    key = request.args.get('key')
    val = cache.get(key)
    res = val if val is not None else 'N/A'
    print('bro', res)
    return res

#this method sets the key is here
@app.route('/cache', methods=['POST'])
def handle_cache_post():
    #app.logger.info('Processing GET')
    key = request.form.get('key')
    val = request.form.get('val')
    cache.set(key, val)
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

# @app.route('/first_setup', methods=['POST'])
# def handle_post():
#     routing_info = requests.form['routing_info']
#     curr_node = requests.form['curr_node']

@app.route('/migrate/<int:key_min>/<int:key_max>', methods=['GET'])
def migrate_keys(key_min, key_max):
    # Construct a list of keys from the key you were given
    vals = cache.get_many(range(key_min, key_max))

    # TODO: Delete the retrieved keys

    # Return keys and routing info
    return jsonify(vals = vals)

@app.route('/join', methods=['POST'])
def node_join():
    vals = request.form.get('vals')
    hash_ring = request.form.get('ring')
    for val in vals:
        cache.add(hashring.gen_key(val), val)

@app.route('/add_node/<int:key>/<node>')
def add_node(key, node):
    # Find what node you have to copy keys from
    temp = hash_ring._sorted_keys[0]
    target_node = None

    for _sorted_key in hash_ring._sorted_keys:
        if _sorted_key > key and key > temp: # BUG: Does not handle case where it is between the first and last node (if it should be between 9000 and 3000, how do we handle this case? probably modulo)
            target_node = hash_ring.ring[_sorted_key]
            break
        else:
            temp = _sorted_key
    
    # Get the keys from that node
    url = "http://" + target_node + "/migrate/" + temp + "/" + key 
    vals = requests.get(url = url).json()['vals'] # Fix this once migrate is finished
    
    # Update routing information
    hash_ring.add_node(node, key_max)

    # Send the keys and routing info to the correct node
    url = "http://" + node + "/join"
    requests.post(url = url, data = {'vals': vals, 'ring': hash_ring})
    
    return 'OK'


"""def create_hash(key):
    #Given a string key, return a hash value.
    return long(md5.md5(key).hexdigest(), 16)
"""

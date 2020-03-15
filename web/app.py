from __future__ import print_function
import requests
from flask import Flask, session, request
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

"""def create_hash(key):
    #Given a string key, return a hash value.
    return long(md5.md5(key).hexdigest(), 16)
"""
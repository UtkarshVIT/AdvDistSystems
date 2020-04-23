import requests
import unittest
import ast
import json
#from random_words import RandomWords
import threading
import time

lb_addr = "18.190.25.30:80"
var1 = "3.16.111.212:80"
var2 = "3.21.171.240:80"
var3 = "3.15.191.148:80"

standby_addr = var3
removenode_addr = var2
migrated_to_addr = var1
nodes = [var1, var2, var3]
post_removal = [var1, var3]

key_map = {"bathtub": "bathtub1", "bed":"bed1", "bee":"bee1", "finger":"finger1", \
			"gas":"gas1", "gate":"gate1", "flower":"flower1", "mist":"mist1",\
			"saddle":"saddle1", "ship":"ship1", "shoes":"shoes1", "roof":"roof1"}

class TestScaling(unittest.TestCase):
	#Testing insert into the system
	#@unittest.skip("skipiing this")
	def test1(self):
		for key in key_map:
			data = {"key": key, "val": key_map[key]}
			route_url = "http://" + lb_addr + "/route"
			r = requests.post(url = route_url, data = data)
			self.assertEqual( r.status_code, 200)
			self.assertEqual( r.text, "OK")

	#Testing key based lookup from the system
	#@unittest.skip("skipiing this")
	def test2(self):
		for key in key_map:
			params = {"key": key}
			route_url = "http://" + lb_addr + "/route"
			r = requests.get(url = route_url, params = params)
			self.assertEqual( r.status_code, 200)
			self.assertEqual( r.text, key_map[key])

	#Testing scale and broadcast
	#@unittest.skip("skipiing this")
	def test3(self):
		route_url = "http://" + lb_addr + "/add_node/5000/" + standby_addr
		r = requests.get(url = route_url)
		self.assertEqual(r.text, "OK")
		test_keys = ['bed', 'bathtub', 'bee']
		for test_key in test_keys:
			params = {"key": test_key}
			route_url = "http://" + lb_addr + "/route_test"
			result = requests.get(url = route_url, params = params).text
			self.assertEqual(result, standby_addr)
		for node in nodes:
			url = "http://" + node + '/hash_ring'
			result = json.loads(requests.get(url = url).text)
			keys = sorted(result["ring"].keys())
			self.assertEqual(keys, ['3000', '5000', '8000'])

	#@unittest.skip("skipiing this")
	def test4(self):
		route_url = "http://" + lb_addr + "/remove_node/" + removenode_addr
		r = requests.get(url = route_url)
		self.assertEqual(r.text, "OK")
		test_keys = ['finger', 'gate', 'gas']
		for test_key in test_keys:
			params = {"key": test_key}
			route_url = "http://" + lb_addr + "/route_test"
			result = requests.get(url = route_url, params = params).text
			self.assertEqual(result, migrated_to_addr)

		for node in nodes:
			url = "http://" + node + '/hash_ring'
			result = json.loads(requests.get(url = url).text)
			keys = sorted(result["ring"].keys())
			self.assertEqual(keys, ['3000', '5000'])

	# @unittest.skip
	# def test_04_system_evaluate(self):
	# 	for i in range(1, 5):
	# 		measure_perform_requests(i*100, 90)

	# 	for i in range(1, 5):
	# 		measure_perform_requests(i*100, 10)

	# 	for i in range(1, 5):
	# 		measure_perform_requests(i*100, 50)
	# 	self.assertEqual(True, True)

'''
'roof' 2184     'gate' 6051    'mist' 8155
'bed' 4019      'finger' 6823  'flower' 8700
'bathtub' 4324  'gas' 6952     'shoes' 9235
'bee' 4603      'saddle' 8016  'ship' 9381









'''

if __name__ == '__main__':
	unittest.main()

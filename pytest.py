import requests
import unittest
import json
import threading
import time

"""Testing routing and scaling of the system.

Example:
    The whole system can be tested by running the following 
	command. This command runs the 4 test cases in sequential 
	order::

        $ python pytest.py

	A single test case can also be exectuted as::

        $ python pytest.py TestScaling.test1

Attributes:
    var1 (str): ip_address:port_number of node1
	var2 (str): ip_address:port_number of node2
	var3 (str): ip_address:port_number of node3
	lb_addr (str) = ip_address:port_number of the load balancer
	key_map = set of key value pairs
	
	For example we can set the IP of var1 as::
		var1 = "172.23.1.1:80"

	Table for refernce of hash value of the keys in `key_map`::

	| 'roof' 2184    | 'gate' 6051    | 'mist' 8155   |
	| 'bed' 4019     | 'finger' 6823  | 'flower' 8700 |
    | 'bathtub' 4324 | 'gas' 6952     | 'shoes' 9235  |
	| 'bee' 4603     | 'saddle' 8016  | 'ship' 9381   |

Todo:
    * Enter the IP address for var1, var2, var3 and the 
	loadbalancer before executing the testcases.

"""
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
	"""
    Class for System tests

    This class defines a set of functions to first test the routing and caching of the system
	and then test the scaling up and scaling down of the system.
    """

	def test1(self):
		"""test1 simulates intersting keys into the system and checks if the keys got routed
		to the correct node.
		
		Author: Utkarsh Sharma
		"""
		for key in key_map:
			data = {"key": key, "val": key_map[key]}
			route_url = "http://" + lb_addr + "/route"
			r = requests.post(url = route_url, data = data)
			self.assertEqual( r.status_code, 200)
			self.assertEqual( r.text, "OK")
		test_keys = {'finger':var2, 'gate':var2, 'roof':var1, 'ship':var1}
		for test_key in test_keys:
			params = {"key": test_key}
			route_url = "http://" + lb_addr + "/route_test"
			result = requests.get(url = route_url, params = params).text
			self.assertEqual(result, test_keys[test_key])

	def test2(self):
		"""test2 simulates fetching values of already inserted keys from the system 
		and compares the value fetched with the value sent for insertion.
		
		Author: Utkarsh Sharma
		"""
		for key in key_map:
			params = {"key": key}
			route_url = "http://" + lb_addr + "/route"
			r = requests.get(url = route_url, params = params)
			self.assertEqual( r.status_code, 200)
			self.assertEqual( r.text, key_map[key])

	def test3(self):
		"""test3 simulates adding a node [node with ip standby_addr] into the system 
		and asserting key migration and routing information updation.
		
		Author: Chris Benfante
		"""
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

	def test4(self):
		"""test4 simulates removing a node [node with ip removenode_addr] into the system 
		and asserting key migration and routing information updation.
		
		Author: Chris Benfante
		"""
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

if __name__ == '__main__':
	unittest.main()

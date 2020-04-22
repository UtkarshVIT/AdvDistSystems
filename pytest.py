import requests
import unittest
import ast
import json
#from random_words import RandomWords
import threading
import time

lb_addr = "18.190.25.30:80"
var1 = "3.21.171.240:80"
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

'''
with open('final-json.txt', 'r') as f:
	d = json.load(f)

def send_get(key):
	params = {"key": key}
	r = requests.get(url = route_url, params = params)

def send_post(key, val):
	data = {"key": key, "val": val}
	r = requests.post(url = route_url, data = data)

def measure_perform_requests(k, percent_reads):
	
	keys_list = list(d.keys())[:k]
	threads = []
	start_time = time.time()
	for key in keys_list[:int(k*(0.01*percent_reads))]:
		threads.append(threading.Thread(target=send_get, args=(key,)))
	for key in keys_list[:int(k*(0.01*(1.0-percent_reads)))]:
		threads.append(threading.Thread(target=send_post, args=(key, d[key])))
	for thread in threads:
		thread.start()
	for thread in threads:
		thread.join()
	print("k = ", k, "percent_reads = ", percent_reads, "total = ", str(time.time() - start_time), "avg = ", float(time.time() - start_time)/k)
'''

class TestStringMethods(unittest.TestCase):
	#Testing insert into the system

	def test_01_system_insert(self):
		for key in key_map:
			data = {"key": key, "val": key_map[key]}
			route_url = "http://" + lb_addr + "/route"
			r = requests.post(url = route_url, data = data)
			self.assertEqual( r.status_code, 200)
			self.assertEqual( r.text, "OK")

	#Testing key based lookup from the system
	def test_02_system_fetch(self):
		for key in key_map:
			params = {"key": key}
			route_url = "http://" + lb_addr + "/route"
			r = requests.get(url = route_url, params = params)
			self.assertEqual( r.status_code, 200)
			self.assertEqual( r.text, key_map[key])

	#Testing scale and broadcast
	@unittest.skip("skipiing this")
	def test_03_system_scale_up(self):
		route_url = "http://" + lb_addr + "/add_node/5000/" + standby_addr
		r = requests.get(url = route_url)
		self.assertEqual(r.text, "OK")
		
		route_url = "http://" + standby_addr + "/fetch_keys"
		r = requests.get(url = route_url)
		result = ast.literal_eval(r.text)
		result = sorted([obj[0] for obj in result])
		self.assertEqual(result, ['4019', '4324', '4603'])
		for node in nodes:
			url = "http://" + node + '/hash_ring'
			result = json.loads(requests.get(url = url).text)
			keys = sorted(result["ring"].keys())
			self.assertEqual(keys, ['3000', '5000', '8000'])

	@unittest.skip("skipiing this")
	def test_04_system_scale_down(self):
		route_url = "http://" + lb_addr + "/remove_node/" + removenode_addr
		r = requests.get(url = route_url)
		self.assertEqual(r.text, "OK")
		
		route_url = "http://" + migrated_to_addr + "/fetch_keys"
		r = requests.get(url = route_url)
		result = ast.literal_eval(r.text)
		result = sorted([obj[0] for obj in result])
		self.assertEqual(sorted(result), sorted(["8016","2184","9381","8155","6051","6823","8700","6952","9235"]))
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

if __name__ == '__main__':
	unittest.main()

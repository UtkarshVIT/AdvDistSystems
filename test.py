import requests
import unittest
import ast
import json
from random_word import RandomWords
import threading
import time


route_url = 'http://0.0.0.0:8080/route'
scale_url = 'http://0.0.0.0:8080/add_node/7300/172.23.0.7:5000'
new_node_url = 'http://0.0.0.0:8084/fetch_keys'
node_ports = ["8081", "8082", "8083", "8084"] 

key_map = {"bathtub": "bathtub1", "bed":"bed1", "bee":"bee1", "finger":"finger1", \
			"gas":"gas1", "gate":"gate1", "flower":"flower1", "mist":"mist1",\
			"saddle":"saddle1", "ship":"ship1", "shoes":"shoes1", "roof":"roof1"}

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


class TestStringMethods(unittest.TestCase):
	#Testing insert into the system
	@unittest.skip
	def test_01_system_insert(self):
		for key in key_map:
			data = {"key": key, "val": key_map[key]}
			r = requests.post(url = route_url, data = data)
			#r = requests.get(url = route_url)
			self.assertEqual( r.status_code, 200)
			self.assertEqual( r.text, "OK")

	#Testing key based lookup from the system
	@unittest.skip
	def test_02_system_fetch(self):
		for key in key_map:
			params = {"key": key}
			r = requests.get(url = route_url, params = params)
			self.assertEqual( r.status_code, 200)
			self.assertEqual( r.text, key_map[key])

	#Testing scale and broadcast
	@unittest.skip
	def test_03_system_scale_up(self):
		requests.get(url = scale_url)
		r = requests.get(url = new_node_url)
		result = ast.literal_eval(r.text)
		result = sorted([obj[0] for obj in result])
		self.assertEqual(result, ['6051', '6823', '6952'])
		for port in node_ports:
			url = 'http://0.0.0.0:' + port + '/hash_ring'
			result = json.loads(requests.get(url = url).text)
			keys = sorted(result["ring"].keys())
			self.assertEqual(keys, ['3000', '6000', '7300', '9000'])

	def test_04_system_evaluate(self):
		for i in range(1, 5):
			measure_perform_requests(i*100, 90)

		for i in range(1, 5):
			measure_perform_requests(i*100, 10)

		for i in range(1, 5):
			measure_perform_requests(i*100, 50)
		self.assertEqual(True, True)

if __name__ == '__main__':
	unittest.main()
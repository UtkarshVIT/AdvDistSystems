import md5
import json
import hashlib
from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache()

class ConsistentHashRing(object):
    """ 
    This is a class for manages a hash ring on each node.
      
    Attributes: 
        ring (dict<str:str>): mapping of 'key': 'ip:port'
        _sorted_keys (list[str]): sorted keys on the ring

    Example:
        
                (k1=3000)
               ____n1___
              |         |            | n1 = 172.23.0.3:5000
    (k3=9000)n3         n2 k2=(6000) | n2 = 172.23.0.4:5000 
              |_________|            | n3 = 172.23.0.5:5000

    ring: {'3000':'172.23.0.3:5000',
           '6000':'172.23.0.4:5000',
           '9000':'172.23.0.5:5000'}

    _sorted_keys: [3000, 6000, 9000]
    """

    def __init__(self, nodes):
        """ 
        The constructor for ConsistentHashRing class. The class attributes are initialised using the node parameter
        of the constructor
  
        Parameters: 
           nodes (list[dict]): e.g. [{"ip":"<ip1:port1>", "key": "<key1>"}, {"ip":"<ip2:port2>", "key": "<key2>"}, ...]   
        """

        self.ring = dict()
        self._sorted_keys = []
        for node in nodes:
            self.add_node(node["ip"], node["key"])
        self.save_state()

    def save_state(self):
        cache.set("ring", json.dumps(self.ring))
        cache.set("_sorted_keys", json.dumps(self._sorted_keys))

    def get_state(self):
        print('yoyo1', cache.get("ring"))
        print('yoyo2', cache.get("_sorted_keys"))
        cache_ring = cache.get("ring")
        if cache_ring is not None: 
            self.ring = json.loads(cache.get("ring"))
            self._sorted_keys = json.loads(cache.get("_sorted_keys"))

    def get_ring(self):
        self.get_state()
        return json.dumps({"ring": self.ring, "_sorted_keys": self._sorted_keys})

    def add_node(self, node, key):
        """Adds a `node` to the hash ring.
        """
        self.get_state()
        if int(key) not in self._sorted_keys:
            self.ring[str(key)] = node
            self._sorted_keys.append(int(key))
            self._sorted_keys.sort()
        self.save_state()

    def get_node(self, string_key):
        """Given a string_key a corresponding node in the hash ring is returned
        along with it's position in the ring.
        If the hash ring is empty, (`None`, `None`) is returned.
        """
        self.get_state()
        print("in here", self.ring)
        h_key = self.gen_key(string_key)
        for _sorted_key in self._sorted_keys:
            if h_key <= _sorted_key:
                return self.ring[str(_sorted_key)]
        return self.ring[str(self._sorted_keys[0])]
    
    def gen_key(self, key):
        """Given a string key it returns a long value,
        this long value represents a place on the hash ring.
        md5 is currently used because it mixes well.
        """
        return int(hashlib.md5(key).hexdigest(),16) % 10000

'''
    def remove_node(self, node):
        """Removes `node` from the hash ring and its replicas.
        """
        for i in xrange(0, self.replicas):
            key = self.gen_key('%s:%s' % (node, i))
            del self.ring[key]
            self._sorted_keys.remove(key)
'''

'''
    def get_nodes(self, string_key):
        """Given a string key it returns the nodes as a generator that can hold the key.
        The generator is never ending and iterates through the ring
        starting at the correct position.
        """
        if not self.ring:
            yield None, None
        node, pos = self.get_node_pos(string_key)
        for key in self._sorted_keys[pos:]:
            yield self.ring[key]
        while True:
            for key in self._sorted_keys:
                yield self.ring[key]
'''

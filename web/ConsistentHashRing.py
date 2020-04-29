import os
import md5
import json
import hashlib
from werkzeug.contrib.cache import SimpleCache, MemcachedCache

#Global object for handling the cache
if os.environ["MODE"] == "DEV":
    cache = SimpleCache()
else:
    cache = MemcachedCache(['0.0.0.0:11211'], default_timeout=0)

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

    def __init__(self, nodes=None):
        """ 
        The constructor for ConsistentHashRing class. The class attributes are initialised using the node parameter
        of the constructor
  
        Attributes: 
           nodes (list[dict]): e.g. [{"ip":"<ip1:port1>", "key": "<key1>"}, {"ip":"<ip2:port2>", "key": "<key2>"}, ...]  

        Author:
            Utkarsh Sharma 
        """

        self.ring = dict()
        self._sorted_keys = []
        if nodes!=None:
            for node in nodes:
                self.add_node(node["ip"], node["key"])
            self.save_state()

    def save_state(self):
        """Save the status of the ring.

        Author:
            Chris Benfante
        """
        cache.set("ring", json.dumps(self.ring))
        cache.set("_sorted_keys", json.dumps(self._sorted_keys))

    def get_state(self):
        """GET the status of the hash ring. If the ring for the server is set, we return 
        the ring and the sorted keys list

        Author:
            Chris Benfante
        """
        if cache.get("ring") is not None:
            self.ring = json.loads(cache.get("ring"))
            self._sorted_keys = json.loads(cache.get("_sorted_keys"))

    def get_ring(self):
        """GET the status of the hash ring.

        Author:
            Utkarsh Sharma
        """
        self.get_state()
        return json.dumps({"ring": self.ring, "_sorted_keys": self._sorted_keys})

    def add_node(self, node, key):
        """Adds a `node` to the hash ring.

        Attributes:
            node (str): 'ip_address:port_number' of new server.
            key (str): key for which to add new server.

        Author:
            Utkarsh Sharma
        """
        self.get_state()
        if int(key) not in self._sorted_keys:
            self.ring[str(key)] = node
            self._sorted_keys.append(int(key))
            self._sorted_keys.sort()
        self.save_state()

    def remove_node(self, key):
        """Removes a `node` to the hash ring.

        Attributes:
            key (str): key for which to remove server.

        Author:
            Utkarsh Sharma
        """
        self.get_state()
        del self.ring[str(key)]
        self._sorted_keys.remove(int(key))
        self.save_state()

    def get_node(self, string_key):
        """Given a string_key a corresponding node in the hash ring is returned
        along with it's position in the ring.
        If the hash ring is empty, (`None`, `None`) is returned.
        
        Attributes:
            key (str): key for which to remove server.

        Author:
            Chris Benfante
        """
        self.get_state()
        h_key = self.gen_key(string_key)
        for _sorted_key in self._sorted_keys:
            if h_key <= _sorted_key:
                return self.ring[str(_sorted_key)]
        return self.ring[str(self._sorted_keys[0])]
    
    def gen_key(self, key):
        """Given a string key it returns a long value, this long value represents a place 
        on the hash ring. md5 is currently used because it mixes well.

        Attributes:
            key (str): key value to generate the hash.

        Author:
            Chris Benfante
        """
        return int(hashlib.md5(key).hexdigest(),16) % 10000

    def contains(self, key):
        """Return True if a key exists on a server.
        
        Attributes:
            key (str): key to examine.

        Author:
            Chris Benfante
        """
        if str(key) in self.ring.keys():
            return True
import md5
import hashlib

class ConsistentHashRing(object):
    def __init__(self, nodes):
        #Initialize it in this format: [['ip1:port1, key1'], ['ip2:port2, key2'], ..]
        """Manages a hash ring.
        `nodes` is a list of objects that have a proper __str__ representation.
        `replicas` indicates how many virtual points should be used pr. node,
        replicas are required to improve the distribution.
        """
        self.ring = dict()
        self._sorted_keys = []
        for node in nodes:
            self.add_node(node["ip"], node["key"], true)

    def add_node(self, node, key):
        """Adds a `node` to the hash ring (including a number of replicas).
        """
        self.ring[key] = node
        self._sorted_keys.append(key)
        self._sorted_keys.sort()

    def get_node(self, string_key):
        """Given a string key a corresponding node in the hash ring is returned
        along with it's position in the ring.
        If the hash ring is empty, (`None`, `None`) is returned.
        """

        h_key = self.gen_key(string_key)
        for _sorted_key in self._sorted_keys:
            if h_key <= _sorted_key:
                return self.ring[_sorted_key]
        return self.ring[self._sorted_keys[0]]
    
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

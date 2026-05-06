"""
LRU (Least Recently Used) 缓存实现
"""

from collections import OrderedDict


class LRUCache:
    """LRU 缓存，当缓存达到最大容量时，自动删除最久未使用的项"""

    def __init__(self, max_size=100):
        self.cache = OrderedDict()
        self.max_size = max_size

    def get(self, key):
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def remove(self, key):
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        self.cache.clear()

    def __len__(self):
        return len(self.cache)

    def __contains__(self, key):
        return key in self.cache

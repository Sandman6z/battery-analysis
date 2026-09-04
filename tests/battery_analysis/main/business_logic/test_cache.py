"""LRU 缓存 (cache) 测试

测试 cache.py 中 LRUCache 类的 get/put/eviction 逻辑，
覆盖容量限制、LRU 淘汰、删除和清空操作。
"""

import pytest

from battery_analysis.main.business_logic.cache import LRUCache


class TestLRUCacheBasic:
    """LRUCache 基本操作测试。"""

    def test_put_and_get(self):
        """put 后 get 应返回对应值。"""
        cache = LRUCache(max_size=3)
        cache.put("a", 1)
        assert cache.get("a") == 1

    def test_get_missing_key(self):
        """get 不存在的 key 应返回 None。"""
        cache = LRUCache(max_size=3)
        assert cache.get("nonexistent") is None

    def test_put_overwrite(self):
        """put 已有 key 应覆盖值。"""
        cache = LRUCache(max_size=3)
        cache.put("a", 1)
        cache.put("a", 2)
        assert cache.get("a") == 2

    def test_len(self):
        """__len__ 应返回缓存中的项数。"""
        cache = LRUCache(max_size=5)
        cache.put("a", 1)
        cache.put("b", 2)
        assert len(cache) == 2

    def test_contains(self):
        """__contains__ 应正确判断 key 是否存在。"""
        cache = LRUCache(max_size=3)
        cache.put("a", 1)
        assert "a" in cache
        assert "b" not in cache


class TestLRUCacheEviction:
    """LRUCache 淘汰策略测试。"""

    def test_evicts_least_recently_used(self):
        """超过容量时应淘汰最久未使用的项。"""
        cache = LRUCache(max_size=2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)  # "a" 应被淘汰
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_get_refreshes_order(self):
        """get 操作应刷新项的使用顺序。"""
        cache = LRUCache(max_size=2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.get("a")  # 刷新 "a"
        cache.put("c", 3)  # "b" 应被淘汰（而非 "a"）
        assert cache.get("a") == 1
        assert cache.get("b") is None
        assert cache.get("c") == 3

    def test_put_existing_refreshes_order(self):
        """put 已有 key 也应刷新使用顺序。"""
        cache = LRUCache(max_size=2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("a", 10)  # 刷新 "a"
        cache.put("c", 3)  # "b" 应被淘汰
        assert cache.get("a") == 10
        assert cache.get("b") is None


class TestLRUCacheRemoveAndClear:
    """LRUCache 删除和清空测试。"""

    def test_remove_existing(self):
        """remove 已有 key 应成功删除。"""
        cache = LRUCache(max_size=3)
        cache.put("a", 1)
        cache.remove("a")
        assert cache.get("a") is None
        assert len(cache) == 0

    def test_remove_nonexistent(self):
        """remove 不存在的 key 不应抛异常。"""
        cache = LRUCache(max_size=3)
        cache.remove("nonexistent")  # 不应抛异常

    def test_clear(self):
        """clear 应清空所有缓存项。"""
        cache = LRUCache(max_size=3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.clear()
        assert len(cache) == 0
        assert cache.get("a") is None

    def test_max_size_one(self):
        """max_size=1 时每次 put 都应淘汰前一项。"""
        cache = LRUCache(max_size=1)
        cache.put("a", 1)
        cache.put("b", 2)
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert len(cache) == 1

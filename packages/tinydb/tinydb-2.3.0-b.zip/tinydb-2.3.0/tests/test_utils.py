import warnings
import pytest

from tinydb.utils import LRUCache, catch_warning


def test_lru_cache():
    cache = LRUCache(capacity=3)
    cache["a"] = 1
    cache["b"] = 2
    cache["c"] = 3
    _ = cache["a"]  # move to front in lru queue
    cache["d"] = 4  # move oldest item out of lru queue

    assert cache.lru == ["c", "a", "d"]


def test_lru_cache_set_multiple():
    cache = LRUCache(capacity=3)
    cache["a"] = 1
    cache["a"] = 2
    cache["a"] = 3
    cache["a"] = 4

    assert cache.lru == ["a"]


def test_lru_cache_get():
    cache = LRUCache(capacity=3)
    cache["a"] = 1
    cache["b"] = 1
    cache["c"] = 1
    cache.get("a")
    cache["d"] = 4

    assert cache.lru == ["c", "a", "d"]


def test_lru_cache_delete():
    cache = LRUCache(capacity=3)
    cache["a"] = 1
    cache["b"] = 2
    del cache["a"]

    assert cache.lru == ["b"]


def test_lru_cache_clear():
    cache = LRUCache(capacity=3)
    cache["a"] = 1
    cache["b"] = 2
    cache.clear()

    assert cache.lru == []


def test_lru_cache_unlimited():
    cache = LRUCache()
    for i in range(100):
        cache[i] = i

    assert len(cache.lru) == 100


def test_lru_cache_unlimited_explicit():
    cache = LRUCache(capacity=None)
    for i in range(100):
        cache[i] = i

    assert len(cache.lru) == 100


def test_catch_warning():
    class MyWarning(Warning):
        pass

    filters = warnings.filters[:]

    with pytest.raises(MyWarning):
        with catch_warning(MyWarning):
            warnings.warn("message", MyWarning)

    assert filters == warnings.filters


def test_catch_warning_reset_filter():
    class MyWarning(Warning):
        pass

    warnings.filterwarnings(action='once', category=MyWarning)

    with pytest.raises(MyWarning):
        with catch_warning(MyWarning):
            warnings.warn("message", MyWarning)

    filters = [f for f in warnings.filters if f[2] == MyWarning]
    assert filters
    assert filters[0][0] == 'once'

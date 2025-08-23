import time
import functools

def ttl_cache(seconds: int):
    def deco(fn):
        cache: dict = {}
        @functools.wraps(fn)
        def wrapper(*a, **k):
            key = (a, frozenset(k.items()))
            ts_v = cache.get(key)
            now = time.time()
            if ts_v and now - ts_v[0] < seconds:
                return ts_v[1]
            v = fn(*a, **k)
            cache[key] = (now, v)
            return v
        return wrapper
    return deco

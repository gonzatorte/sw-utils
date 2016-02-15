import datetime


class CacheManager:
    def __init__(self):
        self.primary = None
        self.cache = None
        self.last_misses = []
        self.hit_size_rate = 0

    def update(self):
        pass

    def get(self, key):
        try:
            res = self.cache.get(key)
        except KeyError:
            self.last_misses.append((datetime.datetime.utcnow(), key))
            if len(self.last_misses) > 100:
                self.last_misses.pop()
            res = self.primary.get(key)
            self.cache.set(key, res)
        return res

    def filter(self):
        pass

    def _evict(self):
        pass

    def migrate(self):
        pass


class CacheManagerWriteThrought(CacheManager):
    pass


class CacheManagerWriteBack(CacheManager):
    pass


class CacheManagerWriteBack_Dirty(CacheManagerWriteBack):
    pass


class CacheManagerTimeout(CacheManager):
    pass


class CacheManagerSpatial(CacheManager):
    pass


class CacheManagerTemporal(CacheManager):
    pass

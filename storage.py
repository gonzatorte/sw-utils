from sw_utils.deep_dict import DeepDict
from sw_utils.profile import get_profiler
import redis


class CachedStorage:
    """
    Es un sistema con cache write_trought delayed, y merge 'inteligente' al guardar...
    ademas se supone el cache local no expira y no tiene limite
    """
    def __init__(self, primary_storage, cache_storage):
        self.primary = primary_storage
        self.cache = cache_storage

    def get(self, key):
        res = self.cache.get(key)
        if res is None:
            res = self.primary.get(key)
            self.cache.set(key, res)
        return res

    def set(self, key, val):
        self.cache.set(key, val)

    def update(self, key, update_fun, *args):
        d = self.cache.get(key)
        d = update_fun(d, *args)
        self.cache.set(key, d)

    def _merge(self):
        pp = get_profiler()
        for k in self.cache.keys():
            v = self.cache.get(k)
            execn = v['execs']
            for execi in execn:
                extra_ls = execi.get('extra', [])
                self.primary.update(k, pp._profiler_update_storage, execi['etimes'], execi['capture'], *extra_ls)
        self.cache.reset()

    def reset(self):
        self.cache.reset()
        self.primary.reset()

    def flush(self):
        self._merge()

    def __del__(self):
        self.flush()


class RedisStorage:
    def __init__(self, host, db):
        self.rediscli = redis.Redis(host=host, db=db)

    def keys(self):
        """
        retorna las claves de redis mas las de suus dict internos en prof
        :return:
        """
        res = []
        #ToDo: la key de skey no es la misma que se le pasa en el set, sino que es la crude en redis... fix
        s_keys = self.rediscli.keys()
        for s_key in s_keys:
            res.append([s_key])
            raw_statistics_data = self.rediscli.get(s_key)
            statistics = DeepDict()
            if raw_statistics_data:
                statistics.deserialize(raw_statistics_data)
            r_keys = statistics.keys()
            for r_key in r_keys:
                res.append([s_key] + r_key)
        return res

    def children(self, ks=None):
        #ToDo: Pensar en que es mejor hacer una interfaz comun de dict para redis y
        # luego agregarlo a una estructura mixta... se aplicaria recursion pero cada nodo puede ser lo que quiera
        # y se eliminarian los storage en favor de varios tipos de DeepDict (DicTree)
        if ks is None or (len(ks) == 0):
            res = {}
            s_keys = self.rediscli.keys()
            for skey in s_keys:
                raw_statistics_data = self.rediscli.get(skey)
                statistics = DeepDict()
                if raw_statistics_data:
                    statistics.deserialize(raw_statistics_data)
                #ToDo: La key yampoco es la misma del set, es la cruda de redis
                res[skey] = statistics
            return res
        else:
            raw_statistics_data = self.rediscli.get(ks[0])
            statistics = DeepDict()
            if raw_statistics_data:
                statistics.deserialize(raw_statistics_data)
            nn = statistics.node(ks[1:])
            if nn is not None:
                return nn.children()
            else:
                return {}

    def get(self, key):
        s_key = "%s" % (key[0],)
        raw_statistics_data = self.rediscli.get(s_key)
        statistics = DeepDict()
        if raw_statistics_data:
            statistics.deserialize(raw_statistics_data)
        val = statistics.get(key[1:])
        return val

    def set(self, key, val):
        s_key = "%s" % (key[0],)

        statistics = DeepDict()

        statistics.set(key[1:], val)
        raw_statistics_data = statistics.serialize()
        self.rediscli.set(s_key, raw_statistics_data)

    def update(self, key, update_fun, *args):
        s_key = "%s" % (key[0],)

        raw_statistics_data = self.rediscli.get(s_key)
        statistics = DeepDict()
        if raw_statistics_data:
            statistics.deserialize(raw_statistics_data)
        val = statistics.get(key[1:])

        val = update_fun(val, *args)

        statistics.set(key[1:], val)
        raw_statistics_data = statistics.serialize()
        self.rediscli.set(s_key, raw_statistics_data)

    def flush(self):
        pass

    def reset(self):
        self.rediscli.flushdb()

    def __del__(self):
        self.flush()


class LocalStorage:
    def __init__(self):
        # self.data = {}
        self.data = DeepDict()

    def keys(self):
        return self.data.keys()

    def get(self, key):
        tkey = tuple(key)
        d = self.data.get(tkey, None)
        return d

    def set(self, key, val):
        tkey = tuple(key)
        self.data[tkey] = val

    def children(self, key=None):
        if key is None:
            return self.data.children(())
        else:
            tkey = tuple(key)
            return self.data.children(tkey)

    def update(self, key, update_fun, *args):
        d = self.get(key)
        d = update_fun(d, *args)
        self.set(key, d)

    def reset(self):
        self.data = DeepDict()

    def flush(self):
        pass

    def __del__(self):
        self.flush()
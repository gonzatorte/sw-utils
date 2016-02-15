import json
import re
import copy
from sw_utils.lang import param_get


class DeepDict:
    def __init__(self, *args, **kwargs):
        data = param_get(args, kwargs, 0, 'data', None)
        if data is not None:
            if getattr(data, '__class__', False):
                if data.__class__ == DeepDict:
                    self.data = copy.copy(data.data)
                else:
                    self.data = copy.copy(data)
            else:
                self.data = {}
        else:
            # dict = param_get(args, kwargs, 1, 'dict')
            # if True:
            #     pass
            # else:
            self.data = {}

    def children(self, ks=None):
        if ks is None:
            ks = []
        if getattr(ks, '__class__', False) and not(ks.__class__ == list or ks.__class__ == tuple):
            ks = [ks]
        e = self
        if not ks:
            try:
                return e.data['v']
            except KeyError:
                return []
        try:
            e = e.data['v'][ks[0]]
        except KeyError:
            return []
        return e.children(ks[1:])

    def node(self, ks):
        #ToDo: Los demas metodos recursivos es mejor que usen este y eviten la recursion...
        # es mas, de haber una funcion que retorna los hijos inmediatos seria mejor...
        if getattr(ks, '__class__', False) and not(ks.__class__ == list or ks.__class__ == tuple):
            ks = [ks]
        e = self
        if not ks:
            return e
        try:
            e = e.data['v'][ks[0]]
        except KeyError:
            return None
        return e.node(ks[1:])

    def get(self, ks, default=None):
        if getattr(ks, '__class__', False) and not(ks.__class__ == list or ks.__class__ == tuple):
            ks = [ks]
        e = self
        if not ks:
            try:
                value = e.data['a']
            except KeyError:
                value = default
            return value
        try:
            e = e.data['v'][ks[0]]
        except KeyError:
            return default
        return e.get(ks[1:])

    def set(self, ks, value):
        if getattr(ks, '__class__', False) and not(ks.__class__ == list or ks.__class__ == tuple):
            ks = [ks]
        e = self
        if not ks:
            if value is None:
                e.data.pop('a')
            else:
                e.data['a'] = value
            return
        try:
            es = e.data['v']
        except KeyError:
            if value is None:
                return
            e.data['v'] = {}
            es = e.data['v']
        try:
            e = es[ks[0]]
        except KeyError:
            es[ks[0]] = DeepDict()
            e = es[ks[0]]
        e.set(ks[1:], value)

    def remove(self, keys):
        # self.set(key, None)
        pass

    def keys(self):
        #retorna keys en toda su profundidad
        try:
            nodes = self.data['v']
        except KeyError:
            nodes = {}
        res = []
        for k, n in nodes.items():
            res.append([k])
            ks = n.keys()
            for kk in ks:
                res.append([k] + kk)
        return res

    def val_like(self, regex):
        """
        Retorna el primer valor like exp
        """
        sig = self.data
        while True:
            if re.match(regex, sig['a']):
                return DeepDict(sig)
            sig = self.data['v']
            if sig is {}:
                break

    def keys_where(self, filter_fun):
        """
        Retorna todos los primeros hijos del padre que matchean la key
        """
        nodes = []
        try:
            childs = self.data['v']
        except KeyError:
            return []
        for k in childs.keys():
            if filter_fun(k):
                nodes.append(DeepDict(childs[k]))
            else:
                more_nodes = childs[k].keys_where(filter_fun)
                nodes = reduce(lambda x,y: x + [y], more_nodes, nodes)
        return nodes

    # def flat(self):
    #     pass

    def __str__(self):
        return str(self.data)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getitem__(self, item):
        return self.get(item)

    def dict_2_object(self, simple_data):
        data = {}
        try:
            data['a'] = simple_data['a']
        except KeyError:
            pass
        try:
            raw_childs = simple_data['v']
            childs = {}
            for r_ch_k, r_ch_v in raw_childs.items():
                ch_k = r_ch_k
                ch = DeepDict()
                ch.dict_2_object(r_ch_v)
                childs[ch_k] = ch
            data['v'] = childs
        except KeyError:
            pass
        self.data = data

    def object_2_dict(self):
        raw_data = {}
        try:
            aggregate = self.data['a']
            raw_data['a'] = aggregate
        except KeyError:
            pass
        try:
            raw_childs = {}
            childs = self.data['v']
            for k, v in childs.items():
                vv = v.object_2_dict()
                raw_childs[k] = vv
            raw_data['v'] = raw_childs
        except KeyError:
            pass
        return raw_data

    def jsonize(self):
        dict_data = self.object_2_dict()
        res = json.dumps(dict_data)
        return res

    def dejsonize(self, raw_data):
        simple_data = json.loads(raw_data)
        self.dict_2_object(simple_data)

    serialize = jsonize

    deserialize = dejsonize


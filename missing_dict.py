# class MissingDict(dict):
#     """
#     Esta retorna otro MissingDict
#     """
#     def __missing__(self, key):
#         self[key] = rv = MissingDict()
#         return rv


class MissingDict(dict):
    """
    Deberia ademas borrar las entradas vacias...
    Puede ser Lazy ademas
    """
    def __init__(self, *args, **kwargs):
        d = dict.__init__(self, *args, **kwargs)

    def __missing__(self, key):
        self[key] = rv = {}
        return rv


class Dict_or_List(dict):
    """
    La idea es que se le pueda acceder tanto a indices numericos como strings, y si no existe que retorne None
    """



def lazy_dict(ks, value, entries):
    k, n_ks = ks[1], ks[1:]
    n_entries = entries[k]
    if n_ks:
        #recusion
        pass


def add_entry(ks, value, entries):
    k, n_ks = ks[1], ks[1:]
    n_entries = entries[k]
    if n_ks:
        #recusion
        pass
    entry = {}
    try:
        entries[k0][k1][k3] = []
    except KeyError:
        try:
            entry[k0][k1] = {}
            entry[k0][k1][k3] = []
        except KeyError:
            entry[k0] = {}
            entry[k0][k1] = {}
            entry[k0][k1][k3] = []

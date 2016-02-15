import re


def is_num(arg):
    tipo = type(arg)
    assert ((tipo == int) or (tipo == long) or (tipo == float))


def is_text(arg):
    tipo = type(arg)
    assert ((tipo == unicode) or (tipo == str))


def is_iterable(arg):
    tipo = type(arg)
    assert ((tipo == list) or (tipo == dict) or (tipo == tuple))


def is_ip(arg):
    is_text(arg)
    assert (re.match(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$', ip) is not None)


def is_email(arg):
    pass


def param_get(args, kwargs, index, key, default=None, optional=True):
    try:
        return args[index]
    except IndexError:
        try:
            return kwargs[key]
        except KeyError:
            if optional:
                return default
            else:
                raise


def params_group_get(args, kwargs, param_groups):
    params_result = []
    param_group_used = None
    param_group_used_id = -1
    more_args = args[:]
    more_kwargs = {}
    for (k,v) in kwargs.items():
        more_kwargs[k] = v
    param_group_id = -1
    for param_group in param_groups:
        param_group_id += 1
        try:
            for param in param_group:
                index = param[0]
                key = param[1]
                try:
                    optional = param[3]
                except IndexError:
                    optional = True
                try:
                    default = param[2]
                except IndexError:
                    default = None
                try:
                    params_result.append(args[index])
                except IndexError:
                    try:
                        params_result.append(kwargs[key])
                    except KeyError:
                        if optional:
                            params_result.append(default)
                        else:
                            raise
            param_group_used = param_group
            param_group_used_id = param_group_id
            for param in param_group:
                index = param[0]
                key = param[1]
                more_args.pop(index)
                more_kwargs.pop(key)
        except KeyError:
            pass
    return more_args, more_kwargs, param_group_used, param_group_used_id, params_result


class objectview(object):
    def __init__(self, d):
        self.__dict__ = d


def enum(*sequential, **named):
    """
Enumerador que provee una funcionalidad similar a la encontrada en Java o C#
Uso:
>> Numbers = enum('ZERO', 'ONE', 'TWO')
>> Numbers.ZERO
1

Numbers = enum(ONE=1, TWO=2, THREE='three')
    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


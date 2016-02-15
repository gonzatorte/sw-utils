

#Es una clase dummy que no revienta sin importar lo que se le haga, pero nunca hace nada
class DummyObj(object):
    def __abs__(self):
        return self

    def __add__(self, other):
        return self

    def __call__(self, *args, **kwargs):
        return self

    def __coerce__(self, other):
        return None

    def __complex__(self):
        return self

    def __contains__(self, item):
        return self

    def __del__(self):
        return self

    def __delattr__(self, item):
        return self

    def __delete__(self, instance):
        return self

    def __delitem__(self, key):
        return self

    def __delslice__(self, i, j):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self

    def __float__(self):
        return self

    def __floordiv__(self, other):
        return self

    def __get__(self, instance, owner):
        return self

    def __getattr__(self, item):
        return self

    def __getitem__(self, item):
        return self

    def __hash__(self):
        return self

    def __hex__(self):
        return self

    def __init__(self, *args, **kwargs):
        pass

    def __iadd__(self, other):
        return self

    def __iand__(self, other):
        return self

    def __idiv__(self, other):
        return self

    def __ifloordiv__(self, other):
        return self

    def __ilshift__(self, other):
        return self

    def __imod__(self, other):
        return self

    def __imul__(self, other):
        return self

    def __index__(self):
        return self

    def __int__(self):
        return self

    def __invert__(self):
        return self

    def __ipow__(self, other):
        return self

    def __isub__(self, other):
        return self

    def __irshift__(self, other):
        return self

    def __itruediv__(self, other):
        return self

    def __iter__(self):
        return self

    def __len__(self):
        return self

    def __long__(self):
        return self

    def __lshift__(self, other):
        return self

    def __mod__(self, other):
        return self

    def __mul__(self, other):
        return self



    def __cmp__(self, other):
        return self

    def __le__(self, other):
        return self

    def __eq__(self, other):
        return self

    def __ne__(self, other):
        return self

    def __lt__(self, other):
        return self

    def __ge__(self, other):
        return False

    def __gt__(self, other):
        return False

    def __and__(self, other):
        return self

    def __ixor__(self, other):
        return self

    def __ior__(self, other):
        return self

    def __or__(self, other):
        return self

    def __xor__(self, other):
        return self

    def __rxor__(self, other):
        return self

    def __ror__(self, other):
        return self

    def __rand__(self, other):
        return self

    def __neg__(self):
        return self

    def __nonzero__(self):
        return False



    def __oct__(self):
        return self

    def __pos__(self):
        return self

    def __pow__(self, power, modulo=None):
        return self

    def __radd__(self, other):
        return self

    def __rdiv__(self, other):
        return self

    def __rdivmod__(self, other):
        return self

    def __reversed__(self):
        return self

    def __rfloordiv__(self, other):
        return self

    def __rlshift__(self, other):
        return self

    def __rmod__(self, other):
        return self

    def __rmul__(self, other):
        return self

    def __rpow__(self, power, modulo=None):
        return self

    def __rrshift__(self, other):
        return self

    def __rshift__(self, other):
        return self

    def __rsub__(self, other):
        return self

    def __rtruediv__(self, other):
        return self

    def __truediv__(self, other):
        return self

    def __unicode__(self):
        return self

    # def __reduce__(self, *args, **kwargs):
    #     pass

    # def __reduce_ex__(self, *args, **kwargs): # real signature unknown
    #     pass

    # def __sizeof__(self):
    #     return self

    # def __repr__(self):
        # return self
        # return "DUMMY OBJ"

    # def __str__(self):
        # return self
        # return "DUMMY OBJ"

    # def __format__(self):
        # return self

    # def __new__(cls, *args, **kwargs):
    #     return self

    # @classmethod # known case
    # def __subclasshook__(cls, subclass): # known special case of object.__subclasshook__
    #     """
    #     Abstract classes can override this to customize issubclass().
    #
    #     This is invoked early on by abc.ABCMeta.__subclasscheck__().
    #     It should return True, False or NotImplemented.  If it returns
    #     NotImplemented, the normal algorithm is used.  Otherwise, it
    #     overrides the normal algorithm (and the outcome is cached).
    #     """
    #     pass

    # __class__ = None # (!) forward: type, real value is ''
    # __dict__ = {}
    # __doc__ = ''
    # __module__ = ''

    # def __getattribute__(self, name): # real signature unknown; restored from __doc__
    #     """ x.__getattribute__('name') <==> x.name """
    #     pass
    #     return self

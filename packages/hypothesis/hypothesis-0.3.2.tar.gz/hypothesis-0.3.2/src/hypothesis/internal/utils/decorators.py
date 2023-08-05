from functools import wraps


def memoized(f):
    dict_name = "__%s" % (f.__name__,)

    @wraps(f)
    def inner(self, x):
        try:
            table = getattr(self, dict_name)
        except AttributeError:
            table = {}
            setattr(self, dict_name, table)
        try:
            return table[x]
        except KeyError:
            pass
        result = f(self, x)
        table[x] = result
        return result

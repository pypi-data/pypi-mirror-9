from functools import wraps

from .base import ParameterSet


def inject_params(fun):
    @wraps(fun)
    def wrapped(*a, **kw):
        names = fun.func_code.co_varnames
        dct = dict()
        psets = list()
        for (name, ai) in zip(names, a):
            if isinstance(ai, ParameterSet):
                dds.append(ai)
            else:
                dct[name] = ai
        for dd in dds:
            dct.update(dd.as_dict())
        dct.update(kw)
        return fun(**dct)
    return wrapped


from functools import wraps


def lazy(func):
    cache = {}

    @wraps(func)
    def wrap(*args, **kwargs):
        key = (args, tuple(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]

    return wrap


def lazy_property(func):
    canary = object()

    prop_name = '_prop_' + func.func_name

    @property
    @wraps(func)
    def wrap(self, *args, **kwargs):
        value = getattr(self, prop_name, canary)
        if value is canary:
            value = func(self, *args, **kwargs)
            setattr(self, prop_name, value)

        return value

    return wrap

# -*- coding:utf-8 -*-
import logging
from functools import wraps
from singledispatch import singledispatch
from collections import ChainMap
from django.db import models
from django.db.models.base import ModelBase
logger = logging.getLogger(__name__)


class MappingManager(object):
    def __init__(self, default="", reserved_words=["doc"]):
        self.mapping = {}
        self.deafult = default
        self.reserved_words = self.setup_reserved_words({}, reserved_words, default)
        self.marker = object()

    def setup_reserved_words(self, D, candidates, default):
        for c in candidates:
            if isinstance(c, (list, tuple)):
                D[c[0]] = c[1]
            else:
                D[c] = default
        return D

    def add_reserved_words(self, *args, **ws):
        self.reserved_words = self.setup_reserved_words(self.reserved_words, args, self.default)
        self.reserved_words = self.setup_reserved_words(self.reserved_words, ws, self.default)

    def get(self, k, default=None):
        try:
            return self.mapping[k]
        except KeyError:
            return default

    def __getitem__(self, k):
        return self.mapping[k]

    def __setitem__(self, k, v):
        self.mapping[k] = v

    def register(self, fn):
        logger.debug("register %s.%s", fn.__module__, fn.__name__)
        wrapped = self.wrapper(fn)
        setattr(self, fn.__name__, wrapped)
        return wrapped

    def wrapper(self, fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            options = {}
            for k, default in self.reserved_words.items():
                v = kwargs.pop(k, default)
                options[k] = v
            result = fn(*args, **kwargs)
            self.mapping[result] = options
            return result
        return wrapped

default_mapping = MappingManager()


def get_default_mapping():
    global default_mapping
    return default_mapping


def set_default_mapping(mapping):
    global default_mapping
    default_mapping = mapping


@singledispatch
def get_mapping(ob, mapping=None):
    # ob.foo_set
    if hasattr(ob, "model"):
        return get_mapping(ob.model, mapping)
    return {}


@get_mapping.register(models.Field)
def mapping__field(field, mapping=None):
    mapping = mapping or get_default_mapping()
    return ChainMap({}, mapping.get(field) or mapping.reserved_words)


@get_mapping.register(ModelBase)
def mapping__modelclass(model, mapping=None):
    mapping = mapping or get_default_mapping()
    try:
        return ChainMap({}, mapping[model])
    except KeyError:
        result = {f.name: get_mapping(f, mapping=mapping) for f in model._meta.fields}
        mapping[model] = result
        return ChainMap({}, result)


@get_mapping.register(models.Model)
def mapping__model(ob, mapping=None):
    mapping = mapping or get_default_mapping()
    try:
        return ChainMap({}, mapping[ob.__class__])
    except KeyError:
        result = {f.name: get_mapping(f, mapping=mapping) for f in ob._meta.fields}
        mapping[ob.__class__] = result
        return ChainMap({}, result)


def setup(mapping, callback=None):
    for k, v in models.__dict__.items():
        if isinstance(v, type) and issubclass(v, models.Field):
            registered = mapping.register(v)
            if callback:
                callback(k, registered)

if __name__ != "__main__":
    import sys
    from django.db import models
    m = sys.modules[__name__]

    def callback(k, registered):
        setattr(m, k, registered)

    setup(default_mapping, callback=callback)

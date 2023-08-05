from copy import copy

import six

from dtotools.field import Field

FIELDS = '_fields'


class DtoType(type):
    def __new__(meta, name, bases, attrs):
        meta._name_fields(attrs)
        meta._set_fields(bases, attrs)
        return super(DtoType, meta).__new__(DtoType, name, bases, attrs)

    @classmethod
    def _name_fields(meta, attrs):
        for k, v in tuple(six.iteritems(attrs)):
            if not isinstance(v, Field):
                continue
            f = copy(v)
            f.set_name(k)
            attrs[k] = f

    @classmethod
    def _set_fields(meta, bases, attrs):
        fields = set(attrs.get(FIELDS, ()))
        for b in bases[::-1]:
            fields.update(getattr(b, FIELDS, ()))
        for k, v in attrs.items():
            if isinstance(v, Field):
                fields.add(k)
        attrs[FIELDS] = tuple(fields)

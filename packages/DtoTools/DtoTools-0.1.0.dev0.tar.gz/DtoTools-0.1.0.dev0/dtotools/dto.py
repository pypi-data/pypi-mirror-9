import six

from dtotools.dto_type import DtoType


class Dto(six.with_metaclass(DtoType)):
    def __init__(self, **kwargs):
        for k, v in six.iteritems(kwargs):
            setattr(self, k, v)

    def __setattr__(self, attr, value):
        if not attr.startswith('_') and attr not in self._fields:
            raise AttributeError("Can't set attribute %r" % attr)
        super(Dto, self).__setattr__(attr, value)

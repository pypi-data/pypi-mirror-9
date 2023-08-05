import six

from dtotools.dto_type import DtoType


class Dto(six.with_metaclass(DtoType)):
    def __init__(self, **kwargs):
        for k, v in six.iteritems(kwargs):
            setattr(self, k, v)

    def __setattr__(self, attr, value):
        if not _is_private(attr) and attr not in self._fields:
            raise AttributeError("Can't set attribute %r" % attr)
        super(Dto, self).__setattr__(attr, value)

    def __getstate__(self):
        state = {}
        for k, v in six.iteritems(self.__dict__):
            if k in self._fields:
                state[k] = v
        return state


def _is_private(attr):
    return attr.startswith('_')

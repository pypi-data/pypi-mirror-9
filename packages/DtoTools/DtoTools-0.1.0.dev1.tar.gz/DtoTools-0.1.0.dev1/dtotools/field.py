class Field(object):
    type = object
    name = None

    def __init__(self, type=None):
        if type is not None:
            self.type = type

    def set_name(self, name):
        self.name = name

    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        return self.get(obj)

    def __set__(self, obj, value):
        self.validate(value)
        obj.__dict__[self.name] = value

    def get(self, obj):
        try:
            return obj.__dict__[self.name]
        except KeyError:
            raise AttributeError(self.name)

    def validate_type(self, value):
        if not isinstance(value, self.type):
            raise TypeError(
                '%(value)r is not an instance of %(type)r' % {
                    'value': value,
                    'type': self.type,
                }
            )

    def validate(self, value):
        self.validate_type(value)

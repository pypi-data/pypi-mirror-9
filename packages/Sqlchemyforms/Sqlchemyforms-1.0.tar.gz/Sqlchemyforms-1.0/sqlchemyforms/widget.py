
from tools import Storage
from abc import abstractmethod

class Widget(Storage):
    def __init__(self, name, type, value = None, required = False, default = None):
        self.name = name
        self.type = type
        self.value = value
        self.value_type = ''
        self.required = required
        self.default = default
        self.regexp = None
        self.error_message = None
        self.iterable = ['name', 'type', 'value', 'value_type', 'required', 'default', 'regexp', 'error_message']

    def validate(self):
        return self.field.validate(self.value)

    def __iter__(self):
        for field in self.iterable:
            yield field

    def __repr__(self):
        return "<Widget(name=%(name)s, type=%(type)s, value=%(value)s)>" % self

class SelectWidget(Widget):
    html_type = 'select'

    def __init__(self, *args, **kwargs):
        super(SelectWidget, self).__init__(*args, **kwargs)
        self.multiple = False
        self.options = None
        self.iterable.extend(['multiple', 'options'])

    def __repr__(self):
        return "<SelectWidget(name=%(name)s, type=%(type)s, value=%(value)s, options=%(options)s, multiple=%(multiple)r)>" % self

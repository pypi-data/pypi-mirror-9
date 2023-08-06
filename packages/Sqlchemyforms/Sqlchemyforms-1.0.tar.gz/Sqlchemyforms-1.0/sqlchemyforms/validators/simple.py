
from abc import abstractmethod
import re

class SimpleValidator(object):

    # with these values, easy to serialize html forms to json object with this: https://github.com/marioizquierdo/jquery.serializeJSON
    value_type_map = dict(
        integer = 'number',
        checkbox = 'boolean',
        text = 'string'
    )

    def __init__(self, type, regexp = None, error_message = None):
        self.type = type
        self.regexp = regexp
        self.error_message = error_message

    @abstractmethod
    def check(self, value):
        if value is None:
            return ''

        if self.type is 'integer' and not isinstance(value, (int, long)):
            return 'value (%s) is not integer' % value

        if self.regexp:
            if not re.match(self.regexp, value):
                return self.error_message

        return ''

    @abstractmethod
    def process_widget(self, widget, db):
        widget.value_type = self.value_type_map[self.type] if self.type in self.value_type_map else 'string'
        widget.regexp = self.regexp
        widget.error_message = self.error_message

    def format_value(self, value, field_type):
        return value


class URLValidator(SimpleValidator):

    def __init__(self):
        super(URLValidator, self).__init__('text', 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 'bad_url')
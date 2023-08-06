
import sqlalchemy

from widget import Widget, SelectWidget
from validators.simple import SimpleValidator
from validators.is_in_set import IsInSetValidator

from copy import copy

class WidgetFactory(object):

    def __init__(self):
        self.__basic_field_types = {
            sqlalchemy.Integer: 'integer',
            sqlalchemy.String: 'text',
            sqlalchemy.Text: 'text',
            sqlalchemy.DateTime: 'datetime',
            sqlalchemy.Boolean: 'checkbox',
            sqlalchemy.Enum: self.__get_enum_widget_info
        }

    def __get_enum_widget_info(self, field):
        field.validators.append(IsInSetValidator({val:val for val in field.type.type.enums}))
        return SelectWidget, 'select'

    def gen_for_basic_types(self, field):
        orm_type = type(field.type.type)

        html_type = self.__basic_field_types[orm_type] if orm_type in self.__basic_field_types else 'text'

        if hasattr(html_type, '__call__'):
            return html_type(field)

        field.validators.append(SimpleValidator(html_type))

        return Widget, html_type

    def generate(self, instance, form_field_definitions, db, fields_to_gen = []):

        widgets = {}

        for field in form_field_definitions:

            attr = field.type
            name = attr.key

            if len(fields_to_gen) and name not in fields_to_gen:
                continue

            if not hasattr(field, 'html_type'):
                widget_type = Widget
                html_type = 'text'

                # try guessing widget type by validators
                for validator in field.validators:
                    if hasattr(validator, 'widget_type'):
                        widget_type = validator.widget_type
                        break

                if hasattr(widget_type, 'html_type'):
                    html_type = widget_type.html_type

                # create validator if there is no one
                if not len(field.validators):
                    widget_type, html_type = self.gen_for_basic_types(field)

                if hasattr(attr, 'primary_key') and attr.primary_key:
                    html_type = 'hidden'

                field.html_type = html_type
                field.widget_type = widget_type

            # get value from model instance
            value = getattr(instance, name)

            default = None
            required = False

            if hasattr(attr, 'nullable'):
                required = not getattr(attr, 'nullable')

            if hasattr(attr, 'default'):
                default = getattr(attr, 'default')
                if default:
                    default = default.arg

            widget = field.widget_type(name, field.html_type, value, required = required, default = default )
            widget.field = field

            for validator in field.validators:
                validator.process_widget(widget, db)

            widgets[name] = widget

        return widgets

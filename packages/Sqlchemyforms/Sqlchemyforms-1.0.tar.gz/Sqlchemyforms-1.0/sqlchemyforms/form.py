
from tools import Storage
from widget_factory import WidgetFactory

class Form(Storage):

    widget_factory = WidgetFactory()

    def __init__(self,
                 model,
                 db,
                 action,
                 method = 'POST',
                 fields = [],
                 name = None):
        self.model = model
        self.db = db
        self.action = action
        self.method = method
        self.fields = fields
        self.name = name or str(model.__table__)
        self.errors = {}
        self.accepted = False

        self.widgets = {}
        self.iterables = ['name', 'action', 'method', 'widgets', 'errors', 'accepted']

    def __iter__(self):
        for field in self.iterables:
            yield field

    # refactor out
    def search_primary_key(self):
        for field in self.model.form_field_definitions:
            if hasattr(field.type, 'primary_key') and field.type.primary_key:
                return field.type
        return None

    def generate_widgets(self, instance):
        self.widgets = self.widget_factory.generate(instance, self.model.form_field_definitions, self.db, self.fields)

    def accept(self, data, instance):
        self.generate_widgets(instance)

        if data is None:
            return False

        data_fields = []

        for name in self.widgets:
            if name in data:
                data_fields.append(name)

        if not len(data_fields):
            return False

        changed_fields = []

        for name in data_fields:
            widget = self.widgets[name]

            # validate
            widget.value = data[name]
            errors = widget.validate()
            if len(errors):
                self.errors[name] = errors

            # check change
            value = getattr(instance, name)
            if value != widget.value:
                changed_fields.append(name)

        if len(self.errors):
            return False

        # update instance
        for name in data_fields:
            field = self.widgets[name].field
            value = field.format_value(data[name])
            setattr(instance, name, value)

        self.db.add(instance)

        primary_key = self.search_primary_key()

        if getattr(instance, primary_key.key) is None:
            self.db.flush()
            self.widgets[primary_key.key].value = getattr(instance, primary_key.key)

        self.accepted = True

        return True

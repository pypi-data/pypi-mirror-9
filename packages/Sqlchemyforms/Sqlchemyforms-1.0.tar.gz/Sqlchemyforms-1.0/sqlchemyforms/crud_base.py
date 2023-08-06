
from exceptions import CrudException
from form import Form
from table.data_table import DataTable
from sqlchemyforms.tools import Storage

class CrudRequest(object):
    def __init__(self, path, get, post, query, db):
        self.path = path
        self.get = get
        self.post = post
        self.query = query
        self.db = db

class CrudBase(object):
    def __init__(self, model):
        self.model = model

    def search_primary_key(self):
        for field in self.model.form_field_definitions:
            if hasattr(field.type, 'primary_key') and field.type.primary_key:
                return field.type
        return None

    def __fetch_instance(self, request):
        primary_key_def = self.search_primary_key()

        if primary_key_def.key not in request.get:
            raise CrudException('%s is missing' % primary_key_def.key, 404)

        primary_value = request.get[primary_key_def.key][0]

        instance = request.db.query(self.model).filter_by(**{primary_key_def.key: primary_value}).first()

        if instance is None:
            raise CrudException('%s not found' % self.model, 404)

        return instance

    def call(self, request, command):
        func = getattr(self, command)

        result = func(request)

        success = True
        if type(result) is tuple:
            data = result[0]
            success = result[1]
        else:
            data = result

        return Storage(
            method = command,
            table = str(self.model.__table__),
            data = data,
            primary_key = self.search_primary_key().key,
            success = success,
        )

    def do_create(self, request):
        instance = self.model()

        form = Form(self.model, request.db, '%s?%s' % (request.path, request.query))

        res = form.accept(request.post, instance)

        return (form, res)

    def do_read(self, request):

        return self.__fetch_instance(request)

    def do_update(self, request):

        instance = self.__fetch_instance(request)

        form = Form(self.model, request.db, '%s?%s' % (request.path, request.query))

        res = form.accept(request.post, instance)

        return (form, res)

    def do_delete(self, request):

        instance = self.__fetch_instance(request)

        if request.post is not None:
            request.db.delete(instance)

        return True

    def do_list(self, request):

        t = DataTable(self, request)

        return t.fetch()


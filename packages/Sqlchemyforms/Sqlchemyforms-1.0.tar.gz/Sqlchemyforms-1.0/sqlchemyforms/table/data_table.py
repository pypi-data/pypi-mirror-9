
from sqlchemyforms.tools import Storage

class DataTable(object):
    def __init__(self, crud, request):
        self.crud = crud
        self.model = crud.model
        self.request = request

    def get_sorting_expression(self, result):
        sort = self.crud.search_primary_key()
        dir = 'asc'

        if self.model.table_definitions.sorting_defaults:
            sort = self.model.table_definitions.sorting_defaults.key
            dir = self.model.table_definitions.sorting_defaults.dir

        if 'sort' in self.request.get:
            gsort = self.request.get['sort'][0]
            if gsort in self.sortable_fields:
                sort = self.sortable_fields[gsort]

        if 'dir' in self.request.get:
            gdir = self.request.get['dir'][0]
            if gdir in ['asc', 'desc']:
                dir = gdir

        result.sort = sort.key
        result.dir = dir

        if dir == 'asc':
            return sort
        else:
            return sort.desc()

    def get_page_expression(self):
        rpp = self.model.table_definitions.row_per_page or 20
        page = 1

        if 'page' in self.request.get:
            page = int(self.request.get['page'])

    def fetch(self):
        result = Storage(
            columns = {},
            rows = [],
        )

        self.sortable_fields = {}
        self.filterable_fields = {}

        for col in self.model.table_definitions.columns:
            result.columns[col.type.key] = dict(
                name = col.type.key,
                sortable = col.sortable
            )
            if col.sortable:
                self.sortable_fields[col.type.key] = col.type

        order = self.get_sorting_expression(result)

        data = self.request.db.query(self.model).order_by(order)

        for instance in data:
            result.rows.append({col.type.key: col.fetch(getattr(instance, col.type.key)) for col in self.model.table_definitions.columns})

        return result
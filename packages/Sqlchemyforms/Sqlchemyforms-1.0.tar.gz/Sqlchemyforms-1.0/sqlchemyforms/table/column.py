
class Column(object):
    def __init__(self, type, sortable = True, fetcher = None):
        self.type = type
        self.sortable = sortable
        self.fetcher = fetcher

    def fetch(self, value):
        if self.fetcher:
            value = self.fetcher(value)
        return value



from json import JSONEncoder as orig_encoder

class JSONEncoder(orig_encoder):
    """
        Encode a lots of types data, what are seems to be iterable
        Also have a custom circular referencing avoiding mechanism, because of the SqlAlchemy's orm classes may have backref or sg
    """
    def __init__(self, *args, **kwargs):
        kwargs['check_circular'] = False
        super(JSONEncoder, self).__init__(*args, **kwargs)
        self._visited = []

    def default(self, o):
        if o in self._visited:
            return '[...]'
        self._visited.append(o)

        if hasattr(o, '__iter__'):
            return dict(o)

        if hasattr(o, '__dict__'):
            return o.__dict__

        return str(o)


# FIXME: move to the right place...!  (maybe sg like CompositeWidget...)
def check_composite_widget_struct(value, required):

    if type(value) is not dict or type(required) is not dict:
        return False

    def check_node(val_node, req_node):
        for key in req_node:
            if key not in val_node:
                return False

            if type(val_node[key]) is dict:
                if type(req_node[key]) is not dict:
                    return False

                if not check_node(val_node[key], req_node[key]):
                    return False

            elif type(val_node[key]) is not req_node[key]:
                return False

        return True

    return check_node(value, required)


class Storage(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __hasattr__(self, key):
        return key in self

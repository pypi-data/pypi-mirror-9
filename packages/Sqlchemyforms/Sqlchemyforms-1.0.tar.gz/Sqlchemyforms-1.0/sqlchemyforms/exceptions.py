

class FormException(Exception):
	pass


class CrudException(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code

    def __str__(self):
        return "%s - %d" % (self.message, self.code)

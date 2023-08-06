

class Field(object):
    def __init__(self, type, validators = None):
        self.type = type
        """
            Q: Why the default param is [] for validators In the function list?
            A: 'cause some weird python shit in all the Field instance created without validator the instance of the validator member will be the _same_
        """
        self.validators = validators if validators else []

    def format_value(self, value):
        for validator in self.validators:
            value = validator.format_value(value, self.type)

        return value

    def validate(self, value):
        errors = []

        for validator in self.validators:
            res = validator.check(value)
            if len(res):
                errors.append(res)

        return errors
class SMSFieldException(Exception):

    def __init__(self, field):
        self.field = field

    def __str__(self):
        return repr(self.field)


class MissingRequiredFieldException(SMSFieldException):

    def __str__(self):
        return "The {required_field} is missing but is required.".format(
            required_field=self.field
        )


class InvalidDateException(SMSFieldException):
    pass


class ChoiceException(SMSFieldException):
    pass

class DuplicateFieldsException(SMSFieldException):
    def __str__(self):
        return "Duplicate fields detected: {fields}".format(
            fields=",".join(self.field))

class UnrecognizedDataFoundException(SMSFieldException):
    def __str__(self):
        return "Unrecognized or duplicate data found: '{field}'. Please remove it before submitting the SMS".format(field=self.field)

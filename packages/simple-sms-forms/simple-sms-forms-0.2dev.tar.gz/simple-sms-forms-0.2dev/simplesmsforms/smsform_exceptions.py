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
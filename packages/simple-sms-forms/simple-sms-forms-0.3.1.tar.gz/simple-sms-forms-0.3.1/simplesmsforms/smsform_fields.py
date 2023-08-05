import datetime

from smsform_exceptions import (SMSFieldException, ChoiceException, InvalidDateException,
                                MissingRequiredFieldException, DuplicateFieldsException)
from smsform_validators import single_choice_validator, multiple_choice_validator,multiple_choice_duplicate_validator, standard_duplicate_validator
# SMS FIELD


class GenericSMSField(object):
    """This is the base class of all fields"""
    empty_values = [None, [], ""]


    def __init__(self, name, **kwargs):
        self.name = name
        self.validators = kwargs.get('validators') or []
        self.prefixes = kwargs.get("prefixes") or [""]
        self.prefixes.sort(key=len, reverse=True)#Longest prefix should be first
        self.accepted_prefix = ""
        self.allow_multiple = False
        self.accepted_raw_field_text = ""
        self.raw_form_text = ""

        required = kwargs.get("required", "blank")
        if required == "blank":
            self.required = True
        else:
            self.required = False


    def get_field_regex(self):
        """Return a dict of 'prefix':prefix and regex:regex"""
        prefix_regexes = []
        for prefix in self.prefixes:
            prefix_regex = r"\b{prefix}(?P<{name}>\w*)".format(
                prefix=prefix,
                name=self.name
            )
            prefix_regexes.append({"prefix": prefix, "regex": prefix_regex})
        return prefix_regexes

    def get_verbose_name(self):
        """Return a good looking name for the field."""
        name_parts = self.name.split("_")
        return " ".join(name_parts).title()

    def to_python(self, text, accepted_prefix=""):
        """Convert the passed in text to a valid python object, any special
        conversions from the passed in text to a valid python object should
        happen here."""
        self.accepted_prefix = self.accepted_prefix or accepted_prefix

        return text, accepted_prefix

    def validate(self, value):
        """Run all field validation"""
        # check to see if the field is required and present
        if self.required and value in self.empty_values:
            raise MissingRequiredFieldException(self.get_verbose_name())

        #Run the standard validator
        standard_duplicate_validator(actual_field=self, value=value)
        for validator in self.validators:
            try:
                validator(value=value)
            except SMSFieldException, e:
                raise
        return True

    def process_field(self, text, accepted_prefix=""):
        """Entry point for all field processing"""
        #add the recognized text before any further processing is done.
        self.accepted_raw_field_text = text
        # Try to split into text and the accepted prefix
        python_obj, accepted_prefix = self.to_python(text, accepted_prefix)
        #try to catch duplicates
        self.validate(python_obj)
        return python_obj

    def __repr__(self):
        return "<{name}> object".format(name=self.name)

# SMSFields
class PrefixField(GenericSMSField):

    """This field is for the special fields that have a first letter followed by
    the actual data. This class just strips out that first letter"""

    pass


class MultiChoiceField(GenericSMSField):
    """MultiChoiceField will be used to take in a selection from some choices
    and will validate that the selectons are part the options"""

    def __init__(self, choices, choice_divider=",", *args, **kwargs):
        self.choice_divider = choice_divider
        self.choices = choices
        super(MultiChoiceField, self).__init__(*args, **kwargs)
        self.validators.extend([
            multiple_choice_validator,
            multiple_choice_duplicate_validator])

    def to_python(self, text, accepted_prefix=""):
        text, accepted_prefix = super(
            MultiChoiceField, self).to_python(text, accepted_prefix)

        return text.split(self.choice_divider), accepted_prefix

    def get_field_regex(self):
        choices_string = "|".join(self.choices)
        return [
            {
                "prefix": "", "regex": "({choices_string})".format(
                    choices_string=choices_string)
            }
        ]

    def validate(self, value):
        # check to see if the field is required and present
        if self.required and value in self.empty_values:
            raise MissingRequiredFieldException(self.get_verbose_name())

        for validator in self.validators:
            try:
                validator(field=self, value=value, choices=self.choices)
            except SMSFieldException, e:
                raise
        return True

class SingleChoiceField(MultiChoiceField):
    """Will validate that a single choice is selected from some options"""

    def __init__(self, choices, *args, **kwargs):
        super(SingleChoiceField, self).__init__(choices, *args, **kwargs)
        self.validators = [single_choice_validator]


class DateField(GenericSMSField):
    """Date field will process dates that are input on the text form"""

    def __init__(self, name, *args, **kwargs):
        date_formats = kwargs.get("date_formats", None) or ["%d/%b/%y", "%d%b%y"]
        super(DateField, self).__init__(name, *args, **kwargs)
        self.date_formats = date_formats

    def get_field_regex(self):
        """We will accept 2 formats for the dates: dayMonthYear, day/Month/Year
            with the month acceptable as a word or digits
        """
        regex_strings = [
            r"\b\d{1,2}[-/]\d{1,2}[-/]\d{1,4}\b",
            r"\b\d{1,2}[a-z]{3,14}\d{1,4}\b",
        ]
        return [
            {
                "prefix": "", "regex": "{regex_strings}".format(
                    regex_strings="|".join(regex_strings), name=self.name)
            }
        ]

    def to_python(self, date_string, accepted_prefix=""):
        python_date = None
        for date_format in self.date_formats:
            try:
                python_date = datetime.datetime.strptime(
                    date_string, date_format)
            except ValueError:
                continue
            else:
                break

        if not python_date:
            raise InvalidDateException(
                "Date not recognized, please use the format: dayMonthYear"
            )

        return python_date.date(), accepted_prefix

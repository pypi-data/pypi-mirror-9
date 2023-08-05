from smsform_exceptions import (ChoiceException, InvalidDateException,
    MissingRequiredFieldException, DuplicateFieldsException, UnrecognizedDataFoundException)

import re
from smsform import to_string

"""Validators should have a simple signature accepting any number of arguments
to make processing them easier"""

class LowerCaseException(Exception):
    pass

def lowercase_list_util(value_list):
    try:
        return [value.lower() for value in value_list]
    except AttributeError:
        raise LowerCaseException("%s can not be lower cased"%value_list)

def multiple_choice_validator(**kwargs):
    """Takes a single value or a list of values and validates that they are all
    part of a set of choices"""
    value = set(lowercase_list_util(kwargs["value"]))
    choices = set(lowercase_list_util(kwargs["choices"]))
    if not value.issubset(choices):
        raise ChoiceException("Invalid option '{value}', please select one of: {choices_string}".format(
                value=", ".join(value),
                choices_string=", ".join(choices)))

def single_choice_validator(*args, **kwargs):
    """Takes a value and validates that it is atleast one of some number of
    variables"""
    multiple_choice_validator(*args, **kwargs)

    value = kwargs.get("value")
    choices = kwargs.get("choices")
    if len(value) > 1:
        raise ChoiceException("Please select only one value out of {choices_string}".format(
            choices_string=", ".join(choices)))

def standard_duplicate_validator(**kwargs):
    """Standard duplicate validator will make sure a field
    is not given multiple times."""

    field = kwargs.get('value')
    actual_field = kwargs.get('actual_field')
    field_regexes = actual_field.get_field_regex()
    accepted_raw_field_text = actual_field.accepted_raw_field_text
    raw_form_text = actual_field.raw_form_text
    accepted_prefix = actual_field.accepted_prefix
    if len(accepted_raw_field_text.split(",")) > 1:
        raise DuplicateFieldsException(actual_field.get_verbose_name())

    #remove the detected text from the full form
    modified_form_text = raw_form_text
    if accepted_prefix:
        modified_form_text = re.sub(
            accepted_prefix,
            repl="",
            string=modified_form_text,
            flags=re.IGNORECASE)
    if accepted_raw_field_text:
        modified_form_text = re.sub(
            accepted_raw_field_text,
            repl="",
            string=modified_form_text,
            flags=re.IGNORECASE)

    for prefix_regex in field_regexes:
        regex = re.compile(prefix_regex['regex'], re.IGNORECASE)
        match = regex.findall(modified_form_text)
        if match:
            raise DuplicateFieldsException(actual_field.get_verbose_name())

def multiple_choice_duplicate_validator(*args, **kwargs):
    actual_field = kwargs.get('field')
    field = to_string(kwargs.get('value'))
    field_set = field.split(',')
    duplicates = []
    for item in set(field_set):
        if field_set.count(item) > 1:
            duplicates.append(item)

    if duplicates:
        raise DuplicateFieldsException(actual_field.get_verbose_name())

def reject_garbage_data(form_keyword, raw_text_string, bound_fields_dict):
    """This method will look for all unrecognized fields in the text and return them"""
    """The implementation currently will also find duplicate fields as unrecognized data"""
    #We remove all the recognized fields and the form keyword, whatever remains is extra-unrecognised data.
    modified_raw_text = raw_text_string
    for field in bound_fields_dict:
        for prefix_regex in field.get_field_regex():
            prefix = prefix_regex['prefix']
            regex = prefix_regex['regex']

            modified_raw_text = re.sub(regex, repl=" ", string=modified_raw_text, flags=re.IGNORECASE)

            if prefix:
                prefix_reg = r'\b{prefix}'.format(prefix=prefix)
                modified_raw_text = re.sub(prefix_reg, repl=" ", string=modified_raw_text, flags=re.IGNORECASE)
    #Remove the form keyword.
    modified_raw_text = re.sub(form_keyword, repl="", string=modified_raw_text, flags=re.IGNORECASE)
    #Remove all non-alphanumeric characters
    modified_raw_text = re.sub('([\W_^\s])', ' ', modified_raw_text, flags=re.IGNORECASE)

    if modified_raw_text.strip():
        raise UnrecognizedDataFoundException(modified_raw_text.strip())



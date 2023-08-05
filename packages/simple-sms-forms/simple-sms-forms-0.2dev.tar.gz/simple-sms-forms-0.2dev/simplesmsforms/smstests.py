import re
import datetime
import unittest
from smsform_fields import (GenericSMSField, PrefixField, SingleChoiceField,
                            MultiChoiceField, DateField)
from smsform_exceptions import (ChoiceException, InvalidDateException,
                                MissingRequiredFieldException)
from smsform import SMSForm


class PersonForm(SMSForm):
    keyword = "REG"
    blank_field = "_"

    first_name = PrefixField(prefixes=["fn"], name="first_name")
    last_name = PrefixField(prefixes=["ln"], name="last_name")
    age = PrefixField(prefixes=["ag"], name="age")
    location = PrefixField(prefixes=["loc"], name="location")
    date = DateField(prefixes=["dt"], name="date", required=False)

    def get_fields(self):
        return [self.first_name, self.last_name, self.age, self.location, self.date]

# Create your tests here.


class TestSMSForms(unittest.TestCase):

    def setUp(self):
        self.person_form = PersonForm()
        self.person_form.original_text = "REG fnAndre lnLesa ag12 locLusaka"
        self.expected_bound_fields =  (
            (self.person_form.first_name, ("fn", "Andre")),
            (self.person_form.last_name,  ("ln", "Lesa")),
            (self.person_form.age, ("ag", "12")),
            (self.person_form.location, ("loc", "Lusaka")),
        )

    def test_parser(self):
        parsed = self.person_form.parse_text()
        self.assertEqual(parsed, ["fnAndre", "lnLesa", "ag12", "locLusaka"])

    def test_fieldbind(self):
        form_bound_fields = self.person_form.bind_fields(
            self.person_form.original_text)

        self.assertEqual(form_bound_fields, self.expected_bound_fields)

    def test_formvalidation(self):
        passed_validation, python_fields, errors = self.person_form.validate_form(
            self.expected_bound_fields)
        self.assertTrue(passed_validation)
        self.assertEqual([], errors)

    def test_missing_required_field(self):
        valid, python_fields, errors = self.person_form.process_form(
            original_text="REG lnLesa ag12 locLusaka")
        self.assertFalse(valid)
        self.assertIsInstance(errors[0], MissingRequiredFieldException)

    def test_form_validation_date(self):
        bound_fields = self.expected_bound_fields + (
            (self.person_form.date, ("dt", "12jan15")),
        )
        passed_validation, python_fields, errors = self.person_form.validate_form(
            bound_fields)

        self.assertTrue(passed_validation)

        date_field = python_fields[4][1][1]
        self.assertIsInstance(date_field, datetime.date)

    def test_failed_formvalidation(self):
        bound_fields = self.expected_bound_fields + (
            (self.person_form.date, ("", "08xxx11xxx14")),
        )
        passed_validation, python_fields, errors = self.person_form.validate_form(
            bound_fields)
        self.assertFalse(passed_validation)
        date_error = errors[0]
        self.assertIsInstance(date_error, InvalidDateException)

    def test_form_processing(self):
        expected_bound_fields = (
            (self.person_form.first_name.name, ("fn", "Andre")),
            (self.person_form.last_name.name,  ("ln", "Lesa")),
            (self.person_form.age.name, ("ag", "12")),
            (self.person_form.location.name, ("loc", "Lusaka")),
        )
        process_form_result = self.person_form.process_form(original_text="REG fnAndre lnLesa ag12 locLusaka")
        self.assertEqual(process_form_result, (True, expected_bound_fields, []))

    def test_form_processing_error(self):
        process_form_result = self.person_form.process_form(original_text="REG fn lnLesa ag12 locLusaka")
        expected_bound_fields = (
                ('last_name', ('ln', 'Lesa')),
                ('age', ('ag', '12')),
                ('location', ('loc', 'Lusaka'))
                )

        self.assertFalse(process_form_result[0])
        self.assertEqual(process_form_result[1], expected_bound_fields)
        for exception in process_form_result[2]:
            self.assertIsInstance(exception, MissingRequiredFieldException)

class TestSMSFields(unittest.TestCase):

    def setUp(self):
        self.POSITION_CHOICES = ("clerk", "officer", "supervisor", "director")

    def test_prefixes_to_python(self):
        field = PrefixField(prefixes=["fn"], name="first_name")
        data = field.to_python(text="andre", accepted_prefix="fn")
        self.assertEqual(data, ("andre", "fn"))

    def test_multichoice_to_python(self):
        field = MultiChoiceField(
            prefixes=["pos"],
            choices=self.POSITION_CHOICES,
            name="postion"
        )
        # test single choice
        text, accepted_prefix = field.to_python(
            text="clerk", accepted_prefix="pos")
        self.assertEqual((text, accepted_prefix), (["clerk"], "pos"))

        # test multiple choices
        data = field.to_python(
            text="clerk,officer,supervisor", accepted_prefix="pos")
        self.assertEqual(data, (["clerk", "officer", "supervisor"], "pos"))

    def test_bad_date(self):
        field = DateField(name="date")

        with self.assertRaises(InvalidDateException):
            python_date = field.to_python("08xxx11xxx14")

    def test_date_to_python(self):
        field = DateField(name="date")
        python_date = field.to_python("08/nov/14")

        self.assertEqual(python_date, (datetime.date(2014, 11, 8), ""))

    def test_for_required_field(self):
        field = PrefixField(prefixes=["fn"], name="first_name")

        with self.assertRaises(MissingRequiredFieldException):
            python_obj, accepted_prefix = field.to_python(
                "", accepted_prefix="fn")

            field.validate(python_obj)

        with self.assertRaises(MissingRequiredFieldException):
            field.validate("")

    def test_single_choice_validation(self):
        field = SingleChoiceField(
            choices=self.POSITION_CHOICES, name="position")

        expected_msg = "Invalid option 'ceo', please select one of: {choices_string}".format(
            choices_string=", ".join(self.POSITION_CHOICES))

        with self.assertRaises(ChoiceException):
            field.validate(['ceo'])

    def test_multichoice_regex(self):
        field = MultiChoiceField(
            choices=['one', 'two', 'three', 'four', 'five'],
            name="numbers"
            )
        prefix_regex = field.get_field_regex()[0]

        match = re.findall(prefix_regex["regex"], "one,two")

        #self.assertEqual(match, ["one", "two"])


    def test_multichoice_validator(self):
        field = MultiChoiceField(
            choices=self.POSITION_CHOICES, name="First Name")
        # test single INCORRECT choices
        expected_msg = "Invalid options 'ceo, attorney', please select one of: {choices}".format(
            choices=", ".join(set(self.POSITION_CHOICES)))  # force into set first
        # because when done in the field itself, the set messes up the ordering
        with self.assertRaises(ChoiceException):
            field.validate(["attorney", "ceo"])

    def test_to_python(self):
        field = DateField(name="date_field")

        date = field.process_field("12jan15")



    """
    def test_multiple_prefixes(self):
        field = MultiPrefixField(prefixes=["fn", "mn"])
    """


if __name__ == '__main__':
    unittest.main()

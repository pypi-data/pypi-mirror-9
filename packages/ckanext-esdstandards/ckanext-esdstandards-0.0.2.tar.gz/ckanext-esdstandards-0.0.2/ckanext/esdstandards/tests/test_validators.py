import nose.tools

import ckan.plugins.toolkit as toolkit

from ckanext.esdstandards.commands import ESDCommand

from ckanext.esdstandards.validators import (esd_function_validator,
                                             esd_service_validator)

assert_equals = nose.tools.assert_equals
assert_raises = nose.tools.assert_raises


class TestESDValidators(object):

    @classmethod
    def setup_class(cls):

        command = ESDCommand('esd')
        command.load(assume_yes=True)

    def test_esd_function_validator_uri(self):

        context = {}
        value = 'http://id.esd.org.uk/function/22'

        validated_value = esd_function_validator(value, context)

        assert_equals(validated_value, value)

    def test_esd_function_validator_uris(self):

        context = {}
        value = 'http://id.esd.org.uk/function/22 http://id.esd.org.uk/function/23'

        validated_value = esd_function_validator(value, context)

        assert_equals(validated_value, value)

    def test_esd_function_validator_uris_commas(self):

        context = {}
        value = 'http://id.esd.org.uk/function/22, http://id.esd.org.uk/function/23'

        validated_value = esd_function_validator(value, context)

        value_spaces = 'http://id.esd.org.uk/function/22 http://id.esd.org.uk/function/23'
        assert_equals(validated_value, value_spaces)

    def test_esd_function_validator_id(self):

        context = {}
        value = '22'

        validated_value = esd_function_validator(value, context)

        assert_equals(validated_value, 'http://id.esd.org.uk/function/22')

    def test_esd_function_validator_ids(self):

        context = {}
        value = '22 23'

        validated_value = esd_function_validator(value, context)

        value_spaces = 'http://id.esd.org.uk/function/22 http://id.esd.org.uk/function/23'
        assert_equals(validated_value, value_spaces)

    def test_esd_function_validator_ids_commas(self):

        context = {}
        value = '22,23'

        validated_value = esd_function_validator(value, context)

        value_spaces = 'http://id.esd.org.uk/function/22 http://id.esd.org.uk/function/23'
        assert_equals(validated_value, value_spaces)

    def test_esd_function_validator_title(self):

        context = {}
        value = 'Youth offending'

        validated_value = esd_function_validator(value, context)

        assert_equals(validated_value, 'http://id.esd.org.uk/function/22')

    def test_esd_function_validator_titles(self):

        context = {}
        value = 'Youth offending,Education and learning'

        validated_value = esd_function_validator(value, context)

        value_spaces = 'http://id.esd.org.uk/function/22 http://id.esd.org.uk/function/23'
        assert_equals(validated_value, value_spaces)

    def test_esd_function_validator_empty_value(self):

        context = {}
        value = ''

        validated_value = esd_function_validator(value, context)

        assert_equals(validated_value, None)

    def test_esd_function_validator_not_found(self):

        context = {}
        value = 'Not Found'

        assert_raises(toolkit.Invalid, esd_function_validator, value, context)


    def test_esd_service_validator_uri(self):

        context = {}
        value = 'http://id.esd.org.uk/service/1512'

        validated_value = esd_service_validator(value, context)

        assert_equals(validated_value, value)

    def test_esd_service_validator_uris(self):

        context = {}
        value = 'http://id.esd.org.uk/service/1512 http://id.esd.org.uk/service/1513'

        validated_value = esd_service_validator(value, context)

        assert_equals(validated_value, value)

    def test_esd_service_validator_uris_commas(self):

        context = {}
        value = 'http://id.esd.org.uk/service/1512, http://id.esd.org.uk/service/1513'

        validated_value = esd_service_validator(value, context)

        value_spaces = 'http://id.esd.org.uk/service/1512 http://id.esd.org.uk/service/1513'
        assert_equals(validated_value, value_spaces)

    def test_esd_service_validator_id(self):

        context = {}
        value = '1512'

        validated_value = esd_service_validator(value, context)

        assert_equals(validated_value, 'http://id.esd.org.uk/service/1512')

    def test_esd_service_validator_ids(self):

        context = {}
        value = '1512 1513'

        validated_value = esd_service_validator(value, context)

        value_spaces = 'http://id.esd.org.uk/service/1512 http://id.esd.org.uk/service/1513'
        assert_equals(validated_value, value_spaces)

    def test_esd_service_validator_ids_commas(self):

        context = {}
        value = '1512,1513'

        validated_value = esd_service_validator(value, context)

        value_spaces = 'http://id.esd.org.uk/service/1512 http://id.esd.org.uk/service/1513'
        assert_equals(validated_value, value_spaces)

    def test_esd_service_validator_title(self):

        context = {}
        value = 'Abandoned bicycles'

        validated_value = esd_service_validator(value, context)

        assert_equals(validated_value, 'http://id.esd.org.uk/service/1512')

    def test_esd_service_validator_titles(self):

        context = {}
        value = 'Abandoned bicycles,Passenger transport vehicle licence'

        validated_value = esd_service_validator(value, context)

        value_spaces = 'http://id.esd.org.uk/service/1512 http://id.esd.org.uk/service/1513'
        assert_equals(validated_value, value_spaces)

    def test_esd_service_validator_empty_value(self):

        context = {}
        value = ''

        validated_value = esd_service_validator(value, context)

        assert_equals(validated_value, None)

    def test_esd_service_validator_not_found(self):

        context = {}
        value = 'Not Found'

        assert_raises(toolkit.Invalid, esd_service_validator, value, context)


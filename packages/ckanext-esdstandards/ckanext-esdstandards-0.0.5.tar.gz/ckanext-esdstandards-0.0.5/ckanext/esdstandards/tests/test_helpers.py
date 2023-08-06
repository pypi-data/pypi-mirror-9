import nose.tools

from ckanext.esdstandards.commands import ESDCommand

from ckanext.esdstandards.helpers import (get_esd_function_titles,
                                          get_esd_service_titles)

assert_equals = nose.tools.assert_equals
assert_raises = nose.tools.assert_raises


class TestESDHelpers(object):

    @classmethod
    def setup_class(cls):

        command = ESDCommand('esd')
        command.load(assume_yes=True)

    def test_esd_function_titles(self):

        value = 'http://id.esd.org.uk/function/22 http://id.esd.org.uk/function/23'

        titles = get_esd_function_titles(value)

        assert_equals(titles, 'Youth offending, Education and learning')

    def test_esd_function_titles_commas(self):

        value = 'http://id.esd.org.uk/function/22,http://id.esd.org.uk/function/23'

        titles = get_esd_function_titles(value)

        assert_equals(titles, 'Youth offending, Education and learning')

    def test_esd_function_titles_one_not_found(self):

        value = 'http://id.esd.org.uk/function/9999,http://id.esd.org.uk/function/23'

        titles = get_esd_function_titles(value)

        assert_equals(titles, 'Education and learning')

    def test_esd_function_no_value(self):

        value = ''

        titles = get_esd_function_titles(value)

        assert_equals(titles, None)

    def test_esd_service_titles(self):

        value = 'http://id.esd.org.uk/service/1512 http://id.esd.org.uk/service/1513'

        titles = get_esd_service_titles(value)

        assert_equals(titles, 'Abandoned bicycles, Passenger transport vehicle licence')

    def test_esd_service_titles_commas(self):

        value = 'http://id.esd.org.uk/service/1512,http://id.esd.org.uk/service/1513'

        titles = get_esd_service_titles(value)

        assert_equals(titles, 'Abandoned bicycles, Passenger transport vehicle licence')

    def test_esd_service_titles_one_not_found(self):

        value = 'http://id.esd.org.uk/service/9999,http://id.esd.org.uk/service/1513'

        titles = get_esd_service_titles(value)

        assert_equals(titles, 'Passenger transport vehicle licence')

    def test_esd_service_no_value(self):

        value = ''

        titles = get_esd_service_titles(value)

        assert_equals(titles, None)

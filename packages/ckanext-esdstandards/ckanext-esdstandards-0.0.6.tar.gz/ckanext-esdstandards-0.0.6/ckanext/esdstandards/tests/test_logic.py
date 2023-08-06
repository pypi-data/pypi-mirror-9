import nose.tools

import ckan.model as core_model
from ckan.new_tests import helpers
import ckan.plugins.toolkit as toolkit

from ckanext.esdstandards.commands import ESDCommand

assert_equals = nose.tools.assert_equals
assert_raises = nose.tools.assert_raises


class TestESDActions(object):

    @classmethod
    def setup_class(cls):

        command = ESDCommand('esd')
        command.load(assume_yes=True)

    def test_esd_function_show(self):

        esd_function = helpers.call_action('esd_function_show', id=22)

        assert_equals(esd_function['esd_id'], '22')
        assert_equals(esd_function['title'], 'Youth offending')
        assert_equals(esd_function['uri'], 'http://id.esd.org.uk/function/22')

    def test_esd_function_show_by_title(self):

        esd_function = helpers.call_action('esd_function_show',
                                           id='Youth offending')

        assert_equals(esd_function['esd_id'], '22')
        assert_equals(esd_function['title'], 'Youth offending')
        assert_equals(esd_function['uri'], 'http://id.esd.org.uk/function/22')

    def test_esd_function_show_by_uri(self):

        esd_function = helpers.call_action(
            'esd_function_show', id='http://id.esd.org.uk/function/22')

        assert_equals(esd_function['esd_id'], '22')
        assert_equals(esd_function['title'], 'Youth offending')
        assert_equals(esd_function['uri'], 'http://id.esd.org.uk/function/22')

    def test_esd_function_show_not_found(self):

        assert_raises(toolkit.ObjectNotFound, helpers.call_action,
                      'esd_function_show', id='not_found')

    def test_esd_function_show_param_missing(self):

        assert_raises(toolkit.ValidationError, helpers.call_action,
                      'esd_function_show')

    def test_esd_service_show(self):

        esd_function = helpers.call_action('esd_service_show', id=1512)

        assert_equals(esd_function['esd_id'], '1512')
        assert_equals(esd_function['title'], 'Abandoned bicycles')
        assert_equals(esd_function['uri'], 'http://id.esd.org.uk/service/1512')

    def test_esd_service_show_by_title(self):

        esd_function = helpers.call_action('esd_service_show',
                                           id='Abandoned bicycles')

        assert_equals(esd_function['esd_id'], '1512')
        assert_equals(esd_function['title'], 'Abandoned bicycles')
        assert_equals(esd_function['uri'], 'http://id.esd.org.uk/service/1512')

    def test_esd_service_show_by_uri(self):

        esd_function = helpers.call_action(
            'esd_service_show', id='http://id.esd.org.uk/service/1512')

        assert_equals(esd_function['esd_id'], '1512')
        assert_equals(esd_function['title'], 'Abandoned bicycles')
        assert_equals(esd_function['uri'], 'http://id.esd.org.uk/service/1512')

    def test_esd_service_show_not_found(self):

        assert_raises(toolkit.ObjectNotFound, helpers.call_action,
                      'esd_service_show', id='not_found')

    def test_esd_service_show_param_missing(self):

        assert_raises(toolkit.ValidationError, helpers.call_action,
                      'esd_service_show')

    def test_esd_function_autocomplete(self):

        esd_functions = helpers.call_action('esd_function_autocomplete',
                                            q='commu')

        titles = sorted([f['title'] for f in esd_functions])

        assert_equals(titles, [
            'Communications and publicity',
            'Community centres and facilities',
            'Community safety',
            'Community support',
            'Community transport',
        ])

    def test_esd_function_autocomplete_limit(self):

        esd_functions = helpers.call_action('esd_function_autocomplete',
                                            q='commu', limit=2)

        titles = sorted([f['title'] for f in esd_functions])

        assert_equals(titles, [
            'Communications and publicity',
            'Community centres and facilities',
        ])

    def test_esd_function_autocomplete_none_found(self):

        esd_functions = helpers.call_action('esd_function_autocomplete',
                                            q='not_found')

        assert_equals(esd_functions, [])

    def test_esd_function_autocomplete_param_missing(self):

        assert_raises(toolkit.ValidationError, helpers.call_action,
                      'esd_function_autocomplete')

    def test_esd_service_autocomplete(self):

        esd_services = helpers.call_action('esd_service_autocomplete',
                                           q='death')

        titles = sorted([f['title'] for f in esd_services])

        assert_equals(titles, [
            'Death - funerals - cost information',
            'Death - funerals - cremations',
            'Death - historical searches',
            'Death registration',
        ])

    def test_esd_service_autocompletei_limit(self):

        esd_services = helpers.call_action('esd_service_autocomplete',
                                           q='death', limit=2)

        titles = sorted([f['title'] for f in esd_services])

        assert_equals(titles, [
            'Death - funerals - cost information',
            'Death - funerals - cremations',
        ])

    def test_esd_service_autocomplete_none_found(self):

        esd_services = helpers.call_action('esd_service_autocomplete',
                                           q='not_found')

        assert_equals(esd_services, [])

    def test_esd_service_autocomplete_param_missing(self):

        assert_raises(toolkit.ValidationError, helpers.call_action,
                      'esd_service_autocomplete')


class TestESDAuth(object):
    '''All actions should be accessible to all users, even anonymous ones'''

    def test_esd_function_show(self):

        context = {'user': None, 'model': core_model}
        response = helpers.call_auth('esd_function_show',
                                     context=context, id=22)
        assert_equals(response, True)

    def test_esd_function_autocomplete(self):

        context = {'user': None, 'model': core_model}
        response = helpers.call_auth('esd_function_autocomplete',
                                     context=context, q='a')
        assert_equals(response, True)

    def test_esd_service_show(self):

        context = {'user': None, 'model': core_model}
        response = helpers.call_auth('esd_service_show',
                                     context=context, id=1512)
        assert_equals(response, True)

    def test_esd_service_autocomplete(self):

        context = {'user': None, 'model': core_model}
        response = helpers.call_auth('esd_service_autocomplete',
                                     context=context, q='a')
        assert_equals(response, True)

import nose.tools

from routes import url_for

import ckan.plugins as p
import ckan.new_tests.helpers as helpers
import ckan.new_tests.factories as factories

from ckanext.esdstandards.commands import ESDCommand

assert_equals = nose.tools.assert_equals
assert_raises = nose.tools.assert_raises

webtest_submit = helpers.webtest_submit
submit_and_follow = helpers.submit_and_follow


def _get_package_new_page(app):
    user = factories.User()
    env = {'REMOTE_USER': user['name'].encode('ascii')}
    response = app.get(
        url=url_for(controller='package', action='new'),
        extra_environ=env,
    )
    return env, response


class TestESDHelpers(helpers.FunctionalTestBase):

    @classmethod
    def setup_class(cls):

        super(TestESDHelpers, cls).setup_class()

        if not p.plugin_loaded('esd_test_plugin'):
            p.load('esd_test_plugin')

    @classmethod
    def teardown_class(cls):

        p.unload('esd_test_plugin')

    def test_create_dataset_one_value(self):
        dataset_name = u'dataset-esd-1'
        app = self._get_test_app()

        # Recreate tables
        command = ESDCommand('esd')
        command.load(assume_yes=True)

        env, response = _get_package_new_page(app)
        form = response.forms[1]
        form['name'] = dataset_name

        form['la_function'] = u'Youth offending'

        form['la_service'] = u'Abandoned bicycles'

        response = submit_and_follow(app, form, env, 'save')
        form = response.forms[1]
        form['url'] = u'http://example.com/resource'

        submit_and_follow(app, form, env, 'save', 'go-metadata')

        dataset_dict = helpers.call_action('package_show', id=dataset_name)

        assert_equals(dataset_dict['name'], dataset_name)

        assert_equals(dataset_dict['la_function'], 'http://id.esd.org.uk/function/22' )
        assert_equals(dataset_dict['la_service'], 'http://id.esd.org.uk/service/1512' )

    def test_create_dataset_multiple_values(self):
        dataset_name = u'dataset-esd-2'
        app = self._get_test_app()

        # Recreate tables
        command = ESDCommand('esd')
        command.load(assume_yes=True)

        env, response = _get_package_new_page(app)
        form = response.forms[1]
        form['name'] = dataset_name

        form['la_function'] = u'Youth offending,Education and learning'

        form['la_service'] = u'Abandoned bicycles, Passenger transport vehicle licence'

        response = submit_and_follow(app, form, env, 'save')
        form = response.forms[1]
        form['url'] = u'http://example.com/resource'

        submit_and_follow(app, form, env, 'save', 'go-metadata')

        dataset_dict = helpers.call_action('package_show', id=dataset_name)

        assert_equals(dataset_dict['name'], dataset_name)

        assert_equals(dataset_dict['la_function'], 'http://id.esd.org.uk/function/22 http://id.esd.org.uk/function/23' )
        assert_equals(dataset_dict['la_service'], 'http://id.esd.org.uk/service/1512 http://id.esd.org.uk/service/1513')

    def test_create_dataset_ids(self):
        dataset_name = u'dataset-esd-3'
        app = self._get_test_app()

        # Recreate tables
        command = ESDCommand('esd')
        command.load(assume_yes=True)

        env, response = _get_package_new_page(app)
        form = response.forms[1]
        form['name'] = dataset_name

        form['la_function'] = u'22,23'

        form['la_service'] = u'1512,1513'

        response = submit_and_follow(app, form, env, 'save')
        form = response.forms[1]
        form['url'] = u'http://example.com/resource'

        submit_and_follow(app, form, env, 'save', 'go-metadata')

        dataset_dict = helpers.call_action('package_show', id=dataset_name)

        assert_equals(dataset_dict['name'], dataset_name)

        assert_equals(dataset_dict['la_function'], 'http://id.esd.org.uk/function/22 http://id.esd.org.uk/function/23' )
        assert_equals(dataset_dict['la_service'], 'http://id.esd.org.uk/service/1512 http://id.esd.org.uk/service/1513')

    def test_create_dataset_uris(self):
        dataset_name = u'dataset-esd-3'
        app = self._get_test_app()

        # Recreate tables
        command = ESDCommand('esd')
        command.load(assume_yes=True)

        env, response = _get_package_new_page(app)
        form = response.forms[1]
        form['name'] = dataset_name

        form['la_function'] = 'http://id.esd.org.uk/function/22 http://id.esd.org.uk/function/23'
        form['la_service'] = 'http://id.esd.org.uk/service/1512 http://id.esd.org.uk/service/1513'

        response = submit_and_follow(app, form, env, 'save')
        form = response.forms[1]
        form['url'] = u'http://example.com/resource'

        submit_and_follow(app, form, env, 'save', 'go-metadata')

        dataset_dict = helpers.call_action('package_show', id=dataset_name)

        assert_equals(dataset_dict['name'], dataset_name)

        assert_equals(dataset_dict['la_function'], 'http://id.esd.org.uk/function/22 http://id.esd.org.uk/function/23' )
        assert_equals(dataset_dict['la_service'], 'http://id.esd.org.uk/service/1512 http://id.esd.org.uk/service/1513')

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.esdstandards.validators import (esd_function_validator,
                                             esd_service_validator)


class TestESDPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')

    # IDatasetForm

    def _modify_package_schema(self, schema):
        schema.update({
            'la_function': [toolkit.get_validator('ignore_missing'),
                            esd_function_validator,
                            toolkit.get_converter('convert_to_extras')],
            'la_service': [toolkit.get_validator('ignore_missing'),
                           esd_service_validator,
                           toolkit.get_converter('convert_to_extras')],
        })
        return schema

    def create_package_schema(self):
        schema = super(TestESDPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(TestESDPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(TestESDPlugin, self).show_package_schema()
        default_validators = [toolkit.get_converter('convert_from_extras'),
                              toolkit.get_validator('ignore_missing')]

        schema.update({
            'la_function': default_validators,
            'la_service': default_validators,
        })
        return schema

    def is_fallback(self):
        return True

    def package_types(self):
        return []

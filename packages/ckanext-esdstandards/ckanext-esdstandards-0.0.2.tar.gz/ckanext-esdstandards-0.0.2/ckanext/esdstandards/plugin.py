import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.esdstandards.model import setup as model_setup
from ckanext.esdstandards.validators import (esd_function_validator,
                                             esd_service_validator)
from ckanext.esdstandards.logic import (esd_function_autocomplete,
                                        esd_service_autocomplete,
                                        esd_function_show,
                                        esd_service_show,
                                        esd_auth,
                                        )
from ckanext.esdstandards.helpers import (get_esd_function_titles,
                                          get_esd_service_titles)


class ESDStandardsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.ITemplateHelpers)
    if toolkit.check_ckan_version(min_version='2.3'):
        plugins.implements(plugins.IValidators)

    # IConfigurer

    def update_config(self, config_):

        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'esd')

    # IConfigurable

    def configure(self, config):
        model_setup()

    # IActions

    def get_actions(self):
        return {
            'esd_function_show': esd_function_show,
            'esd_service_show': esd_service_show,
            'esd_function_autocomplete': esd_function_autocomplete,
            'esd_service_autocomplete': esd_service_autocomplete,

        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'esd_function_show': esd_auth,
            'esd_service_show': esd_auth,
            'esd_function_autocomplete': esd_auth,
            'esd_service_autocomplete': esd_auth,
        }

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'get_esd_function_titles': get_esd_function_titles,
            'get_esd_service_titles': get_esd_service_titles,
        }

    # IValidators (CKAN >= 2.3)
    def get_validators(self):
        return {
            'esd_function_validator': esd_function_validator,
            'esd_service_validator': esd_service_validator,
        }

.. You should enable this project on travis-ci.org and coveralls.io to make
   these badges work. The necessary Travis and Coverage config files have been
   generated for you.

.. image:: https://travis-ci.org/okfn/ckanext-esdstandards.svg?branch=master
    :target: https://travis-ci.org/okfn/ckanext-esdstandards

.. image:: https://coveralls.io/repos/okfn/ckanext-esdstandards/badge.png?branch=master
  :target: https://coveralls.io/r/okfn/ckanext-esdstandards?branch=master

.. image:: https://pypip.in/version/ckanext-esdstandards/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-esdstandards/
    :alt: Latest Version

.. image:: https://pypip.in/py_versions/ckanext-esdstandards/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-esdstandards/
    :alt: Supported Python versions

.. image:: https://pypip.in/license/ckanext-esdstandards/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-esdstandards/
    :alt: License

====================
ckanext-esdstandards
====================

Helpers for working with LGA's `ESD standards`_ on CKAN.

This extension contains:

* Action functions for autocomplete lookup for ESD Functions and Services

* Form widgets and validators for easily integrate ESD Functions and Services fields
  into custom schemas (adding the ``la_function`` and ``la_service`` fields,
  supported when harvesting datasets into http://data.gov.uk)

* Snippets for rendering the ESD Functions and Services on the dataset page.


For more details, see `Integrating it on your own extension`_

.. _ESD standards: http://standards.esd.org.uk

------------
Installation
------------

To install ckanext-esdstandards:

1. Activate your CKAN virtual environment, for example::

     source /usr/lib/ckan/default/bin/activate

2. Install the ckanext-esdstandards Python package into your virtual environment::

     pip install ckanext-esdstandards

3. Add ``esd`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Populate the DB tables, by running::

    paster --plugin=ckanext-esdstandards esd initdb -c /etc/ckan/default/production.ini
    paster --plugin=ckanext-esdstandards esd load -c /etc/ckan/default/production.ini

5. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


------------------------------------
Integrating it on your own extension
------------------------------------

This extension will not add anything by default to your CKAN instance (apart
from some helper actions and functions). You need to modify the schema and
templates on your project extension to add the fields and widgets.


Adding the ``la_function`` and ``la_service`` fields to your custom schema
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

You will need to extend the default CKAN schema
using the ``IDatasetForm`` interface (as described in the tutorial_).

The extension provides a couple of validators to use. The fields generated
should be stored as extras an named ``la_function`` and ``la_service`` 
(as per Appendix B of the `data.gov.uk harvesting guide`_).

.. _data.gov.uk harvesting guide: http://data.gov.uk/sites/default/files/library/Harvesting%20guide.pdf

This snippet should be easy enough to follow (**note**: this assumes CKAN>=2.3)::

    import ckan.plugins as plugins
    import ckan.plugins.toolkit as toolkit


    class MyPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
        plugins.implements(plugins.IDatasetForm)


        # IDatasetForm

        def _modify_package_schema(self, schema):
            schema.update({
                'la_function': [toolkit.get_validator('ignore_missing'),
                                toolkit.get_validator('esd_function_validator'),
                                toolkit.get_converter('convert_to_extras')],
                'la_service': [toolkit.get_validator('ignore_missing'),
                               toolkit.get_validator('esd_service_validator'),
                               toolkit.get_converter('convert_to_extras')],
            })
            return schema

        def create_package_schema(self):
            schema = super(MyPlugin, self).create_package_schema()
            schema = self._modify_package_schema(schema)
            return schema

        def update_package_schema(self):
            schema = super(MyPlugin, self).update_package_schema()
            schema = self._modify_package_schema(schema)
            return schema

        def show_package_schema(self):
            schema = super(MyPlugin, self).show_package_schema()
            default_validators = [toolkit.get_converter('convert_from_extras'),
                                  toolkit.get_validator('ignore_missing')]

            schema.update({
                'la_function': default_validators,
                'la_service': default_validators,
            })
            return schema

On CKAN versions lower than 2.3, the validators need to be explicitly imported::

    import ckan.plugins as plugins
    import ckan.plugins.toolkit as toolkit

    from ckanext.esdstandards.validators import (esd_function_validator,
                                                 esd_service_validator)

    class MyPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
        plugins.implements(plugins.IDatasetForm)


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
            schema = super(MyPlugin, self).create_package_schema()
            schema = self._modify_package_schema(schema)
            return schema

        def update_package_schema(self):
            schema = super(MyPlugin, self).update_package_schema()
            schema = self._modify_package_schema(schema)
            return schema

        def show_package_schema(self):
            schema = super(MyPlugin, self).show_package_schema()
            default_validators = [toolkit.get_converter('convert_from_extras'),
                                  toolkit.get_validator('ignore_missing')]

            schema.update({
                'la_function': default_validators,
                'la_service': default_validators,
            })
            return schema


.. _tutorial: http://docs.ckan.org/en/latest/extensions/adding-custom-fields.html


Adding the Functions and Services fields to the dataset form
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The extension provides two covenient snippets that will add all the necessary
markup and scripts to the templates. You need to extend the ``package_basic_fields.html``
template on your own extension with the following::

    # ckanext-yourext/ckanext/yourext/templates/package/snippets/package_basic_fields.html

    {% ckan_extends %}

    {% block package_basic_fields_custom %}

      {% snippet 'snippets/esd_functions.html', data=data, errors=errors %}

      {% snippet 'snippets/esd_services.html', data=data, errors=errors %}

    {% endblock %}


You should see a couple of new fields added, similar to the one for defining tags:

.. image:: http://i.imgur.com/sPqeK7q.png

Adding the field values on the dataset page
+++++++++++++++++++++++++++++++++++++++++++

Just extend  the ``additional_info.html`` template on your own extension with the following::

    # ckanext-yourext/ckanext/yourext/templates/package/snippets/additional_info.html

    {% ckan_extends %}

    {% block extras %}

      {{ super() }}

      {% snippet 'snippets/esd_functions_additional_info.html', data=pkg_dict %}

      {% snippet 'snippets/esd_services_additional_info.html', data=pkg_dict %}

    {% endblock %}

You can pass ``display_row_if_missing=False`` to the snippet to completely hide the
row if no values are defined.

The snippets will show the fields rendered like that:

.. image:: http://i.imgur.com/0HFUwcw.png



------------------------
Development Installation
------------------------

To install ckanext-esdstandards for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/okfn/ckanext-esdstandards.git
    cd ckanext-esdstandards
    python setup.py develop


-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --ckan --with-pylons=test.ini


----------------------------------------
Registering ckanext-esdstandards on PyPI
----------------------------------------

ckanext-esdstandards should be availabe on PyPI as
https://pypi.python.org/pypi/ckanext-esdstandards. If that link doesn't work, then
you can register the project on PyPI for the first time by following these
steps:

1. Create a source distribution of the project::

     python setup.py sdist

2. Register the project::

     python setup.py register

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the first release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.1 then do::

       git tag 0.0.1
       git push --tags


-----------------------------------------------
Releasing a New Version of ckanext-esdstandards
-----------------------------------------------

ckanext-esdstandards is availabe on PyPI as https://pypi.python.org/pypi/ckanext-esdstandards.
To publish a new version to PyPI follow these steps:

1. Update the version number in the ``setup.py`` file.
   See `PEP 440 <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
   for how to choose version numbers.

2. Create a source distribution of the new version::

     python setup.py sdist

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the new release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.2 then do::

       git tag 0.0.2
       git push --tags

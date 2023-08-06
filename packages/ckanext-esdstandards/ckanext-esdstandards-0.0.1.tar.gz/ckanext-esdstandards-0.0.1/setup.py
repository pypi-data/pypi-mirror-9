from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(
    name='ckanext-esdstandards',
    version=version,
    description="Helpers for working with LGA's ESD standards on CKAN",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Open Knowledge',
    author_email='services@okfn.org',
    url='https://github.com/okfn/ckanext-esdstandards',
    license='AGPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.esdstandards'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        esd=ckanext.esdstandards.plugin:ESDStandardsPlugin
        [ckan.test_plugins]
        esd_test_plugin=ckanext.esdstandards.tests.mockplugin.plugin:TestESDPlugin
        [paste.paster_command]
        esd = ckanext.esdstandards.commands:ESDCommand
    ''',
)

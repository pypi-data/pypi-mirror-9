import os
import sys
import csv
import logging


from ckan import model
import ckan.plugins.toolkit as toolkit

from ckanext.esdstandards.model import setup as db_setup


class ESDCommand(toolkit.CkanCommand):
    '''Management functions for the ESD Standards extension

    Usage:

      paster esd initdb

        Creates the necessary tables in the database

      paster esd load

        Populates the DB tables with the data CSV files. These are
        the ones than can be downloaded from:
        http://standards.esd.org.uk/?uri=list%2Ffunctions&tab=downloads

    '''

    summary = __doc__.split('\n')[0]
    usage = __doc__
    min_args = 1

    def __init__(self, name):

        super(ESDCommand, self).__init__(name)

    def _get_logger(self):
        return logging.getLogger(__name__)

    def command(self):
        self._load_config()
        if not self.args:
            print self.usage
        elif self.args[0] == 'initdb':
            self.initdb()
        elif self.args[0] == 'load':
            self.load()
        else:
            print self.usage

    def initdb(self):
        log = self._get_logger()

        db_setup()

        log.info('DB tables created')

    def load(self, assume_yes=False):

        from ckanext.esdstandards.model import (esd_function_table,
                                                esd_service_table)
        db_setup()

        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', '..', 'ckanext-esdstandards-data')
        csv_functions = os.path.join(csv_path, 'functions.csv')
        csv_services = os.path.join(csv_path, 'services.csv')

        mapping_functions = {
            'Identifier': 'esd_id',
            'Label': 'title',
            'Description': 'description',
            'Parent identifiers': 'parent',
        }
        mapping_services = {
            'Identifier': 'esd_id',
            'Label': 'title',
            'Description': 'description',
        }

        self._load('function', csv_functions, mapping_functions,
                   esd_function_table, assume_yes)
        self._load('service', csv_services, mapping_services,
                   esd_service_table, assume_yes)

    def _load(self, object_type, csv_file, mapping, table, assume_yes=False):

        if model.Session.execute(table.count()).scalar():
            msg = 'Table {0} already contains records, '.format(table.name) + \
                  'do you want to recreate them?'
            if not assume_yes:
                confirm = query_yes_no(msg, default='yes')
                if confirm == "no":
                    return
            model.Session.execute(table.delete())

        log = self._get_logger()

        ckan_dicts = []
        with open(csv_file, 'r') as f:

            reader = csv.DictReader(f)
            for row in reader:
                ckan_dict = {}
                for esd_key, ckan_key in mapping.iteritems():
                    if not row[esd_key]:
                        ckan_dict[ckan_key] = None
                    else:
                        ckan_dict[ckan_key] = row[esd_key]
                ckan_dict['uri'] = 'http://id.esd.org.uk/{0}/{1}'.format(
                    object_type, ckan_dict['esd_id'])
                ckan_dicts.append(ckan_dict)

        if ckan_dicts:

            model.Session.execute(table.insert(), ckan_dicts)
            model.Session.commit()

            log.info('Done: {0} objects of type {1} inserted'.format(
                     len(ckan_dicts), object_type))


# From http://code.activestate.com/recipes/577058/ MIT licence.
# Written by Trent Mick
# This is on CKAN 2.3
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes": "yes",   "y": "yes",  "ye": "yes",
             "no": "no",     "n": "no"}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

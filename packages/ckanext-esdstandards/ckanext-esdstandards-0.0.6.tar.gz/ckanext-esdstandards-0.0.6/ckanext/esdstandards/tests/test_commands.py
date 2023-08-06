import os
import csv
import nose.tools

from ckan import model
from ckan.new_tests import helpers

from ckanext.esdstandards.commands import ESDCommand
from ckanext.esdstandards.model import esd_function_table, esd_service_table

assert_equals = nose.tools.assert_equals
assert_raises = nose.tools.assert_raises


def _num_rows_in_csv_files():

    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            '..', '..', '..', 'ckanext-esdstandards-data')
    csv_functions = os.path.join(csv_path, 'functions.csv')
    csv_services = os.path.join(csv_path, 'services.csv')
    with open(csv_functions, 'r') as f:
        reader = csv.DictReader(f)
        lines_functions = sum(1 for row in reader)
    with open(csv_services, 'r') as f:
        reader = csv.DictReader(f)
        lines_services = sum(1 for row in reader)

    return lines_functions, lines_services


class TestESDCommands(object):

    @classmethod
    def teardown_class(cls):
        helpers.reset_db()

    def test_initdb(self):

        command = ESDCommand('esd')

        command.initdb()

        assert esd_function_table.exists()
        assert esd_service_table.exists()

    def test_load_data(self):

        command = ESDCommand('esd')

        command.load(assume_yes=True)

        assert esd_function_table.exists()
        assert esd_service_table.exists()

        row_count_functions, row_count_services = _num_rows_in_csv_files()

        assert_equals(
            model.Session.execute(esd_function_table.count()).scalar(),
            row_count_functions)

        assert_equals(
            model.Session.execute(esd_service_table.count()).scalar(),
            row_count_services)

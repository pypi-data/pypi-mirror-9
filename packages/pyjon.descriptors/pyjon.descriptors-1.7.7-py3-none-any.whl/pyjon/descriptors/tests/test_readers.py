from six import next
import unittest

from pyjon.descriptors.readers import to_bool
from pyjon.descriptors.readers import CSVReader
from pyjon.descriptors.readers import FixedLengthReader
from pyjon.descriptors.exceptions import TooFewFieldsError
from pyjon.descriptors.exceptions import TooManyFieldsError
from xml.etree import cElementTree as ET

from pyjon.descriptors.tests.test_utils import basetestdir
from pyjon.descriptors.tests.test_utils import open_file


class TestReaderTools(unittest.TestCase):

    def test_to_bool_false(self):
        values = [
            'false',
            'FALSE',
            'False',
            'fAlSe',
            'no',
            'NO',
            'No',
            'nO',
            'off',
            'OFF',
            'OFf',
            'oFF',
            '0',
        ]

        for value in values:
            self.assertFalse(to_bool(value))

    def test_to_bool_true(self):
        values = [
            'true',
            'TRUE',
            'True',
            'tRUE',
            'yes',
            'YES',
            'Yes',
            'yES',
            'on',
            'ON',
            'On',
            'oN',
            '1',
        ]

        for value in values:
            self.assertTrue(to_bool(value))

    def test_to_bool_raises(self):
        values = [
            'TreU',
            'Flase',
            'Nope',
            '2',
        ]

        for value in values:
            self.assertRaises(ValueError, to_bool, value)


class TestCount(unittest.TestCase):

    def test_fixed_count(self):
        schema_filename = '%s/DESC_TEST_FIXED.xml' % basetestdir
        sourcefilename = '%s/fixedlength.txt' % basetestdir
        source = open_file(sourcefilename, 'r')
        schema = ET.parse(schema_filename)
        encoding = 'utf-8'

        reader = FixedLengthReader(encoding, schema)

        assert reader.get_record_count(source) == 3, (
            "We should have counter 3 records"
        )


class TestFixedSplit(unittest.TestCase):

    def test_split(self):
        # in this test we read a fixed source with 250 char per line but
        # we have a special descriptor which will only read the 160 first chars
        # and ignore the rest thus saving up memory on each produced item
        # this also means the generator does not have to describe the data
        # structure defined after the split with dummy placeholders...
        schema_filename = '%s/DESC_TEST_FIXED_SPLIT.xml' % basetestdir
        sourcefilename = '%s/fixedlength.txt' % basetestdir
        source = open_file(sourcefilename, 'r')
        schema = ET.parse(schema_filename)
        encoding = 'utf-8'

        reader = FixedLengthReader(encoding, schema)

        assert reader.get_record_count(source) == 3, (
            "We should have counted 3 records"
        )
        iterator = reader.read(source)
        item = next(iterator)
        assert item.ZSDAT == u'20'


class TestCSVReader(unittest.TestCase):

    def test_csv_toofewfields(self):
        schema_filename = '%s/DESC_TEST_DATE_valid.xml' % basetestdir
        sourcefilename = '%s/csv_date_toofewfieldstests.csv' % basetestdir
        source = open_file(sourcefilename, 'r')
        schema = ET.parse(schema_filename)
        encoding = 'utf-8'

        reader = CSVReader(encoding, schema)

        iterator = reader.read(source)

        self.assertRaises(TooFewFieldsError, lambda: next(iterator))

    def test_csv_toomanyfields(self):
        schema_filename = '%s/DESC_TEST_DATE_valid.xml' % basetestdir
        sourcefilename = '%s/csv_date_toomanyfieldstests.csv' % basetestdir
        source = open_file(sourcefilename, 'r')
        schema = ET.parse(schema_filename)
        encoding = 'utf-8'

        reader = CSVReader(encoding, schema)

        iterator = reader.read(source)

        self.assertRaises(TooManyFieldsError, lambda: next(iterator))

    def test_csv_donotkeepsource(self):
        schema_filename = '%s/DESC_TEST_DATE_valid.xml' % basetestdir
        sourcefilename = '%s/csv_date_tests.csv' % basetestdir
        source = open_file(sourcefilename, 'r')
        schema = ET.parse(schema_filename)
        encoding = 'utf-8'

        # explicitly ask the reader to discard the source row
        reader = CSVReader(encoding, schema, keep_source_ref=False)

        iterator = reader.read(source)

        item = next(iterator)
        # ensure the produced item does not have the raw data attached to it
        self.assertEquals(getattr(item, 'data_row__', None), None)

    def test_csv_keepsource(self):
        schema_filename = '%s/DESC_TEST_DATE_valid.xml' % basetestdir
        sourcefilename = '%s/csv_date_tests.csv' % basetestdir
        source = open_file(sourcefilename, 'r')
        schema = ET.parse(schema_filename)
        encoding = 'utf-8'

        # explicitly ask the reader to keep the source
        reader = CSVReader(encoding, schema, keep_source_ref=True)

        iterator = reader.read(source)

        item = next(iterator)
        # ensure the produced item has the raw data attached to it
        # and that this raw data is what we expect it to be
        self.assertEquals(
            getattr(item, 'data_row__', None),
            ['C000301', '2008-05-22']
        )

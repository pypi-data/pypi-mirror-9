# -*- encoding: utf-8 -*-
"""test cases to ensure the descriptor always behaves the way
we expect
"""

import six
from six import next

from pyjon.descriptors import InputItem, Descriptor
from xml.etree import cElementTree as ET

from pyjon.descriptors.exceptions import MaxLenError
from pyjon.descriptors.exceptions import MinLenError
from pyjon.descriptors.exceptions import MissingFieldError

import decimal
import datetime

from pyjon.descriptors.tests.test_utils import get_descriptor, basetestdir
from pyjon.descriptors.tests.test_utils import open_file
import unittest


class TestDescriptors(unittest.TestCase):

    def test_descriptor_return(self):
        """test that the descriptor is returning valid InputItem objects
        """

        schema_filename = '%s/DESC_TEST_DECIMAL.xml' % basetestdir
        sourcefilename = '%s/csv_decimal_tests.csv' % basetestdir

        d = get_descriptor(schema_filename, 'utf-8')

        source = open_file(sourcefilename, 'r')
        # read one item from the source
        for item in d.read(source):
            assert isinstance(item, InputItem)
            break

        source.close()

    def test_invalid_node_type(self):
        schema_filename = '%s/DESC_TEST_invalid_type.xml' % basetestdir
        sourcefilename = '%s/csv_decimal_tests.csv' % basetestdir

        d = get_descriptor(schema_filename, 'utf-8')

        source = open_file(sourcefilename, 'r')
        # read one item from the source
        self.assertRaises(ValueError, lambda: next(d.read(source)))

        source.close()

    def test_invalid_descriptor_mode(self):
        schema_filename = '%s/DESC_TEST_invalid_mode.xml' % basetestdir
        payload_tree = ET.parse(schema_filename)

        self.assertRaises(
            ValueError,
            Descriptor,
            payload_tree,
            'utf-8'
        )

    def test_invalid_input_type(self):
        schema_filename = '%s/DESC_TEST_invalid_inputtype.xml' % basetestdir
        payload_tree = ET.parse(schema_filename)

        self.assertRaises(
            ValueError,
            Descriptor,
            payload_tree,
            'utf-8'
        )

    def test_date_without_format_and_mandatory(self):
        """a date node without format should raise a value error
        if it is mandatory
        """
        schema_filename = '%s/DESC_TEST_DATE_invalid.xml' % basetestdir
        sourcefilename = '%s/csv_date_tests.csv' % basetestdir

        d = get_descriptor(schema_filename, 'utf-8')

        source = open_file(sourcefilename, 'r')
        # read one item from the source and see how it should fail
        self.assertRaises(ValueError, lambda: next(d.read(source)))

        source.close()

    def test_date_without_format_and_not_mandatory(self):
        """a date node without format should not raise a value error
        if it is not mandatory but it will return None... !!!
        """
        schema_filename = '%s/DESC_TEST_DATE_validnoformat.xml' % basetestdir
        sourcefilename = '%s/csv_date_tests.csv' % basetestdir
        source = open_file(sourcefilename, 'r')

        d = get_descriptor(schema_filename, 'utf-8')

        for index, item in enumerate(d.read(source)):
            if index == 0:
                self.assertIsNone(item.Field2, None)
            elif index == 1:
                self.assertIsNone(item.Field2, None)
            elif index == 2:
                self.assertIsNone(item.Field2, None)

        source.close()

    def test_date_with_format_and_mandatory(self):
        """a date node with format should return a proper date
        """
        schema_filename = '%s/DESC_TEST_DATE_valid.xml' % basetestdir
        sourcefilename = '%s/csv_date_tests.csv' % basetestdir
        source = open_file(sourcefilename, 'r')

        d = get_descriptor(schema_filename, 'utf-8')

        for index, item in enumerate(d.read(source)):
            if index == 0:
                self.assertEquals(item.Field2, datetime.date(2008, 5, 22))
            elif index == 1:
                self.assertEquals(item.Field2, datetime.date(2008, 5, 21))
            elif index == 2:
                self.assertEquals(item.Field2, datetime.date(2008, 5, 5))

        source.close()

    def test_field_notmandatory_but_strict(self):
        """a non mandatory field which is marked as strict cannot
        raise a caster error and get a None value transparently
        """
        schema_filename = (
            '%s/DESC_TEST_DATE_valid_strict_notmandatory.xml' % basetestdir)

        sourcefilename = '%s/csv_date_strict_tests_invalid.csv' % basetestdir
        source = open_file(sourcefilename, 'r')

        d = get_descriptor(schema_filename, 'utf-8')

        read_iter = d.read(source)

        # normal field with parsable value in it
        item = next(read_iter)
        self.assertEquals(item.Field2, datetime.date(2008, 5, 22))

        # since data is not mandatory, field even marked as strict will give a
        # None
        item = next(read_iter)
        self.assertIsNone(item.Field2)

        # But a field with an invalid value will raise a ValueError since the
        # strict flag forces it to raise instead of returning a None value
        self.assertRaises(ValueError, lambda: next(read_iter))

        source.close()

    def test_missing_field_mandatory_and_strict(self):
        """a mandatory field cannot be blank
        """
        schema_filename = (
            '%s/DESC_TEST_DATE_valid_strict_mandatory.xml' % basetestdir)

        sourcefilename = '%s/csv_date_strict_tests.csv' % basetestdir
        source = open_file(sourcefilename, 'r')

        d = get_descriptor(schema_filename, 'utf-8')

        read_iter = d.read(source)

        item = next(read_iter)
        self.assertEquals(item.Field2, datetime.date(2008, 5, 22))

        item = next(read_iter)
        self.assertEquals(item.Field2, datetime.date(2008, 5, 21))

        # this field is marked as mandatory and the raw value is '' so it will
        # raise a MissingFieldError as opposed to the non mandatory / non
        # strict field which returns None
        self.assertRaises(MissingFieldError, lambda: next(read_iter))

        source.close()

    def test_descriptor_underlength(self):
        """descriptor should raise an exception because the field
        is under 4 which is what is defined in the xml description
        """

        schema_filename = '%s/DESC_TEST_DECIMAL.xml' % basetestdir
        sourcefilename = '%s/tinyfield1.csv' % basetestdir

        d = get_descriptor(schema_filename, 'utf-8')
        source = open_file(sourcefilename, 'r')

        len_error = False

        # read one item from the source
        try:
            for item in d.read(source):
                break

        except MinLenError:
            len_error = True

        source.close()
        # The source should have provoked a MinLenError exception
        self.assertTrue(len_error)

    def test_descriptor_decimal_overlength(self):
        """descriptor should raise an exception because the field
        is over 7 which is what is defined in the xml description
        """

        schema_filename = '%s/DESC_TEST_DECIMAL.xml' % basetestdir
        sourcefilename = '%s/bigfield1.csv' % basetestdir

        d = get_descriptor(schema_filename, 'utf-8')
        source = open_file(sourcefilename, 'r')

        len_error = False

        # read one item from the source
        try:
            for item in d.read(source):
                break

        except MaxLenError:
            len_error = True

        source.close()

        self.assertTrue(len_error)

    def test_csv_get_record_count(self):
        """get_record_count implementation for csv reader
        """
        schema_filename = '%s/DESC_TEST_DECIMAL.xml' % basetestdir
        sourcefilename = '%s/csv_decimal_tests.csv' % basetestdir

        d = get_descriptor(schema_filename, 'utf-8')

        source = open_file(sourcefilename, 'r')

        # test that the get_record_count method works
        self.assertEquals(d.get_record_count(source), 4)

    def test_csv_decimal(self):
        """casters will not bork if decimal is not mandatory and not present
        """
        schema_filename = '%s/DESC_TEST_DECIMAL.xml' % basetestdir
        sourcefilename = '%s/csv_decimal_tests.csv' % basetestdir

        d = get_descriptor(schema_filename, 'utf-8')

        source = open_file(sourcefilename, 'r')

        # read one item from the source
        items = list()
        for item in d.read(source):
            items.append(item)

        source.close()

        itemslen = len(items)
        self.assertEquals(
            itemslen,
            4,
            msg="We have 4 items in the file, not %s" % itemslen
        )
        item1 = items[0]
        item2 = items[1]
        item3 = items[2]
        item4 = items[3]

        # asset 1
        assert item1.Field1 == u'C000301'
        assert item1.Field2 == decimal.Decimal('2008.33')
        assert item1.Field3 == decimal.Decimal('2008.33')

        # asset 2
        assert item2.Field1 == u'611380'
        self.assertIsNone(item2.Field2)
        assert item2.Field3 == decimal.Decimal('2008.33')

        # asset 3
        assert item3.Field1 == u'611380'
        assert item3.Field2 == decimal.Decimal('2008.33')
        assert item3.Field3 is None

        # asset 4
        assert item4.Field1 == u'611380'
        assert item4.Field2 == decimal.Decimal('-2008.33')
        assert item4.Field3 is None

    def test_descriptor_fixed_length(self):
        """test that the fixed length reader works with test data of holding
        """
        schema_filename = '%s/DESC_TEST_FIXED.xml' % basetestdir
        sourcefilename = '%s/fixedlength.txt' % basetestdir

        d = get_descriptor(schema_filename, 'utf-8')

        source = open_file(sourcefilename, 'r')
        items = list()
        for item in d.read(source):
            items.append(item)

        source.close()

        assert len(items) == 3

        line_0_dict = {
            'ACCOUNT': u'DLL00000',
            'ZSDAT': u'20',
            'SUB_ACCOUNT': None,
            'DEBIT_CREDIT': u'C',
            'YEAR': 9,
            'MONTH': 5,
            'DAY': 31,
            'CURRENCY': u'E',
            'AMOUNT': decimal.Decimal("0.66"),
            'ANALYTIC_CODE': None, 'DESCRIPTION': u'TOTO'
        }

        for key, value in line_0_dict.items():
            assert getattr(items[0], key) == value

    def test_descriptor_fixed_length_overlength(self):
        """test that the fixed length reader raises error if lines are too big
        """
        schema_filename = '%s/DESC_TEST_FIXED.xml' % basetestdir
        sourcefilename = '%s/fixedlength_toobig.txt' % basetestdir

        d = get_descriptor(schema_filename, 'utf-8')

        source = open_file(sourcefilename, 'r')
        len_error = False
        try:
            for item in d.read(source):
                break

        except MaxLenError:
            len_error = True

        source.close()

        assert len_error is True

    def test_descriptor_fixed_length_underlength(self):
        """test that the fixed length reader raises error if
        lines are too small
        """
        schema_filename = '%s/DESC_TEST_FIXED.xml' % basetestdir
        sourcefilename = '%s/fixedlength_toosmall.txt' % basetestdir

        d = get_descriptor(schema_filename, 'utf-8')

        source = open_file(sourcefilename, 'r')
        len_error = False
        try:
            for item in d.read(source):
                break

        except MinLenError:
            len_error = True

        source.close()

        assert len_error is True

    def test_descriptor_fixed_length_subdescriptors(self):
        """test that subdescriptors work as expected
        """
        schema_filename = '%s/DESC_TEST_FIXED_SUBS.xml' % basetestdir
        sourcefilename = '%s/fixedlength_sub.txt' % basetestdir

        lines_dict = [
            {
                'type': u'IR',
                'content': {
                    'name': 'BARACK OBAMA',
                },
            },
            {
                'type': u'10',
                'content': {
                    'date': '20100528',
                    'debit_credit': u'C',
                    'amount': decimal.Decimal("0.66"),
                    'currency': u'E',
                },
            },
        ]

        d = get_descriptor(schema_filename, 'utf-8')

        source = open_file(sourcefilename, 'r')
        items = d.read(source)

        for i, item in enumerate(items):
            for k, v in six.iteritems(lines_dict[i]):
                if k == 'content':
                    for k1, v1 in six.iteritems(v):
                        self.assertEquals(
                            getattr(getattr(item, k), k1),
                            v1,
                            msg="Invalid value for item.%s: %s "
                                "instead of the expected %s" % (
                                    k, getattr(item, k), v
                                )
                        )
                else:
                    self.assertEquals(
                        getattr(item, k),
                        v,
                        msg="Invalid value for item.%s: %s "
                            "instead of the expected %s" % (
                                k, getattr(item, k), v
                            )
                    )

        source.close()

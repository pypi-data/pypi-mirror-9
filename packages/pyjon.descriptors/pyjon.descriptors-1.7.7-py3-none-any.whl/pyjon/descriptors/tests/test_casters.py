# global import we will always need
from pyjon.descriptors.casters import Caster
import decimal
import datetime
import unittest


class TestDescriptors(unittest.TestCase):
    def create_type_dict(
        self, ftype, format=None, thousanddelimiter=None,
        decimaldelimiter=None, decimalplaces=None
    ):
        type_dict = dict(
            name='%s' % ftype,
            items={}
        )

        if format:
            type_dict['items']['format'] = format

        if thousanddelimiter:
            type_dict['items']['thousanddelimiter'] = thousanddelimiter

        if decimaldelimiter:
            type_dict['items']['decimaldelimiter'] = decimaldelimiter

        if decimalplaces:
            type_dict['items']['decimalplaces'] = decimalplaces

        return type_dict

    def test_caster_instanciation(self):
        """first validate that we are able to instanciate a caster
        """
        caster = Caster()

        assert isinstance(caster, Caster)

    def test_caster_string(self):
        """
        now validate that the simplest of all is working:
        a simple string should come back as a simple string
        """

        caster = Caster()
        typenode = self.create_type_dict('string')
        result = caster.to_python('toto', typenode)

        assert result == 'toto'

    def test_caster_int(self):
        """
        make sure the casters are correctly returning integers
        """

        caster = Caster()
        typenode = self.create_type_dict('int')

        result = caster.to_python('32', typenode)
        assert result == 32

    def test_caster_decimal_dot(self):
        """make sure the casters are correctly returning decimal
        with dot from one with dot
        """
        caster = Caster()
        typenode = self.create_type_dict('decimal', decimaldelimiter='.')

        result = caster.to_python('32.24', typenode)
        assert result == decimal.Decimal('32.24')

    def test_caster_decimal_places(self):
        """
        make sure the casters are correctly returning decimal.
        'decimal places' is expressed as a string
        """
        caster = Caster()
        typenode = self.create_type_dict('decimal', decimalplaces='2')

        result = caster.to_python('3224', typenode)
        assert result == decimal.Decimal('32.24')

    def test_caster_decimal_coma(self):
        """make sure the casters are correctly returning decimal
        with dot from one with coma
        """
        caster = Caster()
        typenode = self.create_type_dict('decimal', decimaldelimiter=',')

        result = caster.to_python('32,24', typenode)
        assert result == decimal.Decimal('32.24')

    def test_caster_thousand_coma(self):
        """make sure the casters are correctly returning decimal
        without thousand delimiter from a number with coma thousand delimiter
        """
        caster = Caster()
        typenode = self.create_type_dict('decimal', thousanddelimiter=',')

        result = caster.to_python('3,224', typenode)
        assert result == decimal.Decimal('3224')

    def test_caster_thousand_coma_with_decimal_dot(self):
        """make sure the casters are correctly returning decimal
        with dot from one with dot decimal delimiter and coma
        thousand separator
        """
        caster = Caster()
        typenode = self.create_type_dict(
            'decimal', thousanddelimiter=',', decimaldelimiter='.'
        )

        result = caster.to_python('3,224.88', typenode)
        assert result == decimal.Decimal('3224.88')

    def test_caster_date1(self):
        """make sure the date caster handles his job for a basic format string
        """
        caster = Caster()
        typenode = self.create_type_dict('date', format='%d/%m/%Y')

        result = caster.to_python('27/08/2007', typenode)
        assert result == datetime.date(2007, 8, 27)

    def test_caster_date2(self):
        """make sure the date caster handles his job for a basic format string
        """
        caster = Caster()
        typenode = self.create_type_dict('date', format='%Y-%m-%d')

        result = caster.to_python('2007-06-12', typenode)
        assert result == datetime.date(2007, 6, 12)

    def test_caster_decimal_places0(self):
        """test comportement when decimal places = 0
        """
        caster = Caster()
        typenode = self.create_type_dict('decimal', decimalplaces=0)

        result = caster.to_python('3224', typenode)
        assert result == decimal.Decimal('3224')

"""Caster class that takes a unicode object and returns a python
object based on parameters provided in the type node.
A type node is an ElementTree.Element that contains at least a field
named type_dict
"""
__all__ = ['Caster']

import datetime  # pragma: no cover
import decimal  # pragma: no cover
import logging  # pragma: no cover

log = logging.getLogger(__name__)


class Caster(object):
    """
    this is a caster that will handle unicode string input,
    type declarations and format string (optionnal).
    It then returns python objects casted from the input
    """

    def to_python(self, str_value, type_dict):
        """
        If something goes wrong this will return None

        @param str_value: the value of the string directly from the
        source
        @type str_value: str object (unicode on Python 2)

        @param type_dict: a dictionnary that contains
        a value corresponding to the desired type and attributes about
        the formating of this value.
        @type type_dict: dict
        """
        if str_value is None or str_value.strip() == '':
            return None

        field_type = type_dict['name']

        if field_type == 'string':
            return str_value

        elif field_type == 'date':
            strfmt = type_dict['items'].get('format')
            if not strfmt:
                raise ValueError(
                    "With type date, you must define the "
                    "input format using the format attribute, "
                    "example : format='%s%m%y'"
                )

            return datetime.datetime.strptime(str_value, strfmt).date()

        elif field_type == 'int':
            return int(str_value.strip())

        elif field_type == 'decimal':
            dec_place = type_dict['items'].get('decimalplaces')
            ths_sep = type_dict['items'].get('thousanddelimiter')
            dec_sep = type_dict['items'].get('decimaldelimiter')

            if dec_place is not None:

                sep = 0 - int(dec_place)
                pref = ''

                if str_value.startswith('-'):
                    pref = '-'
                    str_value = str_value.split('-').pop()

                str_value = str_value.zfill(int(dec_place))
                toconvert = "%s%s.%s" % (
                    pref, str_value[:sep], str_value[sep:]
                )

            else:
                if ths_sep is not None:
                    toconvert = str_value.replace(ths_sep, '')
                else:
                    toconvert = str_value

                if dec_sep is not None and not dec_sep == '.':
                    toconvert = toconvert.replace(dec_sep, '.')

            return decimal.Decimal(toconvert.strip())

        else:
            # no supported type found ;(
            raise ValueError('Unsupported type: "%s"' % field_type)

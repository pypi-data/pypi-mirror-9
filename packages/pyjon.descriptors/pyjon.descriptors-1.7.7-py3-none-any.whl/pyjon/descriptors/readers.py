# -*- encoding: utf-8 -*-
"""defines specialized readers that will be used by the pyjon descriptors
"""
__all__ = ['CSVReader', 'FixedLengthReader']

import ast
import csv  # pragma: no cover
import logging  # pragma: no cove
from lxml import etree  # pragma: no cover
import six
from six import exec_
from six import next

from pyjon.descriptors.input import InputItem
from pyjon.descriptors.exceptions import MaxLenError
from pyjon.descriptors.exceptions import MinLenError
from pyjon.descriptors.exceptions import MissingFieldError
from pyjon.descriptors.exceptions import TooManyFieldsError
from pyjon.descriptors.exceptions import TooFewFieldsError
from pyjon.descriptors.exceptions import RemainingDataError
from pyjon.descriptors.exceptions import InvalidDescriptorError

from pyjon.descriptors.casters import Caster

log = logging.getLogger(__name__)

FALSE_VALUES = ['false', 'no', 'off', '0']
TRUE_VALUES = ['true', 'yes', 'on', '1']


def to_bool(value, false_values=None, true_values=None):
    if false_values is None:
        false_values = FALSE_VALUES

    if true_values is None:
        true_values = TRUE_VALUES

    if value.lower() in false_values:
        return False

    elif value.lower() in true_values:
        return True

    else:
        raise ValueError("%s could not be interpreted as boolean" % value)


class ItemFactory(object):
    def __init__(self, schemaroot, encoding, caster):
        """ a small factory that produces InputItems from csv rows.
        The only constraint is to feed it with some indexable (row will be
        accessed using the indexes from the schema)

        @param schemaroot: the root node of a descriptor schema that describes
        how to read the input stream.
        @type schemaroot: elementtree.Element node

        @param encoding: the encoding that was declared in the header of the
        stream. This encoding will be used to read the data.
        @type encoding: string

        @param caster: a caster instance that will transform arbitrary
        strings into python object
        @type caster: a spaceport.caster.Caster instance
        """
        self.schemaroot = schemaroot
        self.encoding = encoding
        self.caster = caster

        schema_fields = schemaroot.findall('fields/field')

        self.schema_fields = list()

        for field in schema_fields:
            type_node = field.find('type')
            prerenderer_node = field.find('prerenderer')
            type_dict = dict(name=type_node.text.lower().strip(),
                             items=dict(type_node.items()))

            field_dict = dict(name=field.get('name'),
                              type=type_dict,
                              index=int(field.find('source').text) - 1)

            if field_dict['name'] is None:
                msg = "Attribute name is missing from the field node"
                raise KeyError(msg)

            mandatory = field.get('mandatory')
            if mandatory is not None:
                field_dict['mandatory'] = to_bool(mandatory)
            else:
                msg = ("Attribute 'mandatory' is missing from "
                       "the field node %s" % field_dict['name'])
                raise KeyError(msg)

            strict_val = field.get('strict')
            if strict_val is None:
                strict_val = 'false'

            field_dict['strict'] = to_bool(strict_val)

            strip_val = field.get('strip')
            if strip_val is None:
                strip_val = 'true'

            field_dict['pre_strip'] = to_bool(strip_val)

            if prerenderer_node is not None:
                prerenderer_type = prerenderer_node.get('type')
                if prerenderer_type is None:
                    prerenderer_type = 'eval'

                if prerenderer_type not in ['eval', 'function']:
                    raise ValueError(
                        'prerenderer type value can be "eval" '
                        'or "function", not "%s"' % prerenderer_type
                    )

                field_dict['prerenderer_type'] = prerenderer_type
                field_dict['prerenderer_value'] = prerenderer_node.text
                if field_dict['prerenderer_type'] == 'function':
                    code_text = field_dict['prerenderer_value'].strip()
                    code_func_name = ast.parse(code_text).body[-1].name

                    code_content = compile(code_text, '<string>', 'exec')
                    evaldict = dict()
                    exec_(code_content, evaldict)
                    field_dict['prerenderer_function'] = evaldict[
                        code_func_name
                    ]

            length_node = field.find('length')
            if length_node is not None:
                field_dict['has_length'] = True
                field_dict['min_length'] = int(length_node.get('min') or 0)
                field_dict[
                    'max_length'
                ] = int(length_node.get('max') or 0) or None

            else:
                field_dict['has_length'] = False

            self.schema_fields.append(field_dict)

    def create_item(self, row, record_num=None):
        """ creates an item from a row or record

        @param row: a csv row
        @type row: anything that can be accessed by index to retrieve fields
        """
        item = InputItem()
        encoding = self.encoding
        caster = self.caster

        for field in self.schema_fields:
            raw_value = row[field['index']]

            if raw_value is not None:
                if field['pre_strip']:
                    raw_value = raw_value.strip()

                if 'prerenderer_value' in field:
                    if field['prerenderer_type'] == 'eval':
                        expression = field['prerenderer_value']
                        try:
                            raw_value = eval(expression)
                        except Exception as e:
                            # here we catch an reraise because exceptions will
                            # not be explicit enough and we need some
                            # information for debugging the error
                            raise ValueError(
                                'Error during evaluating '
                                'expression %s : %s' % (expression, str(e))
                            )

                    # render_type == "function" but we are protected by schema
                    # parser so we dont revalidate here
                    else:
                        # here we dont catch and reraise because exceptions
                        # will be explicit from the function code...
                        raw_value = field['prerenderer_function'](raw_value)

                # check length if the node was present
                if field['has_length']:
                    # max length is not always defined
                    if field['max_length']:
                        if len(raw_value) > field['max_length']:
                            msg = (
                                "Object length %s is over Max length %s "
                                "for field %s" % (
                                    len(raw_value),
                                    field['max_length'],
                                    field['name']
                                )
                            )
                            raise MaxLenError(msg)

                    # min length is always defined with a default to 0
                    if len(raw_value) < field['min_length']:
                        msg = (
                            "Object length %s is under Min length %s "
                            "for field %s" % (
                                len(raw_value),
                                field['min_length'],
                                field['name']
                            )
                        )
                        raise MinLenError(msg)

            if (raw_value == '' or raw_value is None) and field['mandatory']:
                msg = (
                    'Missing field or value: %s, '
                    'record: %s' % (
                        field['name'],
                        record_num or "unknown"
                    )
                )
                raise MissingFieldError(msg)

            else:
                # set a py_value
                py_value = None

            if raw_value is None:
                unicode_value = None
            else:
                if isinstance(raw_value, unicode if six.PY2 else str):
                    unicode_value = raw_value
                else:
                    unicode_value = raw_value.decode(encoding)
            try:
                py_value = caster.to_python(unicode_value, field['type'])

            except ValueError as e:
                # if field is not mandatory and value was blank,
                # then we have a already a py_value set to None
                # so we just let go of the exception
                if field['mandatory'] or (raw_value != '' and field['strict']):
                    raise ValueError(
                        '%s for field name: %s, record: %s' % (
                            e,
                            field['name'],
                            record_num or "unknown")
                    )

            setattr(item, field['name'], py_value)

        return item


class InputDialect(csv.Dialect):
    """A subclass of the csv.Dialect class"""

    def __init__(self, delimiter):
        """@param delimiter: the character to be used as a delimiter
        @type delimiter: string
        """
        self.delimiter = delimiter
        self.doublequote = True
        # in python 2.4 this cannot be None
        self.escapechar = '\\'
        self.lineterminator = '\r\n'
        self.quotechar = '"'
        self.quoting = csv.QUOTE_ALL
        self.skipinitialspace = False

        csv.Dialect.__init__(self)


class CSVReader(object):
    """a reader that specializes in csv interpretation and
    reading.
    The csv reader will set a 'data_row__' attribute on the produced
    items for consumption by the splitter if you specify the keep_source_ref
    flag.
    """
    def __init__(self, encoding, schema_root, keep_source_ref=True):
        """@param encoding: the encoding that was declared by the stream in its
        header. This will be used by our readers to handle characters.
        @type encoding: string

        @param schema_root: the schema root node as it was read from the xml
        file by an ET.parse() call
        @type schema_root: a xml.etree.ElementTree

        @param keep_source_ref: a flag to specifie if a reference to the csv
        row should be kept. The default value is True. BatchSplitters should
        specify this flag to True in order to be able to access the data.
        In a near future the default value may become false as soon as all
        splitters have switched the flag to their preferred value.

        @type keep_source_ref: Boolean
        """
        self.encoding = encoding
        self.caster = Caster()
        self.schema_root = schema_root
        self.keep_source_ref = keep_source_ref

        self.item_factory = ItemFactory(
            self.schema_root,
            self.encoding,
            self.caster
        )
        self.separator = self.schema_root.find('header/format/delimiter').text
        self.startline = int(self.schema_root.find(
            'header/format/startline'
        ).text)
        self.numcols = len(self.schema_root.findall('fields/field'))

    def read(self, source):
        """A specialized reader that interprets csv files
        use the schema to read the given stream. Yields
        InputItem instances that can be consumed.

        The file must have been opened in binary mode because
        the underliying module for csv support is encoding and format
        agnostic and must be able to interpret carriage returns and line
        feeds.

        @param source: the file-like stream to process
        @type source: file like object
        """
        return self.__read(source)

    def __read(self, source):
        """produces an iterator for the csv reader

        @param source: the file-like to process, it must be opened
        in 'rb' mode
        @type source: open file object
        """
        dialect = InputDialect(self.separator)
        numcols = self.numcols

        csv_reader = csv.reader(source, dialect)

        for row_index, row in enumerate(csv_reader):
            # log.debug('reading %s %s' % (row, len(row)))
            if row_index + 1 < self.startline:
                continue

            if len(row) == numcols:
                input_item = self.item_factory.create_item(
                    row, record_num=row_index + 1
                )

                if self.keep_source_ref:
                    # this is only used by the splitter
                    # no need to set this value in case we are
                    # not reading data for a splitter.
                    input_item.data_row__ = row

            else:
                msg = 'Line %s in source, as %s columns instead of %s' % (
                    row_index, len(row), numcols
                )
                if len(row) > numcols:
                    raise TooManyFieldsError(msg)
                else:
                    raise TooFewFieldsError(msg)

            yield input_item

    def get_record_count(self, source):
        count = 0
        for index, line in enumerate(source):
            if index + 1 < self.startline:
                continue
            count += 1
        source.seek(0)
        return count


class Field(object):
    pass


class XMLReader(object):
    def __init__(self, encoding, schema_root):
        self.encoding = encoding
        self.caster = Caster()
        self.schema_root = schema_root
        datanode = self.schema_root.find('header/datanode')
        if not hasattr(datanode, 'text'):
            msg = "The descriptor needs a datanode tag"
            raise InvalidDescriptorError(msg)

        self.datanode = datanode.text.strip()
        self.fields = list()
        schema_fields = self.schema_root.findall('fields/field')
        for field in schema_fields:
            f = Field()
            fm = field.attrib['mandatory']
            setattr(
                f,
                'mandatory',
                fm == 'true' or fm == 'True'
            )
            setattr(f, 'name', field.attrib['name'])
            setattr(f, 'source', field.find('source').text.strip())
            setattr(
                f,
                'type',
                dict(
                    name=field.find('type').text.strip(),
                    items=field.find('type').attrib
                )
            )
            self.fields.append(f)

    def read(self, source):
        return self.__read(source)

    def __read(self, source):
        record_num = 0

        steps = self.datanode.split('/')
        dataitem = steps[-1]
        steps = steps[:-1]

        flags = dict()
        for step in steps:
            flags[step] = False

        in_datazone = False

        context = etree.iterparse(source, events=("start", "end"))
        for action, elem in context:
            if action == 'start' and elem.tag in flags:
                flags[elem.tag] = True

                for flag in flags.values():
                    in_datazone = in_datazone or flag

            if action == 'end' and in_datazone and elem.tag == dataitem:
                record_num += 1
                input_item = InputItem()
                for field in self.fields:
                    child = None
                    children = elem.xpath(field.source)
                    if len(children):
                        child = children[0]

                    if field.mandatory and child is None:
                        msg = 'Missing field or value: %s, record: %s' % (
                            field.name, record_num or "unknown")
                        raise MissingFieldError(msg)

                    child_value = getattr(child, 'text', '').strip()

                    setattr(
                        input_item,
                        field.name,
                        self.caster.to_python(child_value, field.type)
                    )

                yield input_item

            if action == 'end' and elem.tag in flags:
                flags[elem.tag] = False
                in_datazone = False


class FixedLengthReader(object):
    """a reader that specializes in csv interpretation and
    reading.
    The csv reader will set a 'data_row__' attribute on the produced
    items for consumption by the splitter if you specify the keep_source_ref
    flag.
    """
    def __init__(
        self, encoding, schema_root, keep_source_ref=True, buffersize=16384
    ):
        """@param encoding: the encoding that was declared by the stream in its
        header. This will be used by our readers to handle characters.
        @type encoding: string

        @param schema_root: the schema root node as it was read from the xml
        file by an ET.parse() call
        @type schema_root: a xml.etree.ElementTree

        @param keep_source_ref: a flag to specifie if a reference to the csv
        row should be kept. The default value is True. BatchSplitters should
        specify this flag to True in order to be able to access the data.
        In a near future the default value may become false as soon as all
        splitters have switched the flag to their preferred value.

        @type keep_source_ref: Boolean
        """
        self.encoding = encoding
        self.buffersize = buffersize
        self.caster = Caster()
        self.schema_root = schema_root
        self.keep_source_ref = keep_source_ref

        log.debug('ItemFactory(%s, %s, %s)' % (
            self.schema_root,
            self.encoding,
            self.caster
        ))

        self.item_factory = ItemFactory(
            self.schema_root, self.encoding, self.caster
        )

    def read(self, source):
        """A specialized reader that interprets csv files
        use the schema to read the given stream. Yields
        InputItem instances that can be consumed.

        The file must have been opened in binary mode because
        the underliying module for csv support is encoding and format
        agnostic and must be able to interpret carriage returns and line
        feeds.

        @param source: the file-like stream to process
        @type source: file like object
        """
        return self.__read(source)

    def split_source(self, source, line_size):
        data_available = True
        remaining_data = u""

        while data_available:
            if hasattr(source, 'read'):
                data = source.read(self.buffersize)
            else:
                try:
                    data = next(source)
                except StopIteration:
                    data_available = False

            if not isinstance(data, unicode if six.PY2 else str):
                data = data.decode(self.encoding)

            if len(data) == 0 or not data_available:
                data_available = False

            data = remaining_data + data
            remaining_data = u""

            buffer = list()
            for i, v in enumerate(data):
                buffer.append(v)
                if not (i + 1) % line_size and not i == 0:
                    yield u"".join(buffer)
                    buffer = list()

            if len(buffer):
                remaining_data = u"".join(buffer)

        remaining_data = remaining_data.strip('\n\r')
        if len(remaining_data):
            raise RemainingDataError(remaining_data)

    def __read(self, source):
        """produces an iterator for the csv reader

        @param source: the file-like to process, it must be opened
        in 'rb' mode
        @type source: open file object
        """
        startline = int(self.schema_root.find('header/format/startline').text)
        # numcols = len(self.schema_root.findall('fields/field'))
        fields = self.schema_root.findall('fields/field')

        # Type : Integer, Define the number of characters for cutting
        splitlength = self.schema_root.find('header/format/splitlength')

        lengths = list()
        for field in fields:
            length_node = field.find('length')
            if length_node.text:
                lengths.append(int(length_node.text))
            else:
                raise ValueError(
                    'Descriptor should have length info '
                    'for fixed length reader'
                )

        total_length = sum(lengths)

        if splitlength is not None:
            splitlength_value = int(splitlength.text)
            source = self.split_source(source,
                                       splitlength_value)

        for row_index, line in enumerate(source):
            # log.debug('reading %s %s' % (row, len(row)))
            if row_index + 1 < startline:
                continue

            line = line.rstrip('\r\n')

            if len(line) == total_length:

                row = list()
                cur_pos = 0
                for length in lengths:
                    row_value = line[cur_pos:cur_pos + length]

                    row.append(row_value)
                    cur_pos += length

                input_item = self.item_factory.create_item(
                    row,
                    record_num=row_index + 1
                )

                if self.keep_source_ref:
                    # this is only used by the splitter
                    # no need to set this value in case we are
                    # not reading data for a splitter.
                    input_item.data_row__ = row

            else:
                msg = (
                    'Line %s in source, has %s characters '
                    'instead of %s' % (
                        row_index,
                        len(line),
                        total_length
                    )
                )
                if len(line) > total_length:
                    raise MaxLenError(msg)
                else:
                    raise MinLenError(msg)

            yield input_item

    def get_record_count(self, source):
        count = 0
        for line in source:
            count += 1
        if hasattr(source, 'seek'):
            source.seek(0)

        return count

"""the Descriptor implementation. A descriptor maintains information
about a file or flow and provides the necessary method to iterate over
the flow and return InputItems to be used in the rest of the process
"""

import logging
from six.moves import map
from six.moves import zip

from pyjon.descriptors.readers import CSVReader
from pyjon.descriptors.readers import FixedLengthReader
from pyjon.descriptors.readers import XMLReader

from itertools import tee, groupby
from operator import itemgetter

log = logging.getLogger(__name__)

try:
    from itertools import chain
    ichain = chain.from_iterable
except:  # pragma: no cover
    # versions of Python older than 2.6 do not have chain.from_iterable
    def ichain(iterator):
        for item_list in iterator:
            for item in item_list:
                yield item


class Descriptor(object):
    """a Descriptor object uses a schema to read a stream of file
    it will then yield InputItem instances that can be consumed
    by the internal parts of spaceport
    """
    def __init__(self, payload_tree, encoding, buffersize=16384):
        """@param payload_tree: the descriptor schema as an
        ElementTree instance
        @type payload_tree: ET.ElementTree instance

        @param encoding: the encoding of the stream to read (ie: 'utf-8')
        @type encoding: string

        @param buffersize: the desired size in bytes of the read buffer.
        This parameter will be ignored for csv readers and will be passed
        down to readers that implement their own buffering.
        This is an optionnal argument and will default to 16384.
        @type buffersize: integer
        """
        self.schema_root = payload_tree
        self.input_type = self.schema_root.find('header/format').get('name')
        reader_mode = self.schema_root.find('header/format').get('mode')

        if reader_mode is None:
            reader_mode = 'safe'

        if not (reader_mode == 'safe' or reader_mode == 'fast'):
            msg = 'the descriptor mode should be either'
            msg += ' fast or safe, not %s' % reader_mode
            raise ValueError(msg)

        self.conditional_descriptors = self.__get_conditional_descriptors(
            encoding, buffersize
        )

        if self.input_type == 'csv':
            log.debug("Starting CSVReader")
            self.reader = CSVReader(encoding, self.schema_root)

        elif self.input_type == 'xml':
            log.debug("Starting XMLReader")
            self.reader = XMLReader(encoding, self.schema_root)

        elif self.input_type == 'fixedlength':
            self.reader = FixedLengthReader(encoding, self.schema_root)

        else:
            msg = "The input type: '%s' " % self.input_type
            msg += "of this descriptor schema is unknown"
            log.error(msg)
            raise ValueError('unsupported input type: %s' % self.input_type)

    def __get_conditional_descriptors(self, encoding, buffersize):
        conditional_descriptors = list()

        field_nodes = self.schema_root.findall('fields/field')
        for field_node in field_nodes:
            if field_node.find('type') is None:
                raise ValueError(
                    "One of the fields in your descriptor misses a type node"
                )

            elif field_node.find('type').text.lower().strip() != 'descriptor':
                continue

            else:

                field_name = field_node.get('name')

                # Ugly rewrite of type. It is unfortunately necessary
                # as we will then pass this field to a subdescriptor
                field_node.find('type').text = 'string'

                descriptors_nodes = field_node.findall('descriptor')
                for descriptor_node in descriptors_nodes:
                    condition = descriptor_node.get("condition")

                    desc = dict()
                    desc['condition'] = condition
                    desc['field_name'] = field_name
                    desc['descriptor'] = Descriptor(
                        descriptor_node,
                        encoding,
                        buffersize=buffersize
                    )
                    conditional_descriptors.append(desc)

        return conditional_descriptors

    def read(self, source):
        """reads the source and returns InputItems instances
        @param source: the source stream to read from
        @type source: a file like object
        """
        return self.__read(source)

    def __read(self, source):
        """the generator that yields items for real
        @param source: the source stream to read from
        @type source: a file like object
        """

        main_flow = self.reader.read(source)

        if len(self.conditional_descriptors):
            def apply_condition(condition_set, flow):
                for item in flow:
                    if eval(condition_set.get('condition', "True")):
                        value = list(
                            condition_set.get(
                                'descriptor'
                            ).read(
                                [getattr(
                                    item,
                                    condition_set.get('field_name')
                                )]
                            ))[0]
                        setattr(item, condition_set.get('field_name'), value)

                    yield item

            iterators = tee(main_flow, len(self.conditional_descriptors))
            iterators = [
                apply_condition(
                    self.conditional_descriptors[it], citer
                ) for it, citer in enumerate(list(iterators))
            ]

            final_iterator = groupby(ichain(zip(*iterators)))

            final_iterator = map(itemgetter(0), final_iterator)

            main_flow = final_iterator

        return main_flow

    def get_record_count(self, source):
        """ asks the reader to pre-read the file to get the record count.
        Then, it does a seek(0) on the file to give a fresh file """
        if hasattr(self.reader, 'get_record_count'):
            return self.reader.get_record_count(source)
        else:  # pragma: no cover
            return None

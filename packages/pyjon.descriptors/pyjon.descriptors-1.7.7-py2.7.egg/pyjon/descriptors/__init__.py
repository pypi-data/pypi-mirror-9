"""the descriptor module provides a way to read an input stream
an get a black box called an InputItem, which can be used to isolate
the other parts of your apps from the reading/interpreting parts
of the job.
"""

# flake8: noqa

from pyjon.descriptors.main import Descriptor
from pyjon.descriptors.input import InputItem
from pyjon.descriptors.readers import CSVReader

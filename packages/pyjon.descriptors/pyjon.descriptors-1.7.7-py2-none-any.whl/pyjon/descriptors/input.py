"""InputItems are yielded by the descriptor
an InputItem instance has an arbitrary number
of attributes that are described in the schema.
"""

from operator import itemgetter
import six
from six import next
from six.moves import map

__all__ = ['InputItem']


class InputItem(object):
    """a black box that contains the attributes defined in a schema"""

    def __repr__(self):
        return repr(self.__dict__)

    def iteritems(self):
        for k, v in six.iteritems(self.__dict__):
            if not callable(v) and not k.startswith('__'):
                yield (k, v)

    def iterkeys(self):
        return map(itemgetter(0), self.iteritems())

    __iter__ = iterkeys

    def itervalues(self):
        return map(itemgetter(1), self.iteritems())

    def __getitem__(self, key, default=None):
        return getattr(self, key, default)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def items(self):
        return list(self.iteritems())

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    def __len__(self):
        return len(self.keys())

    def __delitem__(self, key):
        """Warning this method will silently bypass missing keys
        """
        if key in self:
            return delattr(self, key)
        else:
            pass

    def has_key(self, key):
        return key in self.keys()

    def pop(self, key, default=None):
        val = self.__getitem__(key, default)
        self.__delitem__(key)
        return val

    def popitem(self):
        val = next(self.iteritems())
        del self[val[0]]
        return val

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        else:
            self[key] = default
            return self[key]

    def update(self, *args, **kwargs):
        if len(args):
            dictionnary = args[0]
        elif len(kwargs):
            dictionnary = kwargs
        else:
            raise ValueError(
                "Please provide an iterator, a dictionnary, "
                "or keyword arguments to update function"
            )

        if isinstance(dictionnary, dict):
            dictionnary = six.iteritems(dictionnary)
        else:
            raise TypeError("update must receive a dictionary")

        for key, value in dictionnary:
            self[key] = value

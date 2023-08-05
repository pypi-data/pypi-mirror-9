"""test the input item mechanism
"""
from pyjon.descriptors import InputItem
import unittest


class TestInputItem(unittest.TestCase):
    def test_inputitem_instanciation(self):
        """inputitem: make sure we can instanciate
        """
        i = InputItem()
        assert isinstance(i, InputItem), 'InputItem should instanciate'

    def test_inputitem_attrs(self):
        """inputitem: make sure an attribute stays in place
        """
        i = InputItem()
        i.testattr = 3
        assert i.testattr == 3, 'setattr works'

    def test_inputitem_setasdict(self):
        """inputitem: test the setting of attrs as on dicts"""
        i = InputItem()
        i['testkey'] = 'testvalue'

        assert i.testkey == 'testvalue'

    def test_inputitem_getasdict(self):
        """inputitem: test the getting as a dict"""
        i = InputItem()
        i.testkey = 'testvalue'
        assert i['testkey'] == 'testvalue'

    def test_inputitem_iter(self):
        """inputitem: test update with dict iteration"""
        i = InputItem()
        data = dict(a='1', b='2', c='3', d='4')
        i.update(data)

        assert 'a' in i
        assert 'b' in i
        assert 'c' in i
        assert 'd' in i

        assert i['a'] == '1'
        assert i.b == '2'
        assert i['c'] == '3'
        assert i.d == '4'

    def test_inputitem_len(self):
        """inputitem: test len implementation
        """
        i = InputItem()
        data = dict(a='1', b='2', c='3', d='4')
        i.update(data)

        assert len(i) == 4, "input item len should return 4 not %s" % len(i)

    def test_inputitem_haskey(self):
        """inputitem: test has_key implementation
        """
        i = InputItem()
        data = dict(a='1', b='2', c='3', d='4')
        i.update(data)

        assert 'b' in i, "input item should have key 'b'"

    def test_inputitem_pop(self):
        """inputitem: test len implementation
        """
        i = InputItem()
        data = dict(a='1', b='2', c='3', d='4')
        i.update(data)

        pvalue = i.pop('a')

        assert len(i) == 3, "input item len should return 3 not %s" % len(i)
        assert pvalue == '1', "Popped value should be '1', not %s" % pvalue
        assert 'a' not in i, "'a' should not be in inputitem any more"

    def test_items(self):
        i = InputItem()
        i.update(
            {
                'a': 1,
            }
        )

        for k, v in i.items():
            self.assertEquals(k, 'a')
            self.assertEquals(v, 1)

    def test_items_with_private_callable(self):
        i = InputItem()
        i.update(
            dict(
                __a=lambda a: a ** 2
            )
        )

        for k, v in i.items():
            self.assertEquals(k, 'a')
            self.assertEquals(v, 1)

    def test_values(self):
        i = InputItem()
        i.update(
            {
                'a': 1,
                'b': 1,
            }
        )

        for v in i.values():
            self.assertEquals(v, 1)

    def test_pop_nonexistant(self):
        i = InputItem()
        i.update(
            {
                'a': 1,
                'b': 1,
            }
        )

        self.assertEquals(i.pop('c', default=42), 42)

    def test_haskey(self):
        i = InputItem()
        i.update(
            {
                'a': 1,
                'b': 1,
            }
        )

        self.assertTrue('b' in i)

    def test_setdefault_existing(self):
        i = InputItem()
        i.update(
            {
                'a': 1,
            }
        )
        self.assertEquals(i.setdefault('a', default=3), 1)

    def test_setdefault_nonexisting(self):
        i = InputItem()
        i.update(
            {
                'a': 1,
            }
        )
        self.assertEquals(i.setdefault('b', default=3), 3)

    def test_popitem(self):
        i = InputItem()
        i.update(
            {
                'a': 1,
            }
        )
        self.assertEquals(i.popitem(), ('a', 1))

    def test_update_kwargs(self):
        i = InputItem()
        kw = {'a': 1, 'b': 2}
        i.update(**kw)

        self.assertEquals(i['a'], 1)
        self.assertEquals(i['b'], 2)

    def test_update_arg_not_dict(self):
        i = InputItem()
        self.assertRaises(TypeError, i.update, ['a'])

    def test_update_raises(self):
        i = InputItem()
        self.assertRaises(ValueError, i.update)

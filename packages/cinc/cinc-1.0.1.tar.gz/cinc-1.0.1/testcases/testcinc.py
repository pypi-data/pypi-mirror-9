import unittest
import unittest.mock
import pickle

from cinc import *


class CincTestCase(unittest.TestCase):
    def test_default_construction(self):
        '''Test if integers are default contructed to 0'''
        value = uint32()
        self.assertEqual(value, uint32(0))

    def test_int_casting(self):
        '''Test if integers can be converted to int'''
        value = uint32(1)
        self.assertEqual(int(value), 1)

    def test_casting(self):
        '''Test casting between signed and unsigned integers'''
        value = int32(-1)
        self.assertEqual(value, uint32(0xFFFFFFFF))

    def test_int_casting_caching(self):
        '''Test if casted ints are cached'''
        value = uint32(1)
        self.assertIs(int(value), int(value))

    def test_str(self):
        '''Test converting to str'''
        value = uint32(0)
        self.assertEqual(str(value), '0')

    def test_repr(self):
        '''Test repr conversion'''
        value = uint32(0)
        self.assertEqual(repr(value), 'cinc.uint32(0)')

    def test_8bit_str(self):
        '''Test conversion to str for char'''
        self.assertEqual(str(int8()), '0')
        self.assertEqual(str(uint8()), '0')

    def test_8bit_repr(self):
        '''Test repr conversion for char'''
        self.assertEqual(repr(int8()), 'cinc.int8(0)')
        self.assertEqual(repr(uint8()), 'cinc.uint8(0)')

    def test_hash(self):
        '''Test hash function'''
        value = uint32(0xFFFF)
        self.assertEqual(hash(value), 0xFFFF)

    def test_hash_negative_one(self):
        '''Check that __hash__ does not return -1'''
        value = uint32(-1)
        self.assertNotEqual(hash(value), 0xFFFFFFFF)
        value = int32(-1)
        self.assertNotEqual(hash(value), -1)

    def test_bool(self):
        '''Test boolean conversion'''
        value = uint32(1)
        self.assertTrue(value)
        value = uint32(0)
        self.assertFalse(value)

    def test_pickle(self):
        '''Test if cinc types can be pickled'''
        data = pickle.dumps(uint32(1))
        value = pickle.loads(data)
        self.assertEqual(value, uint32(1))


class CincOperatorTestCase(unittest.TestCase):
    def test_equals(self):
        '''Test if equals operator works'''
        self.assertEqual(uint32(1), uint32(1))

    def test_zero_division(self):
        '''Test if division by zero raises ZeroDivisionError'''
        with self.assertRaises(ZeroDivisionError):
            uint32(1) // uint32(0)

    def test_zero_modulo(self):
        '''Test if modulo by zero raises ZeroDivisionError'''
        with self.assertRaises(ZeroDivisionError):
            uint32(1) % uint32(0)

    def test_zero_divmod(self):
        '''Test if divmod by zero raises ZeroDivisionError'''
        with self.assertRaises(ZeroDivisionError):
            divmod(uint32(1), uint32(0))

    def test_power(self):
        '''Test if power operator works'''
        self.assertEqual(pow(int32(0), int32(0)), int32(1))
        self.assertEqual(pow(int32(0), int32(1)), int32(0))
        self.assertEqual(pow(int32(1), int32(0)), int32(1))
        self.assertEqual(pow(int32(1), int32(1)), int32(1))

        self.assertEqual(pow(int32(2), int32(0)), int32(1))
        self.assertEqual(pow(int32(2), int32(10)), int32(1024))
        self.assertEqual(pow(int32(2), int32(20)), int32(1024 * 1024))
        self.assertEqual(pow(int32(2), int32(30)), int32(1024 * 1024 * 1024))

        self.assertEqual(pow(int32(-2), int32(0)), int32(1))
        self.assertEqual(pow(int32(-2), int32(1)), int32(-2))
        self.assertEqual(pow(int32(-2), int32(2)), int32(4))
        self.assertEqual(pow(int32(-2), int32(3)), int32(-8))

        self.assertEqual(pow(int32(2), int32(10), int32(1000)), int32(24))

        self.assertRaises(TypeError, pow, int32(-1), int32(-2), int32(3))
        self.assertRaises(ValueError, pow, int32(1), int32(2), int32(0))

    def test_derived_class_operator_construction(self):
        '''Test if operators in derived classes run __init__'''
        class Derived(uint32):
            pass
        value = Derived(2)
        Derived.__init__ = unittest.mock.Mock(return_value=None)
        value + value
        Derived.__init__.assert_called_with(4)


class CincMethodTestCase(unittest.TestCase):
    def test_extract(self):
        value = uint32(0xFFFF0000)
        self.assertEqual(value.extract(8, 16), uint32(0xFF00))

    def test_insert(self):
        value = uint32(0xFF000000)
        self.assertEqual(value.insert(uint32(0xFF00), 8, 16),
                         uint32(0xFFFF0000))

    def test_lrotate(self):
        value = uint32(0xFF0000FF)
        self.assertEqual(value.lrotate(8), uint32(0x0000FFFF))

    def test_rrotate(self):
        value = uint32(0xFF0000FF)
        self.assertEqual(value.rrotate(8), uint32(0xFFFF0000))

    def test_signed_lrotate(self):
        value = int32(0xFF0000FF)
        self.assertEqual(value.lrotate(8), int32(0x0000FFFF))

    def test_signed_rrotate(self):
        value = int32(0xFF0000F0)
        self.assertEqual(value.rrotate(8), int32(0xF0FF0000))

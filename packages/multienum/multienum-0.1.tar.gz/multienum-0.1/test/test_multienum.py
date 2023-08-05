# pylint: disable=E1101,W0612,W0232,F0401

import unittest
import multienum


class EmptyEnum(multienum.MultiEnum):
    pass

class TestEnum(multienum.MultiEnum):
    _members = (
        ("zero", "none", "zilch"),
        ("one", "single", "uno"),
        ("two", "deuce", "a couple"),
        ("three", "a few", "trio")
    )
    _fields = ("first", "second")
        

class MultiEnumTest(unittest.TestCase):
    def test_multienum_init(self):
        enum = TestEnum("zero")
        self.assertEqual(int(enum), 0)
        self.assertIsInstance(enum, TestEnum)
        self.assertEqual(enum.name, "zero")

    def test_empty_multienum(self):
        with self.assertRaises(TypeError):
            enum = EmptyEnum("bogus")


    def test_missing_value(self):
        with self.assertRaises(AttributeError):
            enum = TestEnum("fifteen")


    def test_secondary_fields(self):
        enum = TestEnum(0)
        self.assertEqual(enum.second, "none")

    def test_as_str(self):
        self.assertEqual("two", str(TestEnum(2)))
        self.assertEqual("three", str(TestEnum('a few')))


    def test_multi_args(self):
        self.assertEqual(2, int(TestEnum(2, "two")))
        self.assertRaises(ValueError, TestEnum, 2, "zero")

    def test_kwarg(self):
        enum = TestEnum(second="deuce")
        self.assertEqual(2, int(enum))
        self.assertEqual('two', str(enum))
        self.assertEqual('deuce', enum.second)
        self.assertRaises(ValueError, TestEnum, 2, first="zero")
        self.assertEqual(2, int(TestEnum(2, first="two")))

    def test_idempotent(self):
        s = TestEnum(2)
        self.assertIs(s, TestEnum(s))
        self.assertIs(s, TestEnum(s, 2))

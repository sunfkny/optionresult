import contextlib
import io
import typing as t
import unittest

from optionresult import Err, Ok, Option

UInt32 = t.NewType("UInt32", int)


def to_uint32(value: int) -> UInt32:
    if value < 0 or value > 2**32 - 1:
        raise ValueError("value out of range")
    return UInt32(value)


class TestOption(unittest.TestCase):
    def test_dunder_eq(self):
        self.assertTrue(Option(2) == Option(2))
        self.assertTrue(Option(None) == Option(None))
        self.assertFalse(Option(2) == 2)

    def test_dunder_repr(self):
        self.assertEqual(repr(Option(2)), "Some(2)")
        self.assertEqual(repr(Option("foo")), "Some('foo')")
        self.assertEqual(repr(Option(None)), "None")

    def test_is_some(self):
        self.assertTrue(Option(2).is_some())
        self.assertFalse(Option(None).is_some())

    def test_is_some_and(self):
        self.assertTrue(Option(2).is_some_and(lambda x: x > 0))
        self.assertFalse(Option(2).is_some_and(lambda x: x < 0))
        self.assertFalse(Option(None).is_some_and(lambda x: x > 0))
        self.assertFalse(Option(None).is_some_and(lambda x: x < 0))

    def test_is_none(self):
        self.assertFalse(Option(2).is_none())
        self.assertTrue(Option(None).is_none())

    def test_expect(self):
        self.assertEqual(Option("value").expect("error"), "value")
        with self.assertRaises(ValueError) as context:
            Option(None).expect("fruits are healthy")
        self.assertEqual("fruits are healthy", str(context.exception))

    def test_unwrap(self):
        self.assertEqual(Option("air").unwrap(), "air")
        with self.assertRaises(RuntimeError) as context:
            Option(None).unwrap()
        self.assertEqual("called `Option.unwrap()` on a `None` value", str(context.exception))

    def test_unwrap_or(self):
        self.assertEqual(Option("car").unwrap_or("bike"), "car")
        self.assertEqual(Option(None).unwrap_or("bike"), "bike")

    def test_unwrap_or_else(self):
        k = 10
        self.assertEqual(Option(4).unwrap_or_else(lambda: 2 * k), 4)
        self.assertEqual(Option(None).unwrap_or_else(lambda: 2 * k), 20)

    def test_map(self):
        self.assertEqual(Option("Hello, World!").map(lambda x: len(x)), Option(13))
        self.assertEqual(Option(None).map(lambda x: len(x)), Option(None))

    def test_inspect(self):
        v = [1, 2, 3, 4, 5]

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            Option.of(lambda: v[3]).inspect(lambda x: print(f"got: {x}"))
        self.assertEqual(f.getvalue(), "got: 4\n")

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            Option.of(lambda: v[5]).inspect(lambda x: print(f"got: {x}"))
        self.assertEqual(f.getvalue(), "")

    def test_map_or(self):
        self.assertEqual(Option("foo").map_or(42, len), 3)
        self.assertEqual(Option(None).map_or(42, len), 42)

    def test_map_or_else(self):
        k = 21
        self.assertEqual(Option("foo").map_or_else(lambda: 2 * k, len), 3)
        self.assertEqual(Option(None).map_or_else(lambda: 2 * k, len), 42)

    def test_ok_or(self):
        self.assertEqual(Option("foo").ok_or(0), Ok("foo"))
        self.assertEqual(Option(None).ok_or(0), Err(0))

    def test_ok_or_else(self):
        self.assertEqual(Option("foo").ok_or_else(lambda: 0), Ok("foo"))
        self.assertEqual(Option(None).ok_or_else(lambda: 0), Err(0))

    def test_and_(self):
        self.assertEqual(Option(2).and_(Option(None)), Option(None))
        self.assertEqual(Option(None).and_(Option("foo")), Option(None))
        self.assertEqual(Option(2).and_(Option("foo")), Option("foo"))
        self.assertEqual(Option(None).and_(Option(None)), Option(None))

        self.assertEqual(Option(2) & Option(None), Option(None))
        self.assertEqual(Option(None) & Option("foo"), Option(None))
        self.assertEqual(Option(2) & Option("foo"), Option("foo"))
        self.assertEqual(Option(None) & Option(None), Option(None))

    def test_and_then(self):
        def sq_then_to_string(x: UInt32) -> Option[str]:
            return Option.of(lambda: to_uint32(x * x)).map(str)

        self.assertEqual(Option(to_uint32(2)).and_then(sq_then_to_string), Option("4"))
        self.assertEqual(Option(to_uint32(1_000_000)).and_then(sq_then_to_string), Option(None))
        self.assertEqual(Option(None).and_then(sq_then_to_string), Option(None))

        arr_2d = [["A0", "A1"], ["B0", "B1"]]
        item_0_1 = Option.of(lambda: arr_2d[0]).and_then(lambda row: Option.of(lambda: row[1]))
        self.assertEqual(item_0_1, Option("A1"))
        item_1_0 = Option.of(lambda: arr_2d[2]).and_then(lambda row: Option.of(lambda: row[0]))
        self.assertEqual(item_1_0, Option(None))

    def test_filter(self):
        def is_even(x: int) -> bool:
            return x % 2 == 0

        self.assertEqual(Option(None).filter(is_even), Option(None))
        self.assertEqual(Option(3).filter(is_even), Option(None))
        self.assertEqual(Option(4).filter(is_even), Option(4))

    def test_or_(self):
        self.assertEqual(Option(2).or_(Option(None)), Option(2))
        self.assertEqual(Option(None).or_(Option(100)), Option(100))
        self.assertEqual(Option(2).or_(Option(100)), Option(2))
        self.assertEqual(Option(None).or_(Option(None)), Option(None))

        self.assertEqual(Option(2) | Option(None), Option(2))
        self.assertEqual(Option(None) | Option(100), Option(100))
        self.assertEqual(Option(2) | Option(100), Option(2))
        self.assertEqual(Option(None) | Option(None), Option(None))

    def test_or_else(self):
        def nobody() -> Option[str]:
            return Option(None)

        def vikings() -> Option[str]:
            return Option("vikings")

        self.assertEqual(Option("barbarians").or_else(vikings), Option("barbarians"))
        self.assertEqual(Option(None).or_else(vikings), Option("vikings"))
        self.assertEqual(Option(None).or_else(nobody), Option(None))

    def test_xor(self):
        self.assertEqual(Option(2).xor(Option(None)), Option(2))
        self.assertEqual(Option(None).xor(Option(2)), Option(2))
        self.assertEqual(Option(2).xor(Option(2)), Option(None))
        self.assertEqual(Option(None).xor(Option(None)), Option(None))

        self.assertEqual(Option(2) ^ Option(None), Option(2))
        self.assertEqual(Option(None) ^ Option(2), Option(2))
        self.assertEqual(Option(2) ^ Option(2), Option(None))
        self.assertEqual(Option(None) ^ Option(None), Option(None))

import contextlib
import io
import typing as t
import unittest

from optionresult import Err, Ok, Option, Result, PanicError

UInt32 = t.NewType("UInt32", int)


def to_uint32(value: int) -> UInt32:
    if value < 0 or value > 2**32 - 1:
        raise ValueError("value out of range")
    return UInt32(value)


class TestResult(unittest.TestCase):
    def test_dunder(self):
        self.assertEqual(Ok(2), Ok(2))
        self.assertEqual(Err("error"), Err("error"))
        self.assertNotEqual(Ok(2), 2)
        self.assertNotEqual(Err("error"), Ok(2))
        self.assertNotEqual(Err("error1"), Err("error2"))
        self.assertEqual(repr(Ok(2)), "Ok(2)")
        self.assertEqual(repr(Err("error")), "Err('error')")

    def test_of(self):
        self.assertEqual(Result.of(lambda: 123), Ok(123))

        def raise_error():
            raise ValueError("error")

        x = Result.of(raise_error)
        self.assertEqual(x, Err(ValueError("error")))

    def test_is_ok(self):
        self.assertTrue(Ok(-3).is_ok())
        self.assertFalse(Err("Some error message").is_ok())

    def test_is_ok_and(self):
        self.assertTrue(Ok(2).is_ok_and(lambda x: x > 1))
        self.assertFalse(Ok(0).is_ok_and(lambda x: x > 1))
        self.assertFalse(Err("hey").is_ok_and(lambda x: x > 1))

    def test_is_err(self):
        self.assertFalse(Ok(-3).is_err())
        self.assertTrue(Err("Some error message").is_err())

    def test_is_err_and(self):
        class NotFoundError(Exception):
            pass

        class PermissionDeniedError(Exception):
            pass

        self.assertTrue(Err(NotFoundError("!")).is_err_and(lambda x: isinstance(x, NotFoundError)))
        self.assertFalse(Err(PermissionDeniedError("!")).is_err_and(lambda x: isinstance(x, NotFoundError)))
        self.assertFalse(Ok(123).is_err_and(lambda x: isinstance(x, NotFoundError)))

    def test_ok(self):
        self.assertEqual(Ok(2).ok(), Option(2))
        self.assertEqual(Err("Nothing here").ok(), Option(None))

    def test_err(self):
        self.assertEqual(Ok(2).err(), Option(None))
        self.assertEqual(Err("Nothing here").err(), Option("Nothing here"))

    def test_map(self):
        f = io.StringIO()
        line = "1\n2\n3\n4\na\nb\nc\nd\n"
        with contextlib.redirect_stdout(f):
            for num in line.splitlines():
                r = Result[int, Exception].of(lambda: int(num)).map(lambda i: i * 2)
                match r:
                    case Ok(n):
                        print(n)
                    case Err():
                        pass
                    case _:  # pragma: no cover
                        assert False, "unreachable"

        self.assertEqual(f.getvalue(), "2\n4\n6\n8\n")

    def test_map_or(self):
        self.assertEqual(Ok("foo").map_or(42, len), 3)
        self.assertEqual(Err("bar").map_or(42, len), 42)

    def test_map_or_else(self):
        k = 21
        self.assertEqual(Ok("foo").map_or_else(lambda e: k * 2, len), 3)
        self.assertEqual(Err("bar").map_or_else(lambda e: k * 2, len), 42)

    def test_map_err(self):
        def stringify(x: int) -> str:
            return f"error code: {x}"

        self.assertEqual(Ok(2).map_err(stringify), Ok(2))
        self.assertEqual(Err(13).map_err(stringify), Err("error code: 13"))

    def test_inspect(self):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            x = (
                Result.of(lambda: int("4"))
                .inspect(lambda x: print(f"original: {x}"))
                .map(lambda x: x**3)
                .expect("failed to parse number")
            )
        self.assertEqual(x, 64)
        self.assertEqual(f.getvalue(), "original: 4\n")

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            Err(1).inspect(lambda x: print(f"error: {x}"))
        self.assertEqual(f.getvalue(), "")

    def test_inspect_err(self):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            Result.of(lambda: open("address.txt", "r")).inspect_err(lambda e: print(f"failed to read file: {e}"))
        self.assertEqual(f.getvalue(), "failed to read file: [Errno 2] No such file or directory: 'address.txt'\n")

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            Ok(2).inspect_err(lambda e: print(f"failed to read file: {e}"))
        self.assertEqual(f.getvalue(), "")

    def test_expect(self):
        with self.assertRaises(PanicError) as context:
            Err("emergency failure").expect("Testing expect")
        self.assertEqual("Testing expect: emergency failure", str(context.exception))

    def test_unwrap(self):
        self.assertEqual(Ok(2).unwrap(), 2)
        with self.assertRaises(PanicError) as context:
            Err("emergency failure").unwrap()
        self.assertEqual("emergency failure", str(context.exception))

    def test_expect_err(self):
        with self.assertRaises(PanicError) as context:
            Ok(10).expect_err("Testing expect_err")
        self.assertEqual("Testing expect_err: 10", str(context.exception))

        self.assertEqual(Err(10).expect_err("Testing expect_err"), 10)

    def test_unwrap_err(self):
        with self.assertRaises(PanicError) as context:
            Ok(2).unwrap_err()
        self.assertEqual("2", str(context.exception))
        self.assertEqual(Err("emergency failure").unwrap_err(), "emergency failure")

    def test_and_(self):
        self.assertEqual(Ok(2).and_(Err("late error")), Err("late error"))
        self.assertEqual(Err("early error").and_(Ok("foo")), Err("early error"))
        self.assertEqual(Err("not a 2").and_(Err("late error")), Err("not a 2"))
        self.assertEqual(Ok(2).and_(Ok("different result type")), Ok("different result type"))

        self.assertEqual(Ok(2) & Err("late error"), Err("late error"))
        self.assertEqual(Err("early error") & Ok("foo"), Err("early error"))
        self.assertEqual(Err("not a 2") & Err("late error"), Err("not a 2"))
        self.assertEqual(Ok(2) & Ok("different result type"), Ok("different result type"))

    def test_and_then(self):
        def sq_then_to_string(x: UInt32) -> Result[str, str]:
            return Option.of(lambda: to_uint32(x * x)).map(str).ok_or("overflowed")

        self.assertEqual(Ok(to_uint32(2)).and_then(sq_then_to_string), Ok("4"))
        self.assertEqual(Ok(to_uint32(1_000_000)).and_then(sq_then_to_string), Err("overflowed"))
        self.assertEqual(Err("not a number").and_then(sq_then_to_string), Err("not a number"))

    def test_or_(self):
        self.assertEqual(Ok(2).or_(Err("late error")), Ok(2))
        self.assertEqual(Err("early error").or_(Ok(2)), Ok(2))
        self.assertEqual(Err("not a 2").or_(Err("late error")), Err("late error"))
        self.assertEqual(Ok(2).or_(Ok(100)), Ok(2))

        self.assertEqual(Ok(2) | Err("late error"), Ok(2))
        self.assertEqual(Err("early error") | Ok(2), Ok(2))
        self.assertEqual(Err("not a 2") | Err("late error"), Err("late error"))
        self.assertEqual(Ok(2) | Ok(100), Ok(2))

    def test_or_else(self):
        def sq(x: int) -> Result[int, int]:
            return Ok(x * x)

        def err(x: int) -> Result[int, int]:
            return Err(x)

        self.assertEqual(Ok(2).or_else(sq).or_else(sq), Ok(2))
        self.assertEqual(Ok(2).or_else(err).or_else(sq), Ok(2))
        self.assertEqual(Err(3).or_else(sq).or_else(err), Ok(9))
        self.assertEqual(Err(3).or_else(err).or_else(err), Err(3))

    def test_unwrap_or(self):
        self.assertEqual(Ok(9).unwrap_or(2), 9)
        self.assertEqual(Err("error").unwrap_or(2), 2)

    def test_unwrap_or_else(self):
        self.assertEqual(Ok(2).unwrap_or_else(len), 2)
        self.assertEqual(Err("foo").unwrap_or_else(len), 3)

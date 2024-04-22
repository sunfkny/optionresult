from __future__ import annotations
import typing as t
from .exceptions import PanicError

if t.TYPE_CHECKING:
    from .option import Option  # pragma: no cover

T = t.TypeVar("T")
U = t.TypeVar("U")
E = t.TypeVar("E")
R = t.TypeVar("R")
F = t.TypeVar("F")


def is_same_exception(exc1: Exception, exc2: Exception) -> bool:
    return type(exc1) == type(exc2) and exc1.args == exc2.args


class Result(t.Generic[T, E]):
    __match_args__ = ("value",)

    @staticmethod
    def of(
        fn: t.Callable[..., U],
        *args: t.Any,
        catch: t.Type[F] = Exception,
        **kwargs: t.Any,
    ) -> Ok[U, F] | Err[U, F]:
        try:
            return Ok(fn(*args, **kwargs))
        except catch as exc:
            return Err(exc)

    def __init__(self, value: T | E):
        raise NotImplementedError

    def is_ok(self) -> bool:
        raise NotImplementedError

    def is_ok_and(self, f: t.Callable[[T], bool]) -> bool:
        raise NotImplementedError

    def is_err(self) -> bool:
        raise NotImplementedError

    def is_err_and(self, f: t.Callable[[E], bool]) -> bool:
        raise NotImplementedError

    def ok(self) -> Option[T]:
        raise NotImplementedError

    def err(self) -> Option[E]:
        raise NotImplementedError

    def map(self, f: t.Callable[[T], U]) -> Ok[U, E] | Err[T, E]:
        raise NotImplementedError

    def map_or(self, default: U, f: t.Callable[[T], U]) -> U:
        raise NotImplementedError

    def map_or_else(self, default: t.Callable[[E], U], f: t.Callable[[T], U]) -> U:
        raise NotImplementedError

    def map_err(self, op: t.Callable[[E], F]) -> Ok[T, E] | Err[T, F]:
        raise NotImplementedError

    def inspect(self, f: t.Callable[[T], None]) -> Ok[T, E] | Err[T, E]:
        raise NotImplementedError

    def inspect_err(self, f: t.Callable[[E], None]) -> Ok[T, E] | Err[T, E]:
        raise NotImplementedError

    def expect(self, msg: str) -> T | t.NoReturn:
        raise NotImplementedError

    def unwrap(self) -> T | t.NoReturn:
        raise NotImplementedError

    def expect_err(self, msg: str) -> t.NoReturn | E:
        raise NotImplementedError

    def unwrap_err(self) -> t.NoReturn | E:
        raise NotImplementedError

    def and_(self, resb: Ok[U, F] | Err[U, F] | Result[U, F]) -> Ok[U, F] | Err[U, F] | Result[U, F]:
        raise NotImplementedError

    def and_then(self, f: t.Callable[[T], Ok | Err | Result]) -> Ok | Err | Result:
        raise NotImplementedError

    def or_(self, res: Ok | Err | Result) -> Ok | Err | Result:
        raise NotImplementedError

    def __or__(self, res: Ok | Err | Result) -> Ok | Err | Result:
        raise NotImplementedError

    def or_else(self, op: t.Callable[[E], Ok | Err | Result]) -> Ok | Err | Result:
        raise NotImplementedError

    def unwrap_or(self, default: T) -> T:
        raise NotImplementedError

    def unwrap_or_else(self, f: t.Callable[[E], T]) -> T:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError


class Ok(Result[T, E]):
    def __init__(self, value: T) -> None:
        self.value = value

    def is_ok(self) -> bool:
        return True

    def is_ok_and(self, f: t.Callable[[T], bool]) -> bool:
        return f(self.unwrap())

    def is_err(self) -> bool:
        return False

    def is_err_and(self, f: t.Callable[[E], bool]) -> bool:
        return self.is_err() and f(self.unwrap_err())

    def ok(self) -> Option[T]:
        from .option import Option

        return Option(self.unwrap())

    def err(self) -> Option[E]:
        from .option import Option

        return Option(None)

    def map(self, f: t.Callable[[T], U]) -> Ok[U, E]:
        return Ok(f(self.unwrap()))

    def map_or(self, default: U, f: t.Callable[[T], U]) -> U:
        return f(self.unwrap())

    def map_or_else(self, default: t.Callable[[E], U], f: t.Callable[[T], U]) -> U:
        return f(self.unwrap())

    def map_err(self, op: t.Callable[[E], F]) -> Ok[T, E]:
        return self

    def inspect(self, f: t.Callable[[T], None]) -> Ok[T, E]:
        f(self.unwrap())
        return self

    def inspect_err(self, f: t.Callable[[E], None]) -> Ok[T, E]:
        return self

    def expect(self, msg: str) -> T:
        return self.unwrap()

    def unwrap(self) -> T:
        return self.value

    def expect_err(self, msg: str) -> t.NoReturn:
        raise PanicError(f"{msg}: {self.unwrap()}")

    def unwrap_err(self) -> t.NoReturn:
        raise PanicError(self.unwrap())

    def and_(
        self, resb: Ok[T, F] | Err[T, F] | Result[T, F] | Ok[U, F] | Err[U, F] | Result[U, F]
    ) -> Ok[T, F] | Err[T, F] | Result[T, F] | Ok[U, F] | Err[U, F] | Result[U, F]:
        return resb

    def __and__(
        self, resb: Ok[T, F] | Err[T, F] | Result[T, F] | Ok[U, F] | Err[U, F] | Result[U, F]
    ) -> Ok[T, F] | Err[T, F] | Result[T, F] | Ok[U, F] | Err[U, F] | Result[U, F]:
        return self.and_(resb)

    @t.overload
    def and_then(self, f: t.Callable[[T], Result[U, F]]) -> Result[U, F]: ...
    @t.overload
    def and_then(self, f: t.Callable[[T], Ok | Err | Result]): ...

    def and_then(self, f: t.Callable[[T], Ok | Err | Result]):
        return f(self.unwrap())

    def or_(self, res: Ok[T, F] | Err[T, F] | Result[T, F]) -> Ok[T, E]:
        return self

    def __or__(self, res: Ok[T, F] | Err[T, F] | Result[T, F]) -> Ok[T, E]:
        return self.or_(res)

    def or_else(self, op: t.Callable[[E], Ok[U, F] | Err[U, F] | Result[U, F]]) -> Ok[T, E]:
        return self

    def unwrap_or(self, default: T) -> T:
        return self.unwrap()

    def unwrap_or_else(self, f: t.Callable[[E], T]) -> T:
        return self.unwrap()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Ok):
            return self.value == other.value
        return False

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"


class Err(Result[T, E]):
    def __init__(self, value: E) -> None:
        self.value = value

    def is_ok(self) -> bool:
        return False

    def is_ok_and(self, f: t.Callable[[T], bool]) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def is_err_and(self, f: t.Callable[[E], bool]) -> bool:
        return f(self.unwrap_err())

    def ok(self) -> Option[T]:
        from .option import Option

        return Option(None)

    def err(self) -> Option[E]:
        from .option import Option

        return Option(self.unwrap_err())

    def map(self, f: t.Callable[[T], U]) -> Err[T, E]:
        return self

    def map_or(self, default: U, f: t.Callable[[T], U]) -> U:
        return default

    def map_or_else(self, default: t.Callable[[E], U], f: t.Callable[[T], U]) -> U:
        return default(self.unwrap_err())

    def map_err(self, op: t.Callable[[E], F]) -> Err[T, F]:
        return Err[T, F](op(self.unwrap_err()))

    def inspect(self, f: t.Callable[[T], None]) -> Err[T, E]:
        return self

    def inspect_err(self, f: t.Callable[[E], None]) -> Err[T, E]:
        f(self.unwrap_err())
        return self

    def expect(self, msg: str) -> t.NoReturn:
        raise PanicError(f"{msg}: {self.unwrap_err()}")

    def unwrap(self) -> t.NoReturn:
        raise PanicError(self.unwrap_err())

    def expect_err(self, msg: str) -> E:
        return self.unwrap_err()

    def unwrap_err(self) -> E:
        return self.value

    def and_(self, resb: Ok[U, F] | Err[U, F] | Result[U, F]) -> Err[T, E]:
        return self

    def __and__(self, resb: Ok[U, F] | Err[U, F] | Result[U, F]) -> Err[T, E]:
        return self.and_(resb)

    def and_then(self, f: t.Callable[[T], Ok | Err | Result]) -> Err[T, E]:
        return self

    def or_(self, res: Ok[T, F] | Err[T, F] | Result[T, F]) -> Ok[T, F] | Err[T, F] | Result[T, F]:
        return res

    def __or__(self, res: Ok[T, F] | Err[T, F] | Result[T, F]) -> Ok[T, F] | Err[T, F] | Result[T, F]:
        return self.or_(res)

    @t.overload
    def or_else(self, op: t.Callable[[E], Ok[U, F]]) -> Ok[U, F]: ...
    @t.overload
    def or_else(self, op: t.Callable[[E], Err[U, F]]) -> Err[U, F]: ...
    @t.overload
    def or_else(self, op: t.Callable[[E], Result[U, F]]) -> Result[U, F]: ...

    def or_else(self, op: t.Callable[[E], Ok[U, F] | Err[U, F] | Result[U, F]]) -> Ok[U, F] | Err[U, F] | Result[U, F]:
        return op(self.unwrap_err())

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, f: t.Callable[[E], T]) -> T:
        return f(self.unwrap_err())

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Err):
            if isinstance(self.value, Exception) and isinstance(value.value, Exception):
                return is_same_exception(self.value, value.value)
            return self.value == value.value
        return False

    def __repr__(self) -> str:
        return f"Err({self.value!r})"

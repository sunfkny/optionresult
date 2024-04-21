from __future__ import annotations

import typing as t

from .exceptions import PanicError

if t.TYPE_CHECKING:
    from .result import Err, Ok # pragma: no cover

T = t.TypeVar("T")
U = t.TypeVar("U")
E = t.TypeVar("E")
R = t.TypeVar("R")
F = t.TypeVar("F")


class Option(t.Generic[T]):
    @staticmethod
    def of(
        fn: t.Callable[..., U],
        *args: t.Any,
        catch: t.Type[Exception] = Exception,
        **kwargs: t.Any,
    ) -> Option[U]:
        try:
            return Option(fn(*args, **kwargs))
        except catch:
            return Option(None)

    def __init__(self, value: T | None):
        self.value = value

    def is_some(self) -> bool:
        return self.value is not None

    def is_some_and(self, f: t.Callable[[T], bool]) -> bool:
        return self.value is not None and f(self.value)

    def is_none(self) -> bool:
        return self.value is None

    def expect(self, msg: str) -> T:
        if self.value is None:
            raise PanicError(msg)
        else:
            return self.value

    def unwrap(self) -> T:
        if self.value is None:
            raise RuntimeError("called `Option.unwrap()` on a `None` value")
        else:
            return self.value

    def unwrap_or(self, default: T) -> T:
        if self.value is None:
            return default
        else:
            return self.value

    def unwrap_or_else(self, f: t.Callable[[], T]) -> T:
        if self.value is None:
            return f()
        else:
            return self.value

    def map(self, f: t.Callable[[T], U]) -> Option[U]:
        if self.value is None:
            return Option(None)
        else:
            return Option(f(self.value))

    def inspect(self, f: t.Callable[[T], None]) -> Option[T]:
        if self.value is not None:
            f(self.value)
        return self

    def map_or(self, default: U, f: t.Callable[[T], U]) -> U:
        if self.value is None:
            return default
        else:
            return f(self.value)

    def map_or_else(self, default: t.Callable[[], U], f: t.Callable[[T], U]) -> U:
        if self.value is None:
            return default()
        else:
            return f(self.value)

    def ok_or(self, err: E) -> Ok[T, E] | Err[T, E]:
        from .result import Err, Ok

        if self.value is None:
            return Err(err)
        else:
            return Ok(self.value)

    def ok_or_else(self, err: t.Callable[[], E]) -> Ok[T, E] | Err[T, E]:
        from .result import Err, Ok

        if self.value is None:
            return Err(err())
        else:
            return Ok(self.value)

    def and_(self, optb: Option[U]) -> Option[U]:
        if self.value is None:
            return Option(None)
        else:
            return optb

    def __and__(self, optb: Option[U]) -> Option[U]:
        return self.and_(optb)

    def and_then(self, f: t.Callable[[T], Option[U]]) -> Option[U]:
        if self.value is None:
            return Option(None)
        else:
            return f(self.value)

    def filter(self, predicate: t.Callable[[T], bool]) -> Option[T]:
        if self.value is None:
            return Option(None)
        if predicate(self.value):
            return Option(self.value)
        else:
            return Option(None)

    def or_(self, optb: Option[T]) -> Option[T]:
        if self.value is None:
            return optb
        else:
            return self

    def __or__(self, optb: Option[T]) -> Option[T]:
        return self.or_(optb)

    def or_else(self, f: t.Callable[[], Option[T]]) -> Option[T]:
        if self.value is None:
            return f()
        else:
            return self

    def xor(self, optb: Option[T]) -> Option[T]:
        if self.value is None and optb.value is not None:
            return optb
        if self.value is not None and optb.value is None:
            return self
        return Option(None)

    def __xor__(self, optb: Option[T]) -> Option[T]:
        return self.xor(optb)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Option):
            return self.value == value.value
        return False

    def __repr__(self) -> str:
        if self.value is None:
            return "None"
        return f"Some({self.value!r})"

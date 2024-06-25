from __future__ import annotations

import typing_extensions as t
from optionresult import Err, Ok, Option, Result

UInt32 = t.NewType("UInt32", int)

t.assert_type(Result.of(lambda: 123), t.Union[Ok[int, Exception], Err[int, Exception]])
t.assert_type(Result.of(lambda: None), t.Union[Ok[None, Exception], Err[None, Exception]])

t.assert_type(Ok(-3), Ok[int, t.Any])
t.assert_type(Err("error"), Err[t.Any, str])


t.assert_type(
    Ok[int, int](2)
    .or_else(
        lambda x: Ok[int, int](x * x),
    )
    .or_else(
        lambda x: Ok[int, int](x * x),
    ),
    Ok[int, int],
)
t.assert_type(
    Ok[int, int](2)
    .or_else(
        lambda x: Err[int, int](x * x),
    )
    .or_else(
        lambda x: Ok[int, int](x * x),
    ),
    Ok[int, int],
)
t.assert_type(
    Err[int, int](3)
    .or_else(
        lambda x: Ok[int, int](x * x),
    )
    .or_else(
        lambda x: Err[int, int](x * x),
    ),
    Ok[int, int],
)
t.assert_type(
    Err[int, int](3)
    .or_else(
        lambda x: Err[int, int](x * x),
    )
    .or_else(
        lambda x: Err[int, int](x * x),
    ),
    Err[int, int],
)


t.assert_type(Option.of(lambda: None), Option[None])
t.assert_type(Option.of(lambda: 42), Option[int])


line = "1\n2\n3\n4\na\nb\nc\nd\n"
for num in line.splitlines():
    r = Result[int, Exception].of(lambda: int(num)).map(lambda i: i * 2)
    if isinstance(r, Ok):
        pass
    elif isinstance(r, Err):
        pass
    else:
        t.assert_type(r, t.Never)  # pragma: no cover


class A:
    def __init__(self, x: int | None):
        self.x = x


t.assert_type(Option(A(None)).map(lambda x: x.x), Option[int])
t.assert_type(Option(A(2)).map(lambda x: x.x), Option[int])

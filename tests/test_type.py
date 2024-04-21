import typing as t

from optionresult import Err, Ok, Option, Result

UInt32 = t.NewType("UInt32", int)

t.assert_type(Result.of(lambda: 123), Ok[int, Exception] | Err[int, Exception])
t.assert_type(Result.of(lambda: None), Ok[None, Exception] | Err[None, Exception])

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
    match r:
        case Ok(n):
            print(n)
        case Err(e):
            pass
        case _:  # pragma: no cover
            t.assert_never(r)

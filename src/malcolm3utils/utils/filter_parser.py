import logging
from typing import Any, Generator

from lark import Lark, Transformer, v_args

logger = logging.getLogger(__name__)

filter_grammar = """
    ?start: or_test_
    ?or_test_: and_test_ ("or" and_test_)*    -> or_test
    ?and_test_: not_test_ ("and" not_test_)*  -> and_test
    ?not_test_: "not" not_test_               -> not_test
              | "True"                        -> true
              | "False"                       -> false
              | sum                           -> num_test
              | comp
              | "(" or_test_ ")"

    ?comp: sum "==" sum     -> eq
         | sum "!=" sum     -> ne
         | sum ">" sum      -> gt
         | sum ">=" sum     -> ge
         | sum "<" sum      -> lt
         | sum "<=" sum     -> le
         | "(" comp ")"

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div
        | product "%" atom  -> mod
        | product "//" atom -> floordiv

    ?atom: NUMBER           -> number
         | STRING_LITERAL   -> strlit
         | "-" atom         -> neg
         | key              -> key
         | "(" sum ")"

    ?key: CNAME | ESCAPED_STRING
    STRING_LITERAL: "'" _STRING_ESC_INNER "'"

    %import common.ESCAPED_STRING
    %import common._STRING_ESC_INNER
    %import common.CNAME
    %import common.NUMBER
    %import common.WS_INLINE

    %ignore WS_INLINE
"""


def to_number_or_string(s: Any) -> float | int | str:
    if isinstance(s, float) or isinstance(s, int):
        return s
    elif isinstance(s, str):
        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                return s
    return str(s)


def applyall(d: dict[str, Any], *args) -> Generator[bool, None, None]:  # type: ignore[no-untyped-def]
    for a in args:
        yield a(d)


@v_args(inline=True)
class FilterParser(Transformer):
    # making methods static breaks the @v_args functionality

    def or_test(self, *args):  # type: ignore[no-untyped-def]
        logger.debug("Or test: %s", args)
        return lambda d: any(applyall(d, *args))

    def and_test(self, *args):  # type: ignore[no-untyped-def]
        logger.debug("And test: %s", args)
        return lambda d: all(applyall(d, *args))

    def not_test(self, a):  # type: ignore[no-untyped-def]
        logger.debug("Not test: %s", a)
        return lambda d: not a(d)

    def num_test(self, a):  # type: ignore[no-untyped-def]
        logger.debug("Num test: %s", a)
        return lambda d: a(d) != 0

    def eq(self, a, b):  # type: ignore[no-untyped-def]
        logger.debug("Eq test: %s and %s", a, b)
        return lambda d: a(d) == b(d)

    def ne(self, a, b):  # type: ignore[no-untyped-def]
        logger.debug("Ne test: %s and %s", a, b)
        return lambda d: a(d) != b(d)

    def gt(self, a, b):  # type: ignore[no-untyped-def]
        logger.debug("Gt test: %s and %s", a, b)
        return lambda d: a(d) > b(d)

    def ge(self, a, b):  # type: ignore[no-untyped-def]
        logger.debug("Ge test: %s and %s", a, b)
        return lambda d: a(d) >= b(d)

    def lt(self, a, b):  # type: ignore[no-untyped-def]
        logger.debug("Lt test: %s and %s", a, b)
        return lambda d: a(d) < b(d)

    def le(self, a, b):  # type: ignore[no-untyped-def]
        logger.debug("Le test: %s and %s", a, b)
        return lambda d: a(d) <= b(d)

    def add(self, a, b):  # type: ignore[no-untyped-def]
        logger.debug("add: %s and %s", a, b)
        return lambda d: a(d) + b(d)

    def sub(self, a, b):  # type: ignore[no-untyped-def]
        logger.debug("sub: %s and %s", a, b)
        return lambda d: a(d) - b(d)

    def mul(self, a, b):  # type: ignore[no-untyped-def]
        logger.debug("mul: %s and %s", a, b)
        return lambda d: a(d) * b(d)

    def div(self, a, b):  # type: ignore[no-untyped-def]
        logger.debug("div: %s and %s", a, b)
        return lambda d: a(d) / b(d)

    def mod(self, a, b):  # type: ignore[no-untyped-def]
        logger.debug("mod: %s and %s", a, b)
        return lambda d: a(d) % b(d)

    def floordiv(self, a, b):  # type: ignore[no-untyped-def]
        logger.debug("floordiv: %s and %s", a, b)
        return lambda d: a(d) // b(d)

    def number(self, value):  # type: ignore[no-untyped-def]
        logger.debug("Number: %s", value)
        return lambda d: to_number_or_string(value)

    def strlit(self, v):  # type: ignore[no-untyped-def]
        logger.debug("String: %s", v)
        vv = v.strip("'")
        return lambda d: vv

    def neg(self, a):  # type: ignore[no-untyped-def]
        logger.debug("Negation: %s", a)
        return lambda d: -a(d)

    def key(self, a):  # type: ignore[no-untyped-def]
        logger.debug("Key: %s", a)
        b = a.strip('"')
        return lambda d: to_number_or_string(d[b])

    def true(self):  # type: ignore[no-untyped-def]
        logger.debug("True")
        return lambda d: True

    def false(self):  # type: ignore[no-untyped-def]
        logger.debug("False")
        return lambda d: False


def create_filter(filter_spec: str):  # type: ignore[no-untyped-def]
    """
    Convert a expression string into a function that takes a dictionary as an argument
    and returns a boolean
    """
    filter_parser = Lark(filter_grammar, parser="lalr", transformer=FilterParser())
    filter_generator = filter_parser.parse
    return filter_generator(filter_spec)

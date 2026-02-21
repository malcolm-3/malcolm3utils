import logging
import os
from csv import DictReader

from click.testing import CliRunner

from malcolm3utils.scripts.csv_filter import cli
from malcolm3utils.utils.filter_parser import create_filter

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

EXPECTED_HELP = """Usage: csv-filter [OPTIONS] FILTER_EXPRESSION csv_file

  Filter the input csv files.

  The filter expression can be a combination of simple arithmatic and logical
  expressions that will evaluate to True or False, with a numerical answer being
  True if non-zero.  Fieldnames can be used as variables in this expression.

  For example 'age + 1 < 4' would check each row and see if row['age'] + 1 is
  less than 4, and keep or discard rows for which the expression is True.

  Available operators are:
  +, -, *, /, %, //, ==, !=, <, <=, >, >=, not, and, or
  String literals can be specified using single quotes.
  Field names with spaces should be surrounded by double quotes.

  If no csv_files are specified, read from stdin.

  If no --output specified, write to stdout.

  Input files do not all have to have the same columns. The output will have all
  columns. To achieve this all csv_files are opened at program initiation. This
  may cause problems with your system's open file limit if you are attempting to
  filter a large number of files at once.

Options:
  --keep / --discard           keep or discard entries for which the expression
                               is true (default=keep)
  --output PATH                output file name
  -d, --delimiter TEXT         column delimiter  [default: ,]
  -o, --output-delimiter TEXT  output column delimiter (default=input delimiter)
  --version                    Show the version and exit.
  -v, --verbosity LVL          Either CRITICAL, ERROR, WARNING, INFO or DEBUG.
  --help                       Show this message and exit.
"""

EXPRESSION_TESTS = [
    {
        "title": "testing string comparison",
        "filter_expression": "'test' == 'test'",
        "expected_result": True,
    },
    {
        "title": "testing string substitution",
        "filter_expression": "S == 'a'",
        "expected_result": True,
    },
    {
        "title": "testing string concatenation",
        "filter_expression": "S + S == 'aa'",
        "expected_result": True,
    },
    {
        "title": "testing arbitrary object to string literal comparison",
        "filter_expression": "L == '[]'",
        "expected_result": True,
    },
    {
        "title": "testing basic comparison",
        "filter_expression": "1 == 1",
        "expected_result": True,
    },
    {
        "title": "testing basic or",
        "filter_expression": "1 == 1 or 1 == 2",
        "expected_result": True,
    },
    {
        "title": "testing math precedence 1",
        "filter_expression": "1 + 2 * 3 == 7",
        "expected_result": True,
    },
    {
        "title": "testing basic math expressions 1",
        "filter_expression": "1 + 2 * 3 + ( 4 + 5 ) / 3  == 5 + 5",
        "expected_result": True,
    },
    {
        "title": "testing basic math expressions 2",
        "filter_expression": "1 + 2 * 3 + ( 4 + 5 ) / 3 == 5 / 5",
        "expected_result": False,
    },
    {
        "title": "testing modulo operator",
        "filter_expression": "12 % 10 == 2",
        "expected_result": True,
    },
    {
        "title": "testing floordiv operator",
        "filter_expression": "12 // 10 == 1",
        "expected_result": True,
    },
    {
        "title": "testing logical expression precedence 1",
        "filter_expression": "(True or True) and False",
        "expected_result": False,
    },
    {
        "title": "testing logical expression precedence 2",
        "filter_expression": "True or True and False",
        "expected_result": True,
    },
    {
        "title": "testing basic logical expressions 1",
        "filter_expression": "True and (True or False) and not False",
        "expected_result": True,
    },
    {
        "title": "testing value assignment 1",
        "filter_expression": "A == 1",
        "expected_result": True,
    },
    {
        "title": "testing value assignment 1",
        "filter_expression": "1 == A",
        "expected_result": True,
    },
    {
        "title": "testing keys with spaces",
        "filter_expression": 'A + B == "C and D"',
        "expected_result": True,
    },
    {
        "title": "testing combined arithmatic and logical expressions",
        "filter_expression": 'A + B == E or A + "C and D" == E and 2 == B',
        "expected_result": True,
    },
    {
        "title": "testing numerical result 1",
        "filter_expression": "1",
        "expected_result": True,
    },
    {
        "title": "testing numerical result 2",
        "filter_expression": "0",
        "expected_result": False,
    },
    {
        "title": "testing inequality",
        "filter_expression": "0 != 1",
        "expected_result": True,
    },
    {
        "title": "testing greater than",
        "filter_expression": "1 > 1",
        "expected_result": False,
    },
    {
        "title": "testing greater than or equal to",
        "filter_expression": "1 >= 1",
        "expected_result": True,
    },
    {
        "title": "testing less than",
        "filter_expression": "1 < 1",
        "expected_result": False,
    },
    {
        "title": "testing less than or equal to",
        "filter_expression": "1 <= 1",
        "expected_result": True,
    },
    {
        "title": "testing add",
        "filter_expression": "1 + 1 == 2",
        "expected_result": True,
    },
    {
        "title": "testing sub",
        "filter_expression": "1 - 1 == 0",
        "expected_result": True,
    },
    {
        "title": "testing mul",
        "filter_expression": "2 * 2 == 4",
        "expected_result": True,
    },
    {
        "title": "testing div",
        "filter_expression": "4 / 2 == 2",
        "expected_result": True,
    },
    {
        "title": "testing floordiv",
        "filter_expression": "5 // 2 == 2",
        "expected_result": True,
    },
    {
        "title": "testing mod",
        "filter_expression": "7 % 5 == 2",
        "expected_result": True,
    },
    {
        "title": "testing neg",
        "filter_expression": "-A + 1 == 0",
        "expected_result": True,
    },
    {
        "title": "testing floats",
        "filter_expression": "1.5 + 1.5 == 3",
        "expected_result": True,
    },
]


def test_filter_parser():
    data = {"A": 1, "B": 2, "C and D": 3, "E": 4, "S": "a", "L": []}

    for expression_test in EXPRESSION_TESTS:
        filter_fucntion = create_filter(expression_test["filter_expression"])
        assert (
            filter_fucntion is not None
        ), f"{expression_test['title']}: filter_fucntion is None"
        assert (
            filter_fucntion(data) == expression_test["expected_result"]
        ), f"{expression_test['title']}: failed"


def test_filter_cli(tmp_csv_files):
    tmpdir = tmp_csv_files[0].parent
    filenames = [x.name for x in tmp_csv_files]
    os.chdir(tmpdir)

    runner = CliRunner()

    # noinspection PyTypeChecker
    result = runner.invoke(
        cli,
        ["--help"],
    )
    assert result.exit_code == 0
    assert result.stdout == EXPECTED_HELP

    # noinspection PyTypeChecker
    output_csv = tmpdir.joinpath("output.csv")
    result = runner.invoke(
        cli,
        ["--output", output_csv.name, "A % 100 == 11", *filenames],
    )
    assert result.exit_code == 0
    with output_csv.open() as fh:
        reader = DictReader(fh)
        data = list(reader)
    assert len(data) == 3
    assert data[0]["A"] == "111"
    assert data[1]["A"] == "211"
    assert data[2]["A"] == "311"

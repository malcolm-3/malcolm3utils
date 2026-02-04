import logging
import sys
from csv import DictReader, DictWriter
from typing import Tuple

import click
import click_logging

from malcolm3utils import __version__, __version_message__
from malcolm3utils.utils.filter_parser import create_filter

logger = logging.getLogger()

@click.command(
    "csv-filter",
    help="""
    Filter the input csv files.

    The filter expression can be a combination of simple
    arithmatic and logical expressions that will evaluate to
    True or False, with a numerical answer being True if
    non-zero.  Fieldnames can be used as variables in
    this expression.

    For example 'age + 1 < 4' would check each row and
    see if row['age'] + 1 is less than 4, and keep or discard
    rows for which the expression is True.

    \b
    Available operators are:
    +, -, *, /, %, //, ==, !=, <, <=, >, >=, not, and, or
    String literals can be specified using single quotes.
    Field names with spaces should be surrounded by double quotes.

    If no csv_files are specified, read from stdin.

    If no --output specified, write to stdout.

    Input files do not all have to have the same columns.
    The output will have all columns.
    To achieve this all csv_files are opened at program initiation.
    This may cause problems with your system's open file limit if
    you are attempting to filter a large number of files at once.
    """
)
@click.argument(
    'filter_expression',
    type=str,
    required=True,
)
@click.argument(
    'csv_files',
    type=click.Path(exists=True),
    nargs=-1,
    metavar='csv_file',
    required=False,
)
@click.option(
    '--keep/--discard',
    is_flag=True,
    help="keep or discard entries for which the expression is true (default=keep)",
    default=True,
)
@click.option(
    '--output',
    type=click.Path(exists=False),
    help="output file name",
)
@click.option(
    "-d",
    "--delimiter",
    type=str,
    help="column delimiter (default=COMMA)",
    default=",",
)
@click.option(
    "--output-delimiter",
    type=str,
    help="output column delimiter (default=input delimiter)",
)
@click.version_option(__version__, message=__version_message__)
@click_logging.simple_verbosity_option(logger)
def cli(
        filter_expression: str,
        csv_files: Tuple[click.Path, ...] = tuple(),
        keep: bool = True,
        output: click.Path | None = None,
        delimiter: str = ',',
        output_delimiter: str | None = None,
) -> None:

    if output_delimiter is None:
        output_delimiter = delimiter
    filter_function = create_filter(filter_expression)
    input_fhs = []
    readers = []
    fieldnames = []
    output_fh = None
    try:
        if output is None:
            output_fh = sys.stdout
        else:
            output_fh = open(str(output), 'w')

        if csv_files:
            for csv_file in csv_files:
                input_fh = open(str(csv_file), "r")
                input_fhs.append(input_fh)
                reader = DictReader(input_fh, delimiter=delimiter)
                fieldnames.extend([x for x in reader.fieldnames if x not in fieldnames])
                readers.append(reader)
        else:
            input_fh = sys.stdin
            input_fhs.append(input_fh)
            reader = DictReader(input_fh)
            fieldnames.extend(reader.fieldnames)
            readers.append(reader)

        writer = DictWriter(output_fh, fieldnames=fieldnames, delimiter=output_delimiter)
        writer.writeheader()

        for reader in readers:
            for row in reader:
                if retval := filter_function(row) == keep:
                    writer.writerow(row)

    finally:
        for input_fh in input_fhs:
            input_fh.close()
        if output_fh is not None:
            output_fh.close()
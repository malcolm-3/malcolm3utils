import csv
import logging
from pathlib import Path

import click
import click_logging

from malcolm3utils.utils.csvio import DEFAULT_DELIMITER, csv_options

from .. import __version__, __version_message__

logger = logging.getLogger(__name__)
click_logging.basic_config(logger)


@click.command(
    "csv-diff",
    help="""
    Print the differences between two CSV files.
    If there are columns that one file has that the other doesn't they are listed first.
    Then for every row where at least one key has different values a row is printed of the form:

    \b
    Row #:: key="value1"|"value2",...

    where the row number 1 is the first line following the headers.
    """,
)
@csv_options()
@click.version_option(__version__, message=__version_message__)
@click_logging.simple_verbosity_option(logger)
@click.argument(
    "first_csv_file",
    type=click.Path(exists=True),
)
@click.argument(
    "second_csv_file",
    type=click.Path(exists=True),
)
def cli(
    first_csv_file: click.Path,
    second_csv_file: click.Path,
    delimiter: str = DEFAULT_DELIMITER,
    output_delimiter: str | None = None,
) -> None:
    if output_delimiter is None:
        output_delimiter = delimiter
    firct_csv_path = Path(str(first_csv_file))
    second_csv_path = Path(str(second_csv_file))
    with firct_csv_path.open(mode="r") as first_csv_fh:
        with second_csv_path.open(mode="r") as second_csv_fh:

            reader1 = csv.DictReader(first_csv_fh, delimiter=delimiter)
            reader2 = csv.DictReader(second_csv_fh, delimiter=delimiter)

            fieldnames1 = set(reader1.fieldnames or [])
            fieldnames2 = set(reader2.fieldnames or [])
            only_in_1 = fieldnames1 - fieldnames2
            if only_in_1:
                print(f"Columns only in {first_csv_file}:")
                for key in only_in_1:
                    print(f"\t{key}")
            only_in_2 = fieldnames2 - fieldnames1
            if only_in_2:
                print(f"Columns only in {second_csv_file}:")
                for key in only_in_2:
                    print(f"\t{key}")
            common_fields = fieldnames1 & fieldnames2
            fieldnames = [
                x for x in list(reader1.fieldnames or []) if x in common_fields
            ]

            for i, (data1, data2) in enumerate(zip(reader1, reader2)):
                diffs = [
                    f'"{k}":"{data1[k]}"|"{data2[k]}"'
                    for k in fieldnames
                    if data1[k] != data2[k]
                ]
                if diffs:
                    print(f"Row {i + 1}:: {output_delimiter.join(diffs)}")

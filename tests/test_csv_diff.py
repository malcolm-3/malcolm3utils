import logging
import os

from click.testing import CliRunner

from malcolm3utils.scripts.csv_diff import cli

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

EXPECTED_HELP = """Usage: csv-diff [OPTIONS] FIRST_CSV_FILE SECOND_CSV_FILE

  Print the differences between two CSV files. If there are columns that one
  file has that the other doesn't they are listed first. Then for every row
  where at least one key has different values a row is printed of the form:

  Row #:: key="value1"|"value2",...

  where the row number 1 is the first line following the headers.

Options:
  -d, --delimiter TEXT         column delimiter  [default: ,]
  -o, --output-delimiter TEXT  output column delimiter (default=input delimiter)
  --version                    Show the version and exit.
  -v, --verbosity LVL          Either CRITICAL, ERROR, WARNING, INFO or DEBUG.
  --help                       Show this message and exit.
"""


EXPECTED_OUTPUT = """Columns only in file1.csv:
\tE
Columns only in file2.csv:
\tF
Row 1:: "S":"c"|"e"
Row 2:: "A":"221"|"321.1","S":"d"|"f","X":"False"|"True"
"""


def test_csv_diff_cli(tmp_csv_diff_files):
    tmpdir = tmp_csv_diff_files[0].parent
    filenames = [x.name for x in tmp_csv_diff_files]
    os.chdir(tmpdir)

    runner = CliRunner()

    # noinspection PyTypeChecker
    result = runner.invoke(
        cli,
        ["--help"],
    )
    assert result.exit_code == 0
    assert result.stdout == EXPECTED_HELP

    result = runner.invoke(cli, filenames)
    assert result.exit_code == 0
    assert result.stdout == EXPECTED_OUTPUT

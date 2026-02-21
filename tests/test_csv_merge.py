import logging
from datetime import datetime
from pathlib import Path
from typing import List, TypedDict

import pytest
from click.testing import CliRunner

from malcolm3utils.scripts.csv_merge import cli

from .utils import os_independent_text_equals

logger = logging.getLogger(__name__)

now = int(datetime.now().timestamp())


class FileEntry(TypedDict):
    name: str
    mtime: int


EXPECTED_HELP = """Usage: csv-merge [OPTIONS] [FILES_TO_READ]...

  Merge the specified delimited files with column headings, joining entries with
  the same key field value.

  The files do not need to be sorted on the key field as with join(1). This does
  require that all of the data be read into memory. If that is a problem, using
  the system join(1) command is recommended.

  Rows will be printed in the order that the unique key values are encountered
  when reading through the input files.

  To read from stdin, use '-' as the filename.

  The output key column will be the first column of the output file and the
  header will be the header from the first file.

  If -k is used to specify alternative keys columns for subsequent files, but
  those files have a column with the same name as the output key column, that
  will be ignored.

Options:
  -v, --verbosity LVL           Either CRITICAL, ERROR, WARNING, INFO or DEBUG.
  -d, --delimiter TEXT          column delimiter  [default: ,]
  -o, --output-delimiter TEXT   output column delimiter (default=input
                                delimiter)
  --all-delimiter TEXT          when keep=="all" this will be the delimiter
                                between entries where there are multiple
                                (default=";")
  -k, --key-column TEXT         comma separated list of key column identifiers.
                                each new file will use the next identifier. the
                                last identifier will be used for all remaining
                                files, so just use "-k identifier" if the
                                identifier is the same for all files. The
                                identifier can either be the header string or
                                the one-based column index. (default=1 (i.e. the
                                first column of each file))
  --keep [first|last|uniq|all]  specifies how to handle multiple values for the
                                same field with the same key
  -I, --ignore TEXT             comma separated list of column identifiers to
                                ignore
  --version                     Show the version and exit.
  --help                        Show this message and exit.
"""

FILE1 = """Key,F1,F2
a,1af1,1af2
b,1bf1,1bf2
c,1cf1,
d,,1df2
"""

FILE2 = """AltKey,Key,F3,F2
d,a,2af3,2af2
c,b,2bf3,2bf2
b,c,2cf3,
a,d,,2df2
e,e,2ef3,2ef2
"""

FILE3 = """X,Y,Z
a,3ay,3az
b,3by,3bz
"""

FILE4 = """AltKey,Key,F3,F2
d,a,2af3,2af2
c,b,2bf3,2bf2
,,x,x
b,c,2cf3,
a,d,,2df2
e,e,2ef3,2ef2
"""

FILE5 = """X,Y,Z
a,3ay,3az
b,3by,5bz
"""

EXPECTED_FIRST = """Key,F1,F2,AltKey,F3
a,1af1,1af2,d,2af3
b,1bf1,1bf2,c,2bf3
c,1cf1,,b,2cf3
d,,1df2,a,
e,,2ef2,e,2ef3
"""

EXPECTED_ALL = """Key,F1,F2,AltKey,F3
a,1af1,1af2;2af2,d,2af3
b,1bf1,1bf2;2bf2,c,2bf3
c,1cf1,,b,2cf3
d,,1df2;2df2,a,
e,,2ef2,e,2ef3
"""

EXPECTED_LAST = """Key,F1,F2,AltKey,F3
a,1af1,2af2,d,2af3
b,1bf1,2bf2,c,2bf3
c,1cf1,,b,2cf3
d,,2df2,a,
e,,2ef2,e,2ef3
"""

EXPECTED_ALL_TAB = EXPECTED_ALL.replace(",", "\t")

EXPECTED_ALL_ALTKEY = """Key,F1,F2,F3
a,1af1,1af2;2df2,
b,1bf1,1bf2,2cf3
c,1cf1,2bf2,2bf3
d,,1df2;2af2,2af3
e,,2ef2,2ef3
"""

EXPECTED_ALL_IGNORE = """Key,F2,F3
a,1af2;2af2,2af3
b,1bf2;2bf2,2bf3
c,,2cf3
d,1df2;2df2,
e,2ef2,2ef3
"""

EXPECTED_UNIQ = """X,Y,Z
a,3ay,3az
b,3by,3bz;5bz
"""

EXPECTED_2FILE3_ALL = """X,Y,Z
a,3ay;3ay,3az;3az
b,3by;3by,3bz;3bz
"""

EXPECTED_2FILE3_UNIQ = FILE3

tmp_tree_files: list[FileEntry] = [
    {"name": "file.1990.01.01", "mtime": int(datetime(1990, 1, 1).timestamp())},
    {"name": "file.2000.03.03", "mtime": int(datetime(2000, 3, 3).timestamp())},
    {"name": "file.2010.05.05", "mtime": int(datetime(2010, 5, 5).timestamp())},
    {"name": "ignore.~1~", "mtime": now},
    {"name": "ignore.JUNK", "mtime": now},
    {"name": "ignore.GARBAGE", "mtime": now},
]


@pytest.fixture
def tmp_files(tmp_path: Path) -> List[Path]:
    f1 = tmp_path.joinpath("file1")
    with open(f1, "w") as fh:
        fh.write(FILE1)
    f2 = tmp_path.joinpath("file2")
    with open(f2, "w") as fh:
        fh.write(FILE2)
    f3 = tmp_path.joinpath("file3")
    with open(f3, "w") as fh:
        fh.write(FILE3)
    f4 = tmp_path.joinpath("file4")
    with open(f4, "w") as fh:
        fh.write(FILE4)
    f5 = tmp_path.joinpath("file5")
    with open(f5, "w") as fh:
        fh.write(FILE5)
    return [f1, f2, f3, f4, f5]


def test_merge(tmp_files: List[Path]) -> None:
    runner = CliRunner()
    file1 = str(tmp_files[0])
    file2 = str(tmp_files[1])
    file3 = str(tmp_files[2])
    file4 = str(tmp_files[3])
    file5 = str(tmp_files[4])

    logger.debug("check help output")
    # noinspection PyTypeChecker
    result = runner.invoke(
        cli,
        ["--help"],
    )
    assert result.exit_code == 0
    assert os_independent_text_equals(result.output, EXPECTED_HELP)

    logger.debug("check without key")
    # noinspection PyTypeChecker
    result = runner.invoke(
        cli,
        [file1, file2],
    )
    assert result.exit_code == 0
    assert os_independent_text_equals(result.output, EXPECTED_ALL_ALTKEY)

    logger.debug("check with key")
    # noinspection PyTypeChecker
    result = runner.invoke(
        cli,
        ["-k", "Key", file1, file2],
    )
    assert result.exit_code == 0
    assert os_independent_text_equals(result.output, EXPECTED_ALL)

    logger.debug("check without per file key")
    # noinspection PyTypeChecker
    result = runner.invoke(
        cli,
        ["-k", "Key,AltKey", file1, file2],
    )
    assert result.exit_code == 0
    assert os_independent_text_equals(result.output, EXPECTED_ALL_ALTKEY)

    logger.debug("check with key, keep==first")
    # noinspection PyTypeChecker
    result = runner.invoke(
        cli,
        ["-k", "Key", "--keep", "first", file1, file2],
    )
    assert result.exit_code == 0
    assert os_independent_text_equals(result.output, EXPECTED_FIRST)

    logger.debug("check with key, keep==last")
    # noinspection PyTypeChecker
    result = runner.invoke(
        cli,
        ["-k", "Key", "--keep", "last", file1, file2],
    )
    assert result.exit_code == 0
    assert os_independent_text_equals(result.output, EXPECTED_LAST)

    logger.debug("check with key, reading stdin")
    # noinspection PyTypeChecker
    result = runner.invoke(cli, ["-k", "Key", file1, "-"], input=FILE2)
    assert result.exit_code == 0
    assert os_independent_text_equals(result.output, EXPECTED_ALL)

    logger.debug("check with key, change output delimiter")
    # noinspection PyTypeChecker
    result = runner.invoke(
        cli,
        ["-k", "Key", "-o", "\t", file1, file2],
    )
    assert result.exit_code == 0
    assert os_independent_text_equals(result.output, EXPECTED_ALL_TAB)

    logger.debug("check with key, bad file")
    # noinspection PyTypeChecker
    result = runner.invoke(cli, ["-k", "Key", file1, file3, file2], input=FILE2)
    assert result.exit_code == 0
    output_lines = result.output.split("\n")
    stderr_line = output_lines.pop(0)
    stdout = "\n".join(output_lines)
    assert os_independent_text_equals(stdout, EXPECTED_ALL)
    assert stderr_line.startswith('warning: Key "Key" not found')

    logger.debug("check with key, bad row")
    # noinspection PyTypeChecker
    result = runner.invoke(cli, ["-k", "Key", file1, file4], input=FILE2)
    assert result.exit_code == 0
    output_lines = result.output.split("\n")
    stderr_line = output_lines.pop(0)
    stdout = "\n".join(output_lines)
    assert os_independent_text_equals(stdout, EXPECTED_ALL)
    assert stderr_line.startswith("warning: No key value found for line 4")

    logger.debug("check with key, empty file")
    result = runner.invoke(cli, ["-k", "Key", file1, "-", file2], input="")
    assert result.exit_code == 0
    output_lines = result.output.split("\n")
    stderr_line = output_lines.pop(0)
    stdout = "\n".join(output_lines)
    assert os_independent_text_equals(stdout, EXPECTED_ALL)
    assert stderr_line.startswith("warning: No fieldnames found in file")

    logger.debug("check with key, ignore")
    # noinspection PyTypeChecker
    result = runner.invoke(
        cli,
        ["-k", "Key", "-I", "F1,AltKey", file1, file2],
    )
    assert result.exit_code == 0
    assert os_independent_text_equals(result.output, EXPECTED_ALL_IGNORE)

    logger.debug("check keep all with duplicate file")
    # noinspection PyTypeChecker
    result = runner.invoke(
        cli,
        ["-k", "X", "--keep", "all", file3, file3],
    )
    assert result.exit_code == 0
    assert os_independent_text_equals(result.output, EXPECTED_2FILE3_ALL)

    logger.debug("check keep uniq with duplicate file")
    # noinspection PyTypeChecker
    result = runner.invoke(
        cli,
        ["-k", "X", "--keep", "uniq", file3, file3],
    )
    assert result.exit_code == 0
    assert os_independent_text_equals(result.output, EXPECTED_2FILE3_UNIQ)

    logger.debug("check keep uniq")
    # noinspection PyTypeChecker
    result = runner.invoke(
        cli,
        ["-k", "X", "--keep", "uniq", file3, file5],
    )
    assert result.exit_code == 0
    assert os_independent_text_equals(result.output, EXPECTED_UNIQ)

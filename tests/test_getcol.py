from pathlib import Path

from click.testing import CliRunner

from fixtures import TEST_INPUT
from malcolm3utils.scripts.getcol import getcol

from .utils import os_independent_text_equals


def test_getcol(tmp_file: Path) -> None:
    runner = CliRunner()
    tmp_file_name = str(tmp_file)

    # noinspection PyTypeChecker
    result = runner.invoke(
        getcol,
        ["2", tmp_file_name],
    )
    assert result.exit_code == 0
    assert os_independent_text_equals(result.output, "B\n2\n")

    # noinspection PyTypeChecker
    result = runner.invoke(
        getcol,
        ["2,4", tmp_file_name],
    )
    assert result.exit_code == 0
    assert os_independent_text_equals(result.output, "B\tD\n2\t4\n")

    # noinspection PyTypeChecker
    result = runner.invoke(
        getcol,
        ["2-4", tmp_file_name],
    )
    assert result.exit_code == 0
    assert os_independent_text_equals(result.output, "B\tC\tD\n2\t3\t4\n")

    # noinspection PyTypeChecker
    result = runner.invoke(
        getcol,
        ["2,D", tmp_file_name],
    )
    assert result.exit_code == 0
    assert os_independent_text_equals(result.output, "B\tD\n2\t4\n")

    # noinspection PyTypeChecker
    result = runner.invoke(
        getcol,
        ["-o", "|", "2,BAD-HEADER,4"],
        input=TEST_INPUT,
    )
    assert result.exit_code == 0
    assert os_independent_text_equals(result.output, "B|D\n2|4\n")

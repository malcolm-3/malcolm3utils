import logging
import os

from click.testing import CliRunner

from malcolm3utils.scripts.ccli2chrpo import cli

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

EXPECTED_HELP = """Usage: ccli2chpro [OPTIONS] input_file

  Convert a CCLI chord text to chordpro format.

  Get the 'Chords' view of your song in Song Select set to the desired key, and
  select and copy all of the text below the tool bar, i.e. from the title
  through to your CCLI license number. Paste this into a text file and run this
  command using that file as the input_file.

  The output is written to that file with the extension changed to chordpro.

  This script attempts to 'fix' everything, but inevitably there will be things
  it gets wrong, so plan on checking the output for correctness. No guarantees
  are given or implied.

Options:
  --version            Show the version and exit.
  -v, --verbosity LVL  Either CRITICAL, ERROR, WARNING, INFO or DEBUG.
  --help               Show this message and exit.
"""

EXPECTED_OUTPUT = """{title: Build My Life}
{artist: Brett Younker, Karl Martin, Kirby Kaple, Matt Redman, and Pat Barrett}
{meta: based on the recording by Pat Barrett}
{key: G}
{tempo: 70}
{time: 4/4}
{chordcolor: blue}
{meta: ccli song 7070345}
{meta: ccli license 57980}

{comment: Intro}
|  [G]          |  [C2]         |  [G/B]         |  [C2]         |

{comment: Verse 1}
[G]     Worthy of ev'ry [C2]song we could ever sing
[G/B]     Worthy of all the [C2]praise we could ever bring
[G]     Worthy of ev'ry [C2]breath we could ever breathe
We live for [G/B]You         [C2]

{comment: Verse 2}
[G]     Jesus the name a - C2bove ev'ry other name
[G/B]     Jesus the only [C2]one who could ever save
[G]     Worthy of ev'ry [C2]breath we could ever breathe
We live for [G/B]You,    we live for [C2]You

{comment: Chorus}
[C2]Holy there is no one [Am]like You
There is none be - [G/D]side You open up my [Em7]eyes in wonder
And [C2]show me who You are and [Am]fill me
With Your heart and [G/D]lead me in Your love to [Em7]those around me

{comment: Bridge}
[C]I will build my [D]life upon Your [Em7]love
It is a [G/B]firm foundation
[C]I will put my [D]trust in You a - [Em7]lone
And I will [G/B]not be shaken  ([C])   (Last time)
"""

EXPECTED_ERROR = [
    "First line does not contain 'SongSelect logo'",
    "Third line does not contain 'based on'",
    "Third line does not contain 'based on'",
    "Fourth line does not start with 'Key'",
    "Could not locate 'CCLI Song #' line",
    "Could not locate 'CCLI License #' line",
]


def test_ccli2chrpo_cli(tmp_ccli_files):
    tmpdir, input_file, *bad_input_files = tmp_ccli_files
    output_file = input_file.with_suffix(".chordpro")
    assert tmpdir.exists()
    assert input_file.exists()
    assert not output_file.exists()

    os.chdir(str(tmpdir))
    runner = CliRunner()

    # noinspection PyTypeChecker
    result = runner.invoke(
        cli,
        ["--help"],
    )
    assert result.exit_code == 0
    assert result.stdout == EXPECTED_HELP

    # noinspection PyTypeChecker
    result = runner.invoke(
        cli,
        [input_file.name],
    )
    assert result.exit_code == 0
    assert output_file.exists()
    with output_file.open("r") as fh:
        assert fh.read() == EXPECTED_OUTPUT

    for i, bad_input_file in enumerate(bad_input_files):
        result = runner.invoke(
            cli,
            [bad_input_file.name],
        )
        assert result.exit_code == 0
        assert (
            result.stdout
            == f"Exception '{EXPECTED_ERROR[i]}' encountered processing {bad_input_file.name}: skipping file.\n"
        )

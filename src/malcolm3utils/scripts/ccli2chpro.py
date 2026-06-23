import logging
import re
from pathlib import Path
from typing import Any, Iterable

import click
import click_logging
import enchant  # type: ignore

from malcolm3utils import __version__, __version_message__

logger = logging.getLogger(__name__)
click_logging.basic_config(logger)
d = enchant.Dict("en_US")


@click.command(
    "ccli2chpro",
    help="""
    Convert a CCLI chord text to chordpro format.

    Get the 'Chords' view of your song in Song Select
    set to the desired key, and select and copy all of the text
    below the tool bar, i.e. from the title through to your CCLI license number.
    Paste this into a text file and run this command using that file as the input_file.

    The output is written to that file with the extension changed to chordpro.

    This script attempts to 'fix' everything, but inevitably there will be
    things it gets wrong, so plan on checking the output for correctness.
    No guarantees are given or implied.
    """,
)
@click.version_option(__version__, message=__version_message__)
@click_logging.simple_verbosity_option(logger)
@click.argument(
    "input_files",
    type=click.Path(exists=True),
    nargs=-1,
    metavar="input_file",
    required=True,
)
def cli(
    *_: Any,
    input_files: Iterable[click.Path] = (),
) -> None:
    for input_file in input_files:
        try:
            process(Path(str(input_file)))
        except ValueError as e:
            msg = f"Exception '{e}' encountered processing {input_file}: skipping file."
            click.secho(msg, fg="red")


comment_regex = re.compile(r"Intro|Verse|Verse \d+|Chorus|Chorus \d+|Bridge")
chord_regex = re.compile(
    r"([A-G](?:b|#)?m?(?:2|4|7|sus2|sus4|maj7)?(?:/[A-G](?:b|#)?)?)(\w*)"
)


def chord_replace(matchobj: re.Match) -> str:
    chord = matchobj.group(1)
    word = matchobj.group(2)
    if word == "" or d.check(word):
        return f"[{chord}]{word}"
    return f"{chord}{word}"


def process(input_file: Path) -> None:  # noqa: C901
    logger.debug("Processing %s", input_file)
    with input_file.open(mode="r") as fh:
        input_lines = [line.strip() for line in fh.readlines()]

    logger.debug("...read %d lines", len(input_lines))
    output_lines = []

    logger.debug("...processing title line")
    line = input_lines[0]
    if "SongSelect logo" not in line:
        msg = "First line does not contain 'SongSelect logo'"
        raise ValueError(msg)
    line = line.replace("SongSelect logo", "")
    line = f"{{title: {line}}}"
    output_lines.append(line)

    logger.debug("...processing artists line")
    line = input_lines[1]
    artists = line.split(" | ")
    if len(artists) > 1:
        artists[-1] = f"and {artists[-1]}"
    if len(artists) > 2:
        sep = ", "
    else:
        sep = " "
    line = f"{{artist: {sep.join(artists)}}}"
    output_lines.append(line)

    logger.debug("...processing based-on line")
    line = input_lines[2]
    if "based on" not in line:
        msg = "Third line does not contain 'based on'"
        raise ValueError(msg)
    line = line.strip("()")
    line = f"{{meta: {line}}}"
    output_lines.append(line)

    logger.debug("...processing key line")
    line = input_lines[3]
    if not line.startswith("Key"):
        msg = "Fourth line does not start with 'Key'"
        raise ValueError(msg)
    for k, v in [y.split(" - ") for y in line.split(" | ")]:
        output_lines.append(f"{{{k.lower()}: {v}}}")

    logger.debug("...adding chordcolor line")
    output_lines.append("{chordcolor: blue}")

    logger.debug("...adding ccli-song line")
    ccli_song_line = len(output_lines)
    output_lines.append("{meta: ccli song ")

    logger.debug("...adding ccli-license line")
    ccli_license_line = len(output_lines)
    output_lines.append("{meta: ccli license ")

    found_ccli_song_line = False
    found_ccli_license_line = False
    logger.debug("...processing the rest of the file")
    for line in input_lines[4:]:
        if line.startswith("CCLI Song # "):
            logger.debug("...found the ccli-song line")
            found_ccli_song_line = True
            line = line.replace("CCLI Song # ", "")
            output_lines[ccli_song_line] += line
            output_lines[ccli_song_line] += "}"
        if not found_ccli_song_line:
            logger.debug("...processing lyrics line")
            if comment_regex.fullmatch(line):
                logger.debug("......comment line")
                output_lines.append(f"{{comment: {line}}}")
            else:
                logger.debug("......regular lyric line")
                output_lines.append(
                    chord_regex.sub(chord_replace, line).replace("|", "[|]")
                )
        elif line.startswith("CCLI License # "):
            logger.debug("...found the ccli-license line")
            found_ccli_license_line = True
            line = line.replace("CCLI License # ", "")
            output_lines[ccli_license_line] += line
            output_lines[ccli_license_line] += "}"

    logger.debug("...checkig that ccli-song line is present")
    if not found_ccli_song_line:
        msg = "Could not locate 'CCLI Song #' line"
        raise ValueError(msg)

    logger.debug("...checkig that ccli-license line is present")
    if not found_ccli_license_line:
        msg = "Could not locate 'CCLI License #' line"
        raise ValueError(msg)

    logger.debug("...writing the output file")
    output_file = input_file.with_suffix(".chordpro")
    with open(output_file, "w") as fh:
        fh.write("\n".join(output_lines))

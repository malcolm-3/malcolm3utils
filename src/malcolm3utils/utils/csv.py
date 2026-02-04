import logging  # noqa: A005
from pathlib import Path
from typing import Any, Callable, Hashable

import pandas as pd

logger = logging.getLogger(__name__)


def read_keyed_csv_data(
    csv_file: Path,
    keyfield: str,
    skiprows: list[int] | int | Callable[[Hashable], bool] | None = None,
    multiple: bool = False,
) -> dict[str, dict[str, Any]] | dict[str, list[dict[str, Any]]]:
    """
    Instead of using DictReader which imports all values as strings,
    we use pandas.read_csv which handles all of the data conversion

    Values are returned as a keyed dictionary rather than a list
    as we may need to be able to look up the entries by key.

    Because MDBs do not support boolean values, we convert all
    boolean values to integer 0/1 fields.

    Skiprows can be
        - a list of 0-based line indexes to skip
        - a integer giving the number of initial lines to skip
        - a callable that takes the line index and returns True to skip that line
        - None to skip no rows (default)

    If multiple is true, then the value of the nested dict will be a list
    with each row that matches the key being appended to that list.

    :param csv_file: CSV file to be read.
    :param keyfield: Field to use as the key in the returned dictionary.
    :param skiprows: rows to skip
    :return: keyed dictionary of each row of data.
    :param multiple: indicates there may be multiple rows for each key
    """
    if multiple:
        result: dict[str, list[dict[str, Any]]] = {}
        for entry in read_csv_data(csv_file, skiprows=skiprows):
            key = entry[keyfield]
            if key not in result:
                result[key] = []
            result[key].append(entry)
        return result
    else:
        return {x[keyfield]: x for x in read_csv_data(csv_file)}


def read_csv_data(
    csv_file: Path,
    skiprows: list[int] | int | Callable[[Hashable], bool] | None = None,
) -> list[dict[str, Any]]:
    """
    Use Pandas to read a CSV into a simple list of dictionaries.

    Rows can be filtered by specifying a skiprows option.

    Skiprows can be
        - a list of 0-based line indexes to skip
        - a integer giving the number of initial lines to skip
        - a callable that takes the line index and returns True to skip that line
        - None to skip no rows (default)


    :param csv_file: file to be read
    :param skiprows: rows to skip
    :return: list of dictionary entries
    """
    logger.debug('...............reading CSV data from "%s"', csv_file)
    pandas_csv_data = pd.read_csv(str(csv_file), skiprows=skiprows)
    for key in pandas_csv_data.select_dtypes("bool").keys():
        pandas_csv_data[key] = pandas_csv_data[key].astype(int)
    return list(pandas_csv_data.transpose().to_dict().values())

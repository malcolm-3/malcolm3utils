import io
import os
from csv import DictReader
from pathlib import Path

import pytest

TEST_INPUT = """A,B,C,D
1,2,3,4
"""


@pytest.fixture
def tmp_file(tmp_path: Path) -> Path:
    f_path = tmp_path.joinpath("test.csv")
    with open(os.path.join(f_path), "w") as fh:
        fh.write(TEST_INPUT)
    return f_path


TEST_INPUTS = {
    "file1.csv": """A,B,C and D,E,S,X
111,112,113,114,a,True
121,122,123,124,b,False
""",
    "file2.csv": """A,B,C and D,E,S,X
211,212,213,214,c,True
221,222,223,224,d,False
""",
    "file3.csv": """A,B,C and D,F,S,X
311,312,313,314,e,True
321.1,322,323,324,f,False
""",
}

DIFF_TEST_INPUTS = {
    "file1.csv": """A,B,C and D,E,S,X
211,212,213,214,c,True
221,222,223,224,d,False
231,232,233,234,e,True
""",
    "file2.csv": """A,B,C and D,F,S,X
211,212,213,214,e,True
321.1,222,223,224,f,True
231,232,233,234,e,True
""",
}


@pytest.fixture
def tmp_csv_files(tmp_path: Path) -> list[Path]:
    tmp_file_list: list[Path] = []
    for fname, content in TEST_INPUTS.items():
        fpath = tmp_path.joinpath(fname)
        with fpath.open("w") as fh:
            fh.write(content)
        tmp_file_list.append(fpath)
    return tmp_file_list


@pytest.fixture
def tmp_csv_diff_files(tmp_path: Path) -> list[Path]:
    tmp_file_list: list[Path] = []
    for fname, content in DIFF_TEST_INPUTS.items():
        fpath = tmp_path.joinpath(fname)
        with fpath.open("w") as fh:
            fh.write(content)
        tmp_file_list.append(fpath)
    return tmp_file_list


@pytest.fixture
def tmp_csv_dicts() -> list[list[dict[str, int]]]:
    tmp_dict_list: list[list[dict[str, int]]] = []
    for content in TEST_INPUTS.values():
        reader = DictReader(io.StringIO(content))
        data = []
        for row in reader:
            d = {}
            for k, v in row.items():
                d[k] = int(v)
            data.append(d)
        tmp_dict_list.append(data)
    return tmp_dict_list

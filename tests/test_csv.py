import os

from malcolm3utils.utils.csv import read_csv_data, read_keyed_csv_data

from .fixtures import tmp_csv_files


def test_csv(tmp_csv_files):
    tmpdir = tmp_csv_files[0].parent
    os.chdir(str(tmpdir))

    data1 = read_csv_data(tmp_csv_files[0])
    assert data1 is not None
    assert len(data1) == 2
    assert data1[0]["A"] == 111

    data2 = read_keyed_csv_data(tmp_csv_files[0], "A")
    assert data2 is not None
    assert len(data2) == 2
    assert data2[111]["A"] == 111

    data2 = read_keyed_csv_data(tmp_csv_files[0], "A", multiple=True)
    assert data2 is not None
    assert len(data2) == 2
    assert data2[111][0]["A"] == 111

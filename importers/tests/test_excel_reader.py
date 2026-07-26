"""
Tests for Excel reader.
"""

from pathlib import Path

from importers.common.excel_reader import ExcelReader


def test_excel_reader_file_exists():

    reader = ExcelReader()

    assert reader is not None


def test_excel_reader_reads_workbook():

    source = Path(
        "importers/sources/test.xlsx"
    )

    if not source.exists():
        return

    reader = ExcelReader()

    rows = reader.read(
        str(source)
    )

    assert isinstance(
        rows,
        list
    )

"""
CSV Reader

Responsible only for reading CSV files.

Input:
    .csv file

Output:
    Raw rows

No framework-specific logic exists here.

Example:

    reader = CsvReader()

    rows = reader.read(
        "importers/sources/CAF.csv"
    )

    for row in rows:
        print(row)
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import csv


class CsvReader:
    """
    Generic CSV file reader.

    Designed to provide the same interface
    as ExcelReader.
    """

    def __init__(
        self,
        delimiter: str = ",",
        encoding: str = "utf-8",
        has_headers: bool = True
    ):
        """
        Configure CSV reading.

        Args:

            delimiter:
                CSV separator character.

            encoding:
                File encoding.

            has_headers:
                Whether first row contains column names.
        """

        self.delimiter = delimiter
        self.encoding = encoding
        self.has_headers = has_headers


    def read(
        self,
        filename: str
    ) -> List[Any]:
        """
        Read CSV rows.

        Args:

            filename:
                Path to CSV file.

        Returns:

            List of rows.

        With headers:

        [
            {
                "id": "A1.a",
                "domain": "Governance"
            }
        ]

        Without headers:

        [
            [
                "A1.a",
                "Governance"
            ]
        ]
        """

        path = Path(filename)

        if not path.exists():

            raise FileNotFoundError(
                f"CSV file not found: {filename}"
            )


        rows = []


        with open(
            path,
            "r",
            encoding=self.encoding,
            newline=""
        ) as file:


            if self.has_headers:

                reader = csv.DictReader(
                    file,
                    delimiter=self.delimiter
                )

            else:

                reader = csv.reader(
                    file,
                    delimiter=self.delimiter
                )


            for row in reader:

                rows.append(row)


        return rows

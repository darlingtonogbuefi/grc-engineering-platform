"""
Evidence Parser

Normalises collected evidence into
the platform evidence contract.

Pipeline:

Collector
    |
    v
Raw Evidence
    |
    v
EvidenceParser
    |
    v
Normalised Evidence
    |
    v
Validator
"""

from __future__ import annotations


from datetime import datetime, timezone


from pathlib import Path


from typing import Any


from uuid import uuid4



from .json_parser import JSONParser


from .yaml_parser import YAMLParser



class EvidenceParser:
    """
    Evidence normalisation engine.
    """



    def __init__(self) -> None:

        self.json_parser = JSONParser()

        self.yaml_parser = YAMLParser()



    def parse(
        self,
        path: Path
    ) -> dict[str, Any]:
        """
        Parse evidence file based on extension.
        """


        suffix = (
            path.suffix.lower()
        )



        if suffix == ".json":

            raw = self.json_parser.load(
                path
            )


        elif suffix in (
            ".yaml",
            ".yml"
        ):

            raw = self.yaml_parser.load(
                path
            )


        else:

            raise ValueError(
                f"Unsupported evidence format: {suffix}"
            )



        return self.normalise(
            raw,
            source=str(path)
        )



    def normalise(
        self,
        evidence: dict[str, Any],
        source: str
    ) -> dict[str, Any]:
        """
        Convert raw evidence into
        platform evidence format.
        """


        return {

            "evidence_id":
                str(uuid4()),


            "collected_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),


            "source":
                source,


            "status":
                "collected",


            "data":
                evidence

        }



    def parse_directory(
        self,
        directory: Path
    ) -> list[dict[str, Any]]:
        """
        Parse all evidence files.
        """


        results: list[dict[str, Any]] = []



        for file in directory.rglob("*"):


            if file.suffix.lower() in (
                ".json",
                ".yaml",
                ".yml"
            ):

                results.append(
                    self.parse(file)
                )



        return results

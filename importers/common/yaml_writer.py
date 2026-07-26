"""
YAML Writer

Responsible for writing canonical importer models
to framework YAML files.

Output example:

frameworks/
└── CAF/
    ├── metadata.yml
    ├── controls.yml
    ├── mappings.yml
    ├── evidence.yml
    └── scoring.yml
"""

from pathlib import Path
from typing import List

import yaml

from .models import (
    Framework,
    Control,
    Evidence,
    Mapping
)


class YamlWriter:
    """
    Writes framework objects into YAML files.
    """


    def __init__(self, output_directory: str):
        """
        Args:

            output_directory:
                Destination framework directory.

        Example:

            frameworks/CAF
        """

        self.output_directory = Path(output_directory)

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True
        )


    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def write_metadata(
        self,
        framework: Framework
    ) -> Path:
        """
        Write metadata.yml
        """

        data = {

            "id": framework.id,

            "name": framework.name,

            "version": framework.version,

            "description": framework.description,

            "owner": framework.owner,

            "source": framework.source,

            "control_count": framework.control_count,

        }


        data.update(
            framework.metadata
        )


        return self._write_yaml(
            "metadata.yml",
            data
        )


    # ------------------------------------------------------------------
    # Controls
    # ------------------------------------------------------------------

    def write_controls(
        self,
        framework: Framework
    ) -> Path:
        """
        Write controls.yml
        """

        controls = []


        for control in framework.controls:

            controls.append(
                {

                    "id": control.id,

                    "domain": control.domain,

                    "title": control.title,

                    "description": control.description,

                    "metadata": control.metadata

                }
            )


        return self._write_yaml(
            "controls.yml",
            {
                "controls": controls
            }
        )


    # ------------------------------------------------------------------
    # Mappings
    # ------------------------------------------------------------------

    def write_mappings(
        self,
        framework: Framework
    ) -> Path:
        """
        Write mappings.yml
        """

        mappings = []


        for control in framework.controls:

            mappings.append(
                {

                    "control_id": control.id,

                    "mappings": self._mapping_to_dict(
                        control.mappings
                    )

                }
            )


        return self._write_yaml(
            "mappings.yml",
            {
                "mappings": mappings
            }
        )


    # ------------------------------------------------------------------
    # Evidence
    # ------------------------------------------------------------------

    def write_evidence(
        self,
        framework: Framework
    ) -> Path:
        """
        Write evidence.yml
        """

        evidence_items = []


        for control in framework.controls:

            for evidence in control.evidence:

                evidence_items.append(
                    {

                        "control_id": control.id,

                        "id": evidence.id,

                        "name": evidence.name,

                        "description": evidence.description,

                        "type": evidence.evidence_type,

                        "capability": evidence.capability,

                        "references": evidence.references

                    }
                )


        return self._write_yaml(
            "evidence.yml",
            {
                "evidence": evidence_items
            }
        )


    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def write_scoring(
        self,
        framework: Framework
    ) -> Path:
        """
        Write scoring.yml

        Initial version provides a framework
        scoring placeholder.
        """

        data = {

            "framework": framework.id,

            "method": "percentage",

            "controls":

                {

                    "total": framework.control_count,

                    "weights": {}

                }

        }


        return self._write_yaml(
            "scoring.yml",
            data
        )


    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _write_yaml(
        self,
        filename: str,
        data: dict
    ) -> Path:
        """
        Write YAML file.
        """

        path = (
            self.output_directory
            /
            filename
        )


        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            yaml.safe_dump(
                data,
                file,
                sort_keys=False,
                allow_unicode=True
            )


        return path



    def _mapping_to_dict(
        self,
        mapping: Mapping
    ) -> dict:
        """
        Convert Mapping object into YAML structure.
        """

        return {

            "capability":
                mapping.capability,

            "nist":
                mapping.nist,

            "iso27001":
                mapping.iso27001,

            "cis":
                mapping.cis,

            "owasp":
                mapping.owasp,

            "cloud_security_principles":
                mapping.cloud_security_principles,

            **mapping.custom

        }

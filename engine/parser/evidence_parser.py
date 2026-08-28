# engine\parser\evidence_parser.py

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

    Converts raw JSON/YAML evidence into the
    platform evidence contract defined by:

        schemas/evidence.schema.json

    Existing collector-specific evidence is preserved
    inside ``data``.
    """

    def __init__(self) -> None:

        self.json_parser = JSONParser()

        self.yaml_parser = YAMLParser()

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def parse(
        self,
        path: Path,
    ) -> dict[str, Any]:
        """
        Parse evidence file based on extension.
        """

        if not isinstance(
            path,
            Path,
        ):
            path = Path(path)

        suffix = path.suffix.lower()

        if suffix == ".json":

            raw = self.json_parser.load(
                path,
            )

        elif suffix in (
            ".yaml",
            ".yml",
        ):

            raw = self.yaml_parser.load(
                path,
            )

        else:

            raise ValueError(f"Unsupported evidence format: {suffix}")

        return self.normalise(
            raw,
            source=str(path),
        )

    # ------------------------------------------------------------------
    # Normalisation
    # ------------------------------------------------------------------

    def normalise(
        self,
        evidence: dict[str, Any],
        source: str,
    ) -> dict[str, Any]:
        """
        Convert raw evidence into the
        platform evidence format.

        The resulting structure follows:

            schemas/evidence.schema.json

        Existing collector-specific evidence is
        preserved inside ``data``.

        Tags are normalised into:

            metadata.tags

        Existing values supplied by collectors are
        preserved wherever possible.
        """

        if not isinstance(
            evidence,
            dict,
        ):
            raise TypeError("Evidence must be a dictionary.")

        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------

        #
        # Preserve an existing metadata object when
        # supplied by the collector.
        #
        metadata = evidence.get(
            "metadata",
            {},
        )

        if not isinstance(
            metadata,
            dict,
        ):
            metadata = {}

        metadata = dict(metadata)

        # ------------------------------------------------------------------
        # Tags
        # ------------------------------------------------------------------

        #
        # Tags belong to metadata according to the
        # platform evidence schema.
        #
        # For compatibility with existing/raw evidence,
        # also accept top-level tags.
        #
        tags = metadata.get(
            "tags",
        )

        if tags is None:

            tags = evidence.get(
                "tags",
                [],
            )

        if not isinstance(
            tags,
            (list, tuple, set),
        ):
            tags = []

        #
        # Normalise tags consistently.
        #
        tags = [
            str(tag).strip().lower()
            for tag in tags
            if tag is not None and str(tag).strip()
        ]

        #
        # Ensure the required metadata field exists.
        #
        metadata["schemaVersion"] = str(
            metadata.get(
                "schemaVersion",
                "1.0",
            )
        )

        metadata["tags"] = tags

        # ------------------------------------------------------------------
        # Evidence ID
        # ------------------------------------------------------------------

        evidence_id = evidence.get(
            "id",
        )

        if evidence_id is None:

            evidence_id = str(uuid4())

        else:

            evidence_id = str(evidence_id).strip()

            if not evidence_id:

                evidence_id = str(uuid4())

        # ------------------------------------------------------------------
        # Tenant ID
        # ------------------------------------------------------------------

        tenant_id = evidence.get(
            "tenantId",
        )

        if tenant_id is None:

            tenant_id = ""

        else:

            tenant_id = str(tenant_id).strip()

        #
        # tenantId is required by the schema.
        #
        # An empty tenant ID is technically a string and would
        # therefore pass the current JSON schema, but it is not
        # useful as a platform identifier.
        #
        # Do not silently invent a tenant.
        #
        if not tenant_id:

            raise ValueError("Evidence is missing required tenantId.")

        # ------------------------------------------------------------------
        # Collector
        # ------------------------------------------------------------------

        collector = evidence.get(
            "collector",
            "unknown",
        )

        if collector is None:

            collector = "unknown"

        collector = str(collector).strip()

        if not collector:

            collector = "unknown"

        # ------------------------------------------------------------------
        # Evidence Type
        # ------------------------------------------------------------------

        evidence_type = evidence.get(
            "evidenceType",
            "unknown",
        )

        if evidence_type is None:

            evidence_type = "unknown"

        evidence_type = str(evidence_type).strip()

        if not evidence_type:

            evidence_type = "unknown"

        # ------------------------------------------------------------------
        # Collection Timestamp
        # ------------------------------------------------------------------

        #
        # Preserve a collector-provided collectedAt value.
        #
        # Only generate the current UTC timestamp when one
        # was not supplied.
        #
        collected_at = evidence.get(
            "collectedAt",
        )

        if collected_at is None:

            collected_at = datetime.now(timezone.utc).isoformat()

        else:

            collected_at = str(collected_at).strip()

            if not collected_at:

                collected_at = datetime.now(timezone.utc).isoformat()

        # ------------------------------------------------------------------
        # Optional Fields
        # ------------------------------------------------------------------

        collection_run_id = evidence.get(
            "collectionRunId",
        )

        if collection_run_id is not None:

            collection_run_id = str(collection_run_id)

        expires_at = evidence.get(
            "expiresAt",
        )

        if expires_at is not None:

            expires_at = str(expires_at)

        raw_reference = evidence.get(
            "rawReference",
            source,
        )

        if raw_reference is not None:

            raw_reference = str(raw_reference)

        # ------------------------------------------------------------------
        # Classification
        # ------------------------------------------------------------------

        classification = evidence.get(
            "classification",
            "internal",
        )

        if classification is None:

            classification = "internal"

        classification = str(classification).strip().lower()

        #
        # The evidence schema permits only these values.
        #
        allowed_classifications = {
            "public",
            "internal",
            "confidential",
            "restricted",
        }

        if classification not in allowed_classifications:

            raise ValueError(
                "Invalid evidence classification: "
                f"{classification!r}. "
                "Expected one of: "
                "public, internal, confidential, restricted."
            )

        # ------------------------------------------------------------------
        # Integrity
        # ------------------------------------------------------------------

        integrity = evidence.get(
            "integrity",
            {},
        )

        if integrity is None:

            integrity = {}

        if not isinstance(
            integrity,
            dict,
        ):
            raise TypeError("Evidence integrity must be a dictionary.")

        integrity = dict(integrity)

        # ------------------------------------------------------------------
        # Normalised Evidence
        # ------------------------------------------------------------------

        #
        # Preserve the original collector evidence.
        #
        # This intentionally remains intact so existing downstream
        # collectors and reporting logic do not lose source-specific
        # fields.
        #
        data = dict(evidence)

        return {
            #
            # Required evidence identifier.
            #
            "id": evidence_id,
            #
            # Required tenant identifier.
            #
            "tenantId": tenant_id,
            #
            # Required collector identifier.
            #
            "collector": collector,
            #
            # Source remains based on the actual evidence
            # file path, preserving existing parser behaviour.
            #
            "source": source,
            #
            # Required evidence type.
            #
            "evidenceType": evidence_type,
            #
            # Optional collection run identifier.
            #
            "collectionRunId": collection_run_id,
            #
            # Required collection timestamp.
            #
            "collectedAt": collected_at,
            #
            # Optional expiry timestamp.
            #
            "expiresAt": expires_at,
            #
            # Evidence classification.
            #
            "classification": classification,
            #
            # Integrity information supplied by
            # the collector, when available.
            #
            "integrity": integrity,
            #
            # Normalised metadata.
            #
            "metadata": metadata,
            #
            # Original collector evidence.
            #
            "data": data,
            #
            # Preserve the original source path as
            # the raw evidence reference.
            #
            "rawReference": raw_reference,
        }

    # ------------------------------------------------------------------
    # Directory Parsing
    # ------------------------------------------------------------------

    def parse_directory(
        self,
        directory: Path,
    ) -> list[dict[str, Any]]:
        """
        Parse all evidence files.
        """

        if not isinstance(
            directory,
            Path,
        ):
            directory = Path(directory)

        results: list[dict[str, Any]] = []

        for file in directory.rglob("*"):

            if file.suffix.lower() in (
                ".json",
                ".yaml",
                ".yml",
            ):

                results.append(self.parse(file))

        return results

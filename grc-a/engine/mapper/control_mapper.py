# engine\mapper\control_mapper.py


"""
Control Mapper

Maps normalised evidence to framework controls.

Supports:

- NCSC CAF
- ISO 42001
- ISO 27001
- SOC 2
- Cyber Essentials
- Government Assurance

Input

Evidence

↓

Framework Definition

↓

Control Mapping

↓

Mapped Controls
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ==============================================================================
# Supported Frameworks
# ==============================================================================


SUPPORTED_FRAMEWORKS = (
    "NCSC_CAF",
    "ISO_42001",
    "ISO_27001",
    "SOC_2",
    "CYBER_ESSENTIALS",
    "GOV_ASSURANCE",
)


# ==============================================================================
# Models
# ==============================================================================


@dataclass(slots=True)
class ControlMapping:
    """
    Represents a single control mapping.

    A control mapping contains all evidence items that matched
    the control during the mapping operation.
    """

    framework: str

    control_id: str

    title: str

    capability: str | None = None

    confidence: float = 1.0

    evidence: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class MappingResult:
    """
    Result returned from a mapping operation.
    """

    framework: str

    mappings: list[ControlMapping] = field(default_factory=list)

    unmapped_evidence: list[dict[str, Any]] = field(default_factory=list)

    @property
    def mapped_controls(self) -> int:
        """
        Return the number of mapped controls.
        """

        return len(self.mappings)

    @property
    def evidence_count(self) -> int:
        """
        Return the total number of evidence items
        attached to mapped controls.
        """

        return sum(
            len(item.evidence)
            for item in self.mappings
        )


# ==============================================================================
# Control Mapper
# ==============================================================================


class ControlMapper:
    """
    Core evidence-to-control mapper.

    The mapper receives a validated framework definition
    and attempts to map normalised evidence to its controls.

    The default implementation performs tag-based matching.

    More advanced rule-based, semantic and confidence-aware
    matching can be introduced later without changing the
    public mapping result model.
    """

    def __init__(self) -> None:

        self._framework: dict[str, Any] = {}

    # ------------------------------------------------------------------

    def load_framework(
        self,
        framework: dict[str, Any],
    ) -> None:
        """
        Load a validated framework definition.

        Args:
            framework:
                Framework definition containing metadata
                and controls.
        """

        if not isinstance(
            framework,
            dict,
        ):
            raise TypeError(
                "Framework definition must be a dictionary."
            )

        self._framework = framework

    # ------------------------------------------------------------------

    def map_evidence(
        self,
        evidence: list[dict[str, Any]],
    ) -> MappingResult:
        """
        Map evidence to framework controls.

        Evidence is matched against control tags.

        Normalised evidence follows the platform evidence schema,
        where tags are normally stored under:

            metadata.tags

        Legacy evidence containing top-level ``tags`` is also
        supported for backwards compatibility.

        Evidence that matches multiple controls is mapped
        to each applicable control.

        Multiple evidence items matching the same control
        are aggregated into a single ControlMapping.

        Evidence that matches no controls is returned in
        ``unmapped_evidence``.
        """

        metadata = self._framework.get(
            "metadata",
            {},
        )

        if not isinstance(
            metadata,
            dict,
        ):
            metadata = {}

        framework_name = metadata.get(
            "id",
            metadata.get(
                "name",
                "Unknown",
            ),
        )

        result = MappingResult(
            framework=framework_name,
        )

        controls = self._framework.get(
            "controls",
            [],
        )

        if not isinstance(
            controls,
            list,
        ):
            return result

        indexed = self._index_controls(
            controls,
        )

        #
        # Keep mappings indexed by control ID so that multiple
        # evidence records are accumulated against the same
        # control rather than producing duplicate mappings.
        #
        mappings_by_control: dict[
            str,
            ControlMapping,
        ] = {}

        for item in evidence:

            if not isinstance(
                item,
                dict,
            ):
                result.unmapped_evidence.append(
                    item
                )

                continue

            matched = False

            for control in indexed.values():

                if not self._matches(
                    item,
                    control,
                ):
                    continue

                control_id = str(
                    control["id"]
                )

                mapping = mappings_by_control.get(
                    control_id
                )

                #
                # First evidence item for this control.
                #
                if mapping is None:

                    mapping = ControlMapping(
                        framework=framework_name,
                        control_id=control_id,
                        title=control.get(
                            "title",
                            control_id,
                        ),
                        capability=control.get(
                            "capability"
                        ),
                        evidence=[],
                    )

                    mappings_by_control[
                        control_id
                    ] = mapping

                #
                # Preserve every matching evidence item.
                #
                if item not in mapping.evidence:
                    mapping.evidence.append(
                        item
                    )

                matched = True

            if not matched:

                result.unmapped_evidence.append(
                    item
                )

        #
        # Preserve framework control ordering by walking the
        # indexed controls rather than relying on dictionary
        # insertion behaviour from evidence processing.
        #
        result.mappings = [
            mappings_by_control[control_id]
            for control_id in indexed
            if control_id in mappings_by_control
        ]

        return result

    # ------------------------------------------------------------------

    @staticmethod
    def _index_controls(
        controls: list[dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """
        Index controls by identifier.

        Controls without a valid ``id`` are ignored.
        """

        return {
            str(control["id"]): control
            for control in controls
            if isinstance(
                control,
                dict,
            )
            and control.get("id")
        }

    # ------------------------------------------------------------------

    @staticmethod
    def _extract_evidence_tags(
        evidence: dict[str, Any],
    ) -> set[str]:
        """
        Extract tags from normalised evidence.

        The platform evidence schema defines tags under:

            metadata.tags

        The mapper also supports:

            tags

        at the top level for backwards compatibility.

        Additionally, tags contained directly inside the
        evidence ``data`` object are supported when present.

        This allows existing collectors and legacy evidence
        records to continue working while the canonical
        evidence contract remains schema-compatible.
        """

        tags: list[Any] = []

        #
        # ------------------------------------------------------------------
        # Canonical schema location:
        #
        # evidence.metadata.tags
        # ------------------------------------------------------------------
        metadata = evidence.get(
            "metadata",
            {},
        )

        if isinstance(
            metadata,
            dict,
        ):
            metadata_tags = metadata.get(
                "tags",
                [],
            )

            if isinstance(
                metadata_tags,
                (list, tuple, set),
            ):
                tags.extend(
                    metadata_tags
                )

        #
        # ------------------------------------------------------------------
        # Legacy top-level location:
        #
        # evidence.tags
        # ------------------------------------------------------------------
        top_level_tags = evidence.get(
            "tags",
            [],
        )

        if isinstance(
            top_level_tags,
            (list, tuple, set),
        ):
            tags.extend(
                top_level_tags
            )

        #
        # ------------------------------------------------------------------
        # Optional data-level location:
        #
        # evidence.data.tags
        #
        # Some collectors may place source-specific tags inside
        # the payload. Supporting this does not change the
        # canonical evidence contract.
        # ------------------------------------------------------------------
        data = evidence.get(
            "data",
            {},
        )

        if isinstance(
            data,
            dict,
        ):
            data_tags = data.get(
                "tags",
                [],
            )

            if isinstance(
                data_tags,
                (list, tuple, set),
            ):
                tags.extend(
                    data_tags
                )

        #
        # Normalise tags consistently.
        #
        return {
            str(tag).strip().lower()
            for tag in tags
            if tag is not None
            and str(tag).strip()
        }

    # ------------------------------------------------------------------

    @staticmethod
    def _extract_control_tags(
        control: dict[str, Any],
    ) -> set[str]:
        """
        Extract and normalise control tags.

        Framework catalogues normally define tags directly
        on the control.

        Malformed or missing tag collections are treated as
        empty rather than causing the mapper to fail.
        """

        control_tags = control.get(
            "tags",
            [],
        )

        if not isinstance(
            control_tags,
            (list, tuple, set),
        ):
            return set()

        return {
            str(tag).strip().lower()
            for tag in control_tags
            if tag is not None
            and str(tag).strip()
        }

    # ------------------------------------------------------------------

    @staticmethod
    def _matches(
        evidence: dict[str, Any],
        control: dict[str, Any],
    ) -> bool:
        """
        Determine whether evidence satisfies a control.

        Default implementation performs tag matching.

        Normalised evidence uses ``metadata.tags`` according
        to ``evidence.schema.json``.

        Legacy top-level tags and optional data-level tags
        are also supported.

        This method is intentionally simple and is designed
        to be overridden by future rule engines.
        """

        evidence_tags = (
            ControlMapper._extract_evidence_tags(
                evidence
            )
        )

        control_tags = (
            ControlMapper._extract_control_tags(
                control
            )
        )

        #
        # A control without tags cannot be matched by the
        # default tag-based mapper.
        #
        if not control_tags:

            return False

        #
        # Evidence without tags cannot be matched.
        #
        if not evidence_tags:

            return False

        #
        # A single shared tag is sufficient for the current
        # tag-based matching behaviour.
        #
        return bool(
            evidence_tags.intersection(
                control_tags
            )
        )

    # ------------------------------------------------------------------

    def summary(
        self,
        result: MappingResult,
    ) -> dict[str, Any]:
        """
        Produce mapping statistics.
        """

        return {
            "framework": result.framework,
            "mapped_controls": result.mapped_controls,
            "mapped_evidence": result.evidence_count,
            "unmapped_evidence": len(
                result.unmapped_evidence
            ),
        }


# ==============================================================================
# Public API
# ==============================================================================


def map_evidence_to_controls(
    framework: dict[str, Any],
    evidence: list[dict[str, Any]],
) -> MappingResult:
    """
    Convenience function for mapping evidence to framework controls.

    Example:

        result = map_evidence_to_controls(
            framework,
            evidence,
        )
    """

    mapper = ControlMapper()

    mapper.load_framework(
        framework
    )

    return mapper.map_evidence(
        evidence
    )

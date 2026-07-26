"""
Control Mapper

Maps normalised evidence to framework controls.

Supports:

- CAF
- ISO27001
- SOC2
- GovAssure
- CyberEssentials

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
# Models
# ==============================================================================


@dataclass(slots=True)
class ControlMapping:
    """
    Represents a single control mapping.
    """

    framework: str

    control_id: str

    title: str

    capability: str | None = None

    confidence: float = 1.0

    evidence: list[dict[str, Any]] = field(
        default_factory=list
    )


@dataclass(slots=True)
class MappingResult:
    """
    Result returned from a mapping operation.
    """

    framework: str

    mappings: list[ControlMapping] = field(
        default_factory=list
    )

    unmapped_evidence: list[dict[str, Any]] = field(
        default_factory=list
    )

    @property
    def mapped_controls(self) -> int:
        return len(self.mappings)

    @property
    def evidence_count(self) -> int:
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
        """

        self._framework = framework

    # ------------------------------------------------------------------

    def map_evidence(
        self,
        evidence: list[dict[str, Any]],
    ) -> MappingResult:
        """
        Map evidence to framework controls.
        """

        metadata = self._framework.get(
            "metadata",
            {}
        )

        framework_name = metadata.get(
            "name",
            "Unknown",
        )

        result = MappingResult(
            framework=framework_name
        )

        controls = self._framework.get(
            "controls",
            []
        )

        indexed = self._index_controls(
            controls
        )

        for item in evidence:

            matched = False

            for control in indexed.values():

                if self._matches(
                    item,
                    control,
                ):

                    mapping = ControlMapping(

                        framework=framework_name,

                        control_id=control["id"],

                        title=control.get(
                            "title",
                            control["id"],
                        ),

                        capability=control.get(
                            "capability"
                        ),

                        evidence=[item],

                    )

                    result.mappings.append(
                        mapping
                    )

                    matched = True

            if not matched:

                result.unmapped_evidence.append(
                    item
                )

        return result

    # ------------------------------------------------------------------

    @staticmethod
    def _index_controls(
        controls: list[dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """
        Index controls by identifier.
        """

        return {

            control["id"]: control

            for control in controls

            if "id" in control

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

        This method is intentionally simple and is
        designed to be overridden by future rule engines.
        """

        evidence_tags = set(
            evidence.get(
                "tags",
                [],
            )
        )

        control_tags = set(
            control.get(
                "tags",
                [],
            )
        )

        if not control_tags:

            return False

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

            "framework":
                result.framework,

            "mapped_controls":
                result.mapped_controls,

            "mapped_evidence":
                result.evidence_count,

            "unmapped_evidence":
                len(
                    result.unmapped_evidence
                ),

        }

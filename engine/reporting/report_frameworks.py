# engine/reporting/report_frameworks.py

"""
Framework Reporting

Builds framework-level report representations from completed assessment
results.

Supported frameworks include:

- ISO 27001
- SOC 2
- CAF
- Cyber Essentials
- GovAssure
- Future frameworks

This module does not calculate compliance, invent statuses, or manufacture
evidence. It transforms existing assessment-layer results into the structured
FrameworkReport / RequirementReport models defined in report_models.py.
"""

from __future__ import annotations

from typing import Any

from .report_helpers import (
    assessment_framework_scores,
    control_confidence,
    control_evidence,
    control_findings,
    control_framework,
    control_identifier,
    control_score,
    control_status,
    control_title,
    controls_for_framework,
    count_statuses,
    enum_value,
    first_value,
    framework_name,
    framework_version,
    get_control_assessments,
    finding_text,
    numeric_value,
    object_to_dict,
    serialise_value,
)
from .report_models import (
    FrameworkReport,
    RequirementReport,
)

# ==============================================================================
# Framework Report Builder
# ==============================================================================


class FrameworkReportBuilder:
    """
    Builds framework-level report models.

    The builder is deliberately framework-agnostic. Framework-specific
    requirements come from the assessment pipeline rather than being
    hard-coded into this reporting layer.
    """

    # ------------------------------------------------------------------
    # Framework Identifier
    # ------------------------------------------------------------------

    @staticmethod
    def framework_identifier(
        framework: Any,
    ) -> str:
        """
        Return a stable framework identifier for report metadata.

        Supports:

        - framework score objects
        - framework objects
        - dictionaries
        - strings
        - enum-like framework identifiers

        No framework is invented. If no usable identifier exists,
        "Unknown" is returned.
        """

        #
        # A plain string is already a usable identifier.
        #
        if isinstance(
            framework,
            str,
        ):
            return framework

        #
        # A framework score normally contains a "framework" object.
        #
        data = object_to_dict(framework)

        framework_object = data.get(
            "framework",
            getattr(
                framework,
                "framework",
                None,
            ),
        )

        #
        # If the supplied object is itself the framework object,
        # use it directly.
        #
        if framework_object is None:
            framework_object = framework

        #
        # Extract the framework name/id when represented as an object
        # or dictionary.
        #
        framework_object_data = object_to_dict(framework_object)

        name = first_value(
            framework_object_data,
            (
                "name",
                "id",
                "framework",
                "framework_id",
            ),
        )

        #
        # If the framework object is already a primitive value, preserve it.
        #
        if name is None:
            name = framework_object

        #
        # Handle enum-like framework identifiers.
        #
        name = enum_value(name)

        if name is None:
            return "Unknown"

        return str(serialise_value(name))

    # ------------------------------------------------------------------
    # Framework Collection
    # ------------------------------------------------------------------

    def build_frameworks(
        self,
        assessment: Any,
    ) -> list[FrameworkReport]:
        """
        Build one FrameworkReport for every framework present in the
        assessment.

        Frameworks are sourced from assessment.framework_scores.

        Control results are also used when they explicitly identify their
        framework.
        """

        framework_scores = assessment_framework_scores(assessment)

        controls = get_control_assessments(assessment)

        reports: list[FrameworkReport] = []

        #
        # Prefer the framework scores because they represent the
        # assessment pipeline's framework-level result.
        #
        for framework_score in framework_scores:

            report = self.build_framework(
                framework_score=framework_score,
                controls=controls,
            )

            if report is not None:
                reports.append(report)

        #
        # If framework scores are unavailable, derive framework names
        # only from actual control results. No framework is invented.
        #
        if not reports:

            framework_names = self._framework_names_from_controls(controls)

            for name in framework_names:

                report = self.build_framework_from_controls(
                    framework=name,
                    controls=controls,
                )

                if report is not None:
                    reports.append(report)

        return reports

    # ------------------------------------------------------------------
    # Single Framework
    # ------------------------------------------------------------------

    def build_framework(
        self,
        framework_score: Any,
        controls: list[Any] | None = None,
    ) -> FrameworkReport | None:
        """
        Build a FrameworkReport from an existing framework score.

        Existing framework-level score/status/coverage values are preserved.
        Control counts are based only on controls explicitly associated with
        the framework.
        """

        name = framework_name(framework_score)

        if name is None:
            return None

        version = framework_version(framework_score)

        data = object_to_dict(framework_score)

        score = first_value(
            data,
            (
                "score",
                "framework_score",
                "overall_score",
            ),
        )

        status = first_value(
            data,
            (
                "status",
                "result",
                "outcome",
                "compliance_status",
            ),
        )

        status = enum_value(status)

        if controls is None:
            controls = []

        framework_controls = controls_for_framework(
            controls,
            name,
        )

        #
        # Some assessment implementations attach controls directly to
        # the framework score. Prefer those if present.
        #
        attached_controls = self._framework_controls(framework_score)

        if attached_controls:
            framework_controls = attached_controls

        requirements = [
            self.build_requirement(control) for control in framework_controls
        ]

        requirements = [
            requirement for requirement in requirements if requirement is not None
        ]

        counts = count_statuses(framework_controls)

        total_requirements = self._total_requirements(
            framework_score,
            len(requirements),
        )

        #
        # If the framework score explicitly supplies summary counts,
        # preserve them. Otherwise use counts from the actual control
        # assessments.
        #
        met = self._summary_count(
            data,
            (
                "met",
                "requirements_met",
                "controls_met",
            ),
            counts["met"],
        )

        partially_met = self._summary_count(
            data,
            (
                "partially_met",
                "partial",
                "requirements_partially_met",
                "controls_partially_met",
            ),
            counts["partially_met"],
        )

        not_met = self._summary_count(
            data,
            (
                "not_met",
                "requirements_not_met",
                "controls_not_met",
            ),
            counts["not_met"],
        )

        not_applicable = self._summary_count(
            data,
            (
                "not_applicable",
                "requirements_not_applicable",
                "controls_not_applicable",
            ),
            counts["not_applicable"],
        )

        #
        # If an explicit total exists, preserve it. Otherwise use the
        # number of requirements represented in the report.
        #
        if total_requirements == 0:
            total_requirements = met + partially_met + not_met + not_applicable

        return FrameworkReport(
            framework=name,
            version=version,
            score=numeric_value(score),
            status=(str(serialise_value(status)) if status is not None else None),
            total_requirements=total_requirements,
            met=met,
            partially_met=partially_met,
            not_met=not_met,
            not_applicable=not_applicable,
            requirements=requirements,
        )

    # ------------------------------------------------------------------
    # Framework From Controls
    # ------------------------------------------------------------------

    def build_framework_from_controls(
        self,
        framework: str,
        controls: list[Any],
    ) -> FrameworkReport | None:
        """
        Build a FrameworkReport when only control-level results are
        available.

        No framework score or compliance status is calculated here.
        """

        framework_controls = controls_for_framework(
            controls,
            framework,
        )

        if not framework_controls:
            return None

        requirements = [
            self.build_requirement(control) for control in framework_controls
        ]

        requirements = [
            requirement for requirement in requirements if requirement is not None
        ]

        counts = count_statuses(framework_controls)

        total_requirements = len(requirements)

        return FrameworkReport(
            framework=framework,
            version=None,
            score=None,
            status=None,
            total_requirements=total_requirements,
            met=counts["met"],
            partially_met=counts["partially_met"],
            not_met=counts["not_met"],
            not_applicable=counts["not_applicable"],
            requirements=requirements,
        )

    # ------------------------------------------------------------------
    # Requirement
    # ------------------------------------------------------------------

    def build_requirement(
        self,
        control: Any,
    ) -> RequirementReport | None:
        """
        Convert one existing control assessment into RequirementReport.

        No control result is generated here.
        """

        identifier = control_identifier(control)

        if identifier is None:
            return None

        title = control_title(control)

        status = control_status(control)

        confidence = control_confidence(control)

        score = control_score(control)

        findings = control_findings(control)

        evidence = control_evidence(control)

        #
        # Some assessment models expose a single finding while others
        # expose a list of findings. Both are preserved.
        #
        finding = finding_text(findings)

        normalized_evidence = self._normalize_evidence(evidence)

        return RequirementReport(
            requirement_id=str(serialise_value(identifier)),
            title=(str(serialise_value(title)) if title is not None else None),
            status=(str(serialise_value(status)) if status is not None else None),
            confidence=(
                str(serialise_value(confidence)) if confidence is not None else None
            ),
            score=numeric_value(score),
            finding=finding,
            evidence=normalized_evidence,
        )

    # ------------------------------------------------------------------
    # Framework Controls
    # ------------------------------------------------------------------

    @staticmethod
    def _framework_controls(
        framework_score: Any,
    ) -> list[Any]:
        """
        Retrieve controls directly attached to a framework score.

        Supports common assessment model aliases.
        """

        for attribute_name in (
            "control_assessments",
            "controls",
            "control_scores",
            "requirements",
            "requirement_scores",
        ):

            value = getattr(
                framework_score,
                attribute_name,
                None,
            )

            if value is None:
                continue

            if isinstance(
                value,
                dict,
            ):
                controls: list[Any] = []

                for item in value.values():

                    if isinstance(
                        item,
                        (list, tuple, set),
                    ):
                        controls.extend(item)

                    else:
                        controls.append(item)

                if controls:
                    return controls

            elif isinstance(
                value,
                (list, tuple, set),
            ):
                return list(value)

            else:
                return [value]

        return []

    # ------------------------------------------------------------------
    # Summary Counts
    # ------------------------------------------------------------------

    @staticmethod
    def _summary_count(
        data: dict[str, Any],
        names: tuple[str, ...],
        fallback: int,
    ) -> int:
        """
        Return an explicitly supplied summary count where available.

        Otherwise use the supplied fallback.
        """

        value = first_value(
            data,
            names,
        )

        if value is None:
            return fallback

        try:
            return int(value)

        except (
            TypeError,
            ValueError,
        ):
            return fallback

    @staticmethod
    def _total_requirements(
        framework_score: Any,
        fallback: int,
    ) -> int:
        """
        Retrieve an explicitly supplied requirement/control count.
        """

        data = object_to_dict(framework_score)

        value = first_value(
            data,
            (
                "total_requirements",
                "requirement_count",
                "control_count",
                "total_controls",
                "controls_assessed",
            ),
        )

        if value is None:
            return fallback

        try:
            return int(value)

        except (
            TypeError,
            ValueError,
        ):
            return fallback

    # ------------------------------------------------------------------
    # Evidence
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_evidence(
        evidence: Any,
    ) -> list[Any]:
        """
        Normalize evidence while preserving the evidence supplied by the
        assessment pipeline.
        """

        if evidence is None:
            return []

        if isinstance(
            evidence,
            (list, tuple, set),
        ):
            return [serialise_value(item) for item in evidence]

        return [serialise_value(evidence)]

    # ------------------------------------------------------------------
    # Framework Discovery
    # ------------------------------------------------------------------

    @staticmethod
    def _framework_names_from_controls(
        controls: list[Any],
    ) -> list[str]:
        """
        Discover framework names from controls that explicitly identify
        their framework.

        Order is preserved and duplicate framework names are removed.
        """

        names: list[str] = []
        seen: set[str] = set()

        for control in controls:

            framework = control_framework(control)

            if framework is None:
                continue

            name = str(serialise_value(framework))

            key = name.upper()

            if key in seen:
                continue

            seen.add(key)

            names.append(name)

        return names


# ==============================================================================
# Public API
# ==============================================================================


def build_framework_reports(
    assessment: Any,
) -> list[FrameworkReport]:
    """
    Convenience API for framework report construction.
    """

    builder = FrameworkReportBuilder()

    return builder.build_frameworks(assessment)


def build_framework_report(
    framework_score: Any,
    controls: list[Any] | None = None,
) -> FrameworkReport | None:
    """
    Convenience API for constructing a single framework report.
    """

    builder = FrameworkReportBuilder()

    return builder.build_framework(
        framework_score=framework_score,
        controls=controls,
    )


def build_requirement_report(
    control: Any,
) -> RequirementReport | None:
    """
    Convenience API for constructing a single requirement report.
    """

    builder = FrameworkReportBuilder()

    return builder.build_requirement(control)

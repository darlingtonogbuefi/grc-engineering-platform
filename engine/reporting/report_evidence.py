# engine/reporting/report_evidence.py

"""
Evidence Reporting

Contains evidence-related reporting logic extracted from report_generator.py.

Responsibilities:

- Evidence summary reporting
- Control-level evidence reporting
- Evidence lookup construction
- Control assessment discovery
- Control assessment normalization
- Evidence ID resolution
- Observed evidence normalization
- Standard evidence table reporting

This module consumes evidence and control assessment results produced by
the assessment/scoring pipeline.

It does not:

- calculate compliance
- determine control status
- invent findings
- invent evidence
- modify assessment results

The original ReportGenerator behaviour is preserved through the
EvidenceReporter class.

The standard evidence-table representation is delegated to
EvidenceTableBuilder in evidence_table.py so that all reporting outputs
use one framework/provider-independent evidence normalization path.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from ..scoring.scoring_engine import AssessmentScore

# EvidenceTableBuilder lives in its own module.
#
# IMPORTANT:
# Do not use:
#
#     from .report_evidence import EvidenceReporter, EvidenceTableBuilder
#
# here because this file IS report_evidence.py.
#
# Change the module name below if your EvidenceTableBuilder class is stored
# in a different file.
from .evidence_table import EvidenceTableBuilder

from .report_helpers import (
    enum_value,
    first_value,
    object_name,
    object_to_dict,
    serialise_value,
)

# ==============================================================================
# Evidence Reporter
# ==============================================================================


class EvidenceReporter:
    """
    Produces evidence-related report sections.

    All values are consumed from the completed AssessmentScore or from
    control assessment objects attached to it.
    """

    # ------------------------------------------------------------------
    # Evidence Summary
    # ------------------------------------------------------------------

    @staticmethod
    def evidence_summary(
        assessment: AssessmentScore,
    ):
        """
        Produce the evidence collection and scoring summary.

        Includes:

        - Evidence identifiers
        - Evidence scores
        - Confidence values
        - Findings
        - Original collected evidence when available

        No evidence is created by this method.
        """

        from .report_models import ReportSection

        evidence_scores = [
            {
                "evidence_id": evidence.evidence_id,
                "score": evidence.score,
                "confidence": evidence.confidence,
                "findings": list(evidence.findings),
            }
            for evidence in assessment.evidence_scores
        ]

        content: dict[str, Any] = {
            "evidence_count": len(assessment.evidence_scores),
            "evidence_scores": evidence_scores,
        }

        #
        # Support the extended AssessmentScore model where the original
        # collected evidence is retained.
        #
        # This keeps the reporting layer backward compatible with
        # AssessmentScore objects that do not yet expose an "evidence"
        # attribute.
        #
        collected_evidence = getattr(
            assessment,
            "evidence",
            None,
        )

        if collected_evidence is not None:
            content["collected_evidence"] = collected_evidence

        return ReportSection(
            title="Evidence Summary",
            content=content,
        )

    # ------------------------------------------------------------------
    # Control Evidence Summary
    # ------------------------------------------------------------------

    @classmethod
    def control_evidence_summary(
        cls,
        assessment: AssessmentScore,
    ):
        """
        Produce the standard control-level evidence section.

        This section is deliberately evidence-driven.

        The reporting layer does NOT determine whether a control passes.
        It consumes the control assessment produced by the assessment
        pipeline.

        A normal control evidence record can contain:

            {
                "framework": "ISO27001",
                "control_id": "A.8.2",
                "title": "Privileged access rights",
                "status": "PASS",
                "evidence_source": "Microsoft Entra ID / Microsoft Graph",
                "observed_evidence": [
                    "2 high-privilege roles",
                    "2 assignments",
                    "Global Administrator -> user",
                    "User Administrator -> user",
                ],
            }

        The method also supports the current ControlScore model produced
        by ScoringEngine. In that model, a control can contain:

            - control_id
            - score
            - evidence_count
            - findings

        No PASS/FAIL status is invented when the scoring model does not
        provide one.
        """

        from .report_models import ReportSection

        control_assessments = cls._get_control_assessments(
            assessment,
        )

        controls: list[dict[str, Any]] = []

        #
        # Build an evidence lookup once. This allows a richer control
        # assessment to reference evidence by evidence_id without
        # requiring the reporting layer to manufacture evidence.
        #
        evidence_lookup = cls._build_evidence_lookup(
            assessment,
        )

        for control in control_assessments:

            normalized = cls._normalize_control_assessment(
                control,
                evidence_lookup=evidence_lookup,
            )

            #
            # Ignore completely empty objects rather than producing
            # meaningless rows in the report.
            #
            if not normalized:
                continue

            controls.append(
                normalized,
            )

        return ReportSection(
            title="Live Control Evidence",
            content={
                "assessment_type": ("Control-level evidence assessment"),
                "controls": controls,
            },
        )

    # ------------------------------------------------------------------
    # Standard Evidence Table
    # ------------------------------------------------------------------

    @classmethod
    def evidence_table(
        cls,
        assessment: AssessmentScore,
    ):
        """
        Build the standard framework-independent evidence table.

        EvidenceTableBuilder is the single normalization path for this
        report table.

        The table uses the same columns for every provider/framework:

            selection
            time
            compliance_check
            evidence_by_type
            data_source
            event_name
            event_source
            assessment_report_selection

        The method does not invent evidence.

        It only converts evidence already attached to the assessment
        into the standard reporting representation.

        EvidenceTableBuilder supports:

            - dictionaries
            - wrapped {"data": {...}} records
            - EvidenceRecord-style objects
            - Pydantic v1 models
            - Pydantic v2 models

        Therefore this method deliberately does not duplicate evidence
        normalization logic here.
        """

        from .report_models import ReportSection

        collected_evidence = cls._get_collected_evidence(
            assessment,
        )

        #
        # Materialise the iterable once.

        # This preserves support for lists/tuples while also allowing
        # generators and other iterable evidence collections.
        #
        evidence_records = cls._materialize_evidence(
            collected_evidence,
        )

        builder = EvidenceTableBuilder(
            title=f"Evidence ({len(evidence_records)})",
        )

        #
        # EvidenceTableBuilder is responsible for:
        #
        # - extracting evidence data
        # - resolving standard field names
        # - applying default values
        # - formatting timestamps
        # - formatting compliance status
        # - converting values into report text
        #
        builder.add_records(
            evidence_records,
        )

        table = builder.build()

        return ReportSection(
            title=table.title,
            content=table.to_dict(),
        )

    # ------------------------------------------------------------------
    # Evidence Collection Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_collected_evidence(
        assessment: AssessmentScore,
    ) -> Any:
        """
        Retrieve collected evidence from AssessmentScore.

        This remains backward compatible with AssessmentScore models
        that do not expose an ``evidence`` attribute.
        """

        return getattr(
            assessment,
            "evidence",
            None,
        )

    @staticmethod
    def _materialize_evidence(
        collected_evidence: Any,
    ) -> list[Any]:
        """
        Convert the collected evidence container into a stable list.

        Supported forms include:

            - list
            - tuple
            - set
            - generators
            - other iterable collections

        Strings and mappings are treated as individual evidence records
        rather than iterated character-by-character or key-by-key.

        Unsupported or missing values produce an empty list.

        No evidence is created by this method.
        """

        if collected_evidence is None:
            return []

        #
        # A mapping can itself represent a single evidence record.
        #
        if isinstance(
            collected_evidence,
            Mapping,
        ):
            return [
                collected_evidence,
            ]

        #
        # Strings represent one value, not an iterable of evidence
        # characters.
        #
        if isinstance(
            collected_evidence,
            (str, bytes),
        ):
            return [
                collected_evidence,
            ]

        #
        # Preserve normal collection behaviour.
        #
        if isinstance(
            collected_evidence,
            (list, tuple, set),
        ):
            return list(
                collected_evidence,
            )

        #
        # Support generators and other iterable evidence collections.
        #
        if isinstance(
            collected_evidence,
            Iterable,
        ):

            try:
                return list(
                    collected_evidence,
                )

            except TypeError:
                return []

        #
        # A single evidence object is still a valid record.
        #
        return [
            collected_evidence,
        ]

    # ------------------------------------------------------------------
    # Evidence Lookup
    # ------------------------------------------------------------------

    @classmethod
    def _build_evidence_lookup(
        cls,
        assessment: AssessmentScore,
    ) -> dict[str, dict[str, Any]]:
        """
        Build an evidence lookup indexed by evidence_id.

        The lookup is only used when a control assessment refers to
        evidence by identifier.

        No evidence is created by this method.

        Evidence records are normalized using EvidenceTableBuilder's
        extraction logic so that dictionary, wrapped dictionary,
        EvidenceRecord-style, and Pydantic evidence records are handled
        consistently.
        """

        lookup: dict[str, dict[str, Any]] = {}

        collected_evidence = cls._get_collected_evidence(
            assessment,
        )

        evidence_records = cls._materialize_evidence(
            collected_evidence,
        )

        for item in evidence_records:

            #
            # Use the same extraction mechanism as the standard evidence
            # table. This prevents the lookup path from having a different
            # understanding of what constitutes an evidence record.
            #
            data = EvidenceTableBuilder.extract_data(
                item,
            )

            if not data:
                continue

            evidence_id = data.get(
                "evidence_id",
            )

            if evidence_id is None:
                continue

            lookup[str(evidence_id)] = data

        return lookup

    # ------------------------------------------------------------------
    # Control Assessment Discovery
    # ------------------------------------------------------------------

    @staticmethod
    def _get_control_assessments(
        assessment: AssessmentScore,
    ) -> list[Any]:
        """
        Retrieve control assessments from AssessmentScore.

        Different versions of the assessment/scoring models may expose
        control results under different attribute names.

        Preferred attributes:

        - control_assessments
        - controls
        - control_scores

        The method deliberately does not construct controls from
        framework names or scores.

        A control must come from the assessment pipeline.
        """

        candidate_attributes = (
            "control_assessments",
            "controls",
            "control_scores",
        )

        for attribute_name in candidate_attributes:

            value = getattr(
                assessment,
                attribute_name,
                None,
            )

            if value is None:
                continue

            if isinstance(
                value,
                dict,
            ):
                #
                # Some assessment implementations group controls
                # by framework.
                #
                flattened: list[Any] = []

                for item in value.values():

                    if isinstance(
                        item,
                        list,
                    ):
                        flattened.extend(
                            item,
                        )

                    elif isinstance(
                        item,
                        tuple,
                    ):
                        flattened.extend(
                            item,
                        )

                    else:
                        flattened.append(
                            item,
                        )

                return flattened

            if isinstance(
                value,
                (list, tuple),
            ):
                return list(
                    value,
                )

            #
            # A single control assessment object is also supported.
            #
            return [value]

        #
        # Backward compatibility:
        #
        # Some assessment models may expose control results through
        # framework scores.
        #
        framework_controls: list[Any] = []

        for framework_score in getattr(
            assessment,
            "framework_scores",
            [],
        ):

            for attribute_name in (
                "control_assessments",
                "controls",
                "control_scores",
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

                    for item in value.values():

                        if isinstance(
                            item,
                            list,
                        ):
                            framework_controls.extend(
                                item,
                            )

                        elif isinstance(
                            item,
                            tuple,
                        ):
                            framework_controls.extend(
                                item,
                            )

                        else:
                            framework_controls.append(
                                item,
                            )

                elif isinstance(
                    value,
                    (list, tuple),
                ):
                    framework_controls.extend(
                        value,
                    )

                else:
                    framework_controls.append(
                        value,
                    )

                #
                # Once a recognised control collection has been
                # found for this framework score, do not inspect
                # another alias and accidentally duplicate it.
                #
                break

        return framework_controls

    # ------------------------------------------------------------------
    # Control Assessment Normalization
    # ------------------------------------------------------------------

    @classmethod
    def _normalize_control_assessment(
        cls,
        control: Any,
        evidence_lookup: dict[str, dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Convert an assessment-layer control object into the standard
        reporting representation.

        No assessment value is invented.

        Missing fields remain absent or use an empty collection where
        appropriate.

        ``evidence_lookup`` allows evidence_ids supplied by the
        assessment layer to be expanded into the original collected
        evidence when those records are available.
        """

        data = object_to_dict(
            control,
        )

        if not data:
            return {}

        evidence_lookup = evidence_lookup or {}

        #
        # Framework
        #
        framework = first_value(
            data,
            (
                "framework",
                "framework_id",
                "framework_name",
            ),
        )

        framework = object_name(
            framework,
        )

        #
        # Control ID
        #
        control_id = first_value(
            data,
            (
                "control_id",
                "control",
                "id",
            ),
        )

        #
        # Control title / requirement
        #
        title = first_value(
            data,
            (
                "title",
                "control_title",
                "name",
                "requirement",
                "description",
            ),
        )

        #
        # Status
        #
        status = first_value(
            data,
            (
                "status",
                "result",
                "outcome",
            ),
        )

        status = enum_value(
            status,
        )

        #
        # Score
        #
        score = first_value(
            data,
            (
                "score",
                "control_score",
            ),
        )

        #
        # Evidence count
        #
        evidence_count = first_value(
            data,
            (
                "evidence_count",
                "mapped_evidence_count",
            ),
        )

        #
        # Coverage
        #
        coverage = first_value(
            data,
            (
                "coverage",
                "control_coverage",
            ),
        )

        #
        # Reason
        #
        reason = first_value(
            data,
            (
                "reason",
                "rationale",
                "assessment_reason",
            ),
        )

        #
        # Evidence source
        #
        evidence_source = first_value(
            data,
            (
                "evidence_source",
                "source",
                "evidence_provider",
            ),
        )

        #
        # Findings
        #
        findings = first_value(
            data,
            (
                "findings",
                "issues",
                "observations",
            ),
        )

        #
        # Observed evidence
        #
        observed_evidence = first_value(
            data,
            (
                "observed_evidence",
                "evidence",
                "observations",
                "evidence_items",
            ),
        )

        observed_evidence = cls._normalize_observed_evidence(
            observed_evidence,
        )

        #
        # If the assessment supplies evidence IDs but not expanded
        # evidence, resolve those IDs against the original collected
        # evidence where possible.
        #
        if not observed_evidence:

            evidence_ids = first_value(
                data,
                (
                    "evidence_ids",
                    "mapped_evidence_ids",
                ),
            )

            resolved_evidence = cls._resolve_evidence_ids(
                evidence_ids,
                evidence_lookup,
            )

            if resolved_evidence:
                observed_evidence = resolved_evidence

        #
        # Build the standard reporting object.
        #
        result: dict[str, Any] = {}

        if framework is not None:
            result["framework"] = serialise_value(
                framework,
            )

        if control_id is not None:
            result["control_id"] = serialise_value(
                control_id,
            )

        if title is not None:
            result["title"] = serialise_value(
                title,
            )

        if status is not None:
            result["status"] = serialise_value(
                status,
            )

        if score is not None:
            result["score"] = serialise_value(
                score,
            )

        if evidence_count is not None:
            result["evidence_count"] = serialise_value(
                evidence_count,
            )

        if coverage is not None:
            result["coverage"] = serialise_value(
                coverage,
            )

        if reason is not None:
            result["reason"] = serialise_value(
                reason,
            )

        if evidence_source is not None:
            result["evidence_source"] = serialise_value(
                evidence_source,
            )

        if findings is not None:
            result["findings"] = serialise_value(
                findings,
            )

        #
        # Always provide observed_evidence as a list when the
        # assessment model supplied evidence.
        #
        if observed_evidence:
            result["observed_evidence"] = observed_evidence

        #
        # Preserve useful evidence-related fields that may be
        # supplied by a collector/evaluator but are not part of
        # the minimum standard representation.
        #
        for field_name in (
            "evidence_ids",
            "mapped_evidence_ids",
            "assignment_count",
            "members",
            "roles",
        ):

            if field_name not in data:
                continue

            if field_name in result:
                continue

            result[field_name] = serialise_value(
                data[field_name],
            )

        return result

    # ------------------------------------------------------------------
    # Evidence ID Resolution
    # ------------------------------------------------------------------

    @classmethod
    def _resolve_evidence_ids(
        cls,
        evidence_ids: Any,
        evidence_lookup: dict[str, dict[str, Any]],
    ) -> list[Any]:
        """
        Resolve evidence IDs into original evidence records.

        Only IDs that actually exist in the collected evidence are
        returned.

        Missing IDs are not converted into fabricated evidence.
        """

        if not evidence_ids:
            return []

        if isinstance(
            evidence_ids,
            (str, int),
        ):
            evidence_ids = [
                evidence_ids,
            ]

        if not isinstance(
            evidence_ids,
            (list, tuple, set),
        ):
            return []

        resolved: list[Any] = []

        for evidence_id in evidence_ids:

            item = evidence_lookup.get(
                str(evidence_id),
            )

            if item is not None:
                resolved.append(
                    serialise_value(
                        item,
                    ),
                )

        return resolved

    # ------------------------------------------------------------------
    # Observed Evidence Normalization
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_observed_evidence(
        evidence: Any,
    ) -> list[Any]:
        """
        Normalize observed evidence into a report-friendly list.

        The underlying evidence is preserved. This method only converts
        common object representations into serialisable values.
        """

        if evidence is None:
            return []

        if isinstance(
            evidence,
            (list, tuple, set),
        ):
            return [
                serialise_value(
                    item,
                )
                for item in evidence
            ]

        #
        # A dictionary can itself represent one evidence item.
        #
        if isinstance(
            evidence,
            dict,
        ):
            return [
                serialise_value(
                    evidence,
                ),
            ]

        return [
            serialise_value(
                evidence,
            ),
        ]


# ==============================================================================
# Module-Level Compatibility API
# ==============================================================================


def evidence_summary(
    assessment: AssessmentScore,
):
    """
    Compatibility wrapper for callers that prefer a module-level API.
    """

    return EvidenceReporter.evidence_summary(
        assessment,
    )


def control_evidence_summary(
    assessment: AssessmentScore,
):
    """
    Compatibility wrapper for callers that prefer a module-level API.
    """

    return EvidenceReporter.control_evidence_summary(
        assessment,
    )


def evidence_table(
    assessment: AssessmentScore,
):
    """
    Compatibility wrapper for callers that prefer a module-level API.

    Builds the standard framework-independent evidence table through
    EvidenceTableBuilder.
    """

    return EvidenceReporter.evidence_table(
        assessment,
    )

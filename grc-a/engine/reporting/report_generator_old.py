# engine\reporting\report_generator.py

"""
Report Generator

Creates reporting objects from completed assessments.

Supports:

- Executive reporting
- Technical reporting
- Evidence reporting
- Framework reporting
- Compliance summaries
- Control assessment reporting
- Control evidence reporting
- Risk summaries

The reporting layer consumes assessment results and evidence produced by
the assessment pipeline. It does not invent control results or evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from ..scoring.scoring_engine import AssessmentScore


# ==============================================================================
# Report Models
# ==============================================================================


@dataclass(slots=True)
class ReportMetadata:
    """
    Report metadata.
    """

    title: str
    tenant: str
    generated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    frameworks: list[str] = field(
        default_factory=list
    )
    version: str = "1.0"


@dataclass(slots=True)
class ReportSection:
    """
    Individual report section.
    """

    title: str
    content: dict[str, Any]


@dataclass(slots=True)
class ReportDocument:
    """
    Complete report.
    """

    metadata: ReportMetadata
    sections: list[ReportSection] = field(
        default_factory=list
    )


# ==============================================================================
# Report Generator
# ==============================================================================


class ReportGenerator:
    """
    Generates report objects from assessment results.

    Control-level evidence is taken from the completed assessment object.
    The reporting layer does not manufacture control results, statuses,
    scores, or evidence.
    """

    def __init__(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Report Generation
    # ------------------------------------------------------------------

    def generate(
        self,
        assessment: AssessmentScore,
        tenant: str = "default",
    ) -> ReportDocument:
        """
        Generate complete report.

        The report contains:

        - Executive Summary
        - Evidence Summary
        - Live Control Evidence
        - Framework Summary
        - Capability Summary
        - Risk Summary
        """

        metadata = ReportMetadata(
            title="Compliance Assessment",
            tenant=tenant,
            frameworks=[
                self._framework_identifier(
                    framework
                )
                for framework in assessment.framework_scores
            ],
        )

        report = ReportDocument(
            metadata=metadata,
        )

        report.sections.extend(
            [
                self.executive_summary(
                    assessment
                ),
                self.evidence_summary(
                    assessment
                ),
                self.control_evidence_summary(
                    assessment
                ),
                self.framework_summary(
                    assessment
                ),
                self.capability_summary(
                    assessment
                ),
                self.risk_summary(
                    assessment
                ),
            ]
        )

        return report

    # ------------------------------------------------------------------
    # Executive Summary
    # ------------------------------------------------------------------

    @staticmethod
    def executive_summary(
        assessment: AssessmentScore,
    ) -> ReportSection:
        """
        Executive overview.
        """

        return ReportSection(
            title="Executive Summary",
            content=dict(
                assessment.executive_summary
            ),
        )

    # ------------------------------------------------------------------
    # Evidence Summary
    # ------------------------------------------------------------------

    @staticmethod
    def evidence_summary(
        assessment: AssessmentScore,
    ) -> ReportSection:
        """
        Evidence collection and scoring summary.

        Includes the evidence identifiers, quality scores,
        confidence values, and findings produced by the
        scoring engine.

        If the AssessmentScore contains the original evidence
        records, those records are also included in the report.
        """

        evidence_scores = [
            {
                "evidence_id": evidence.evidence_id,
                "score": evidence.score,
                "confidence": evidence.confidence,
                "findings": list(
                    evidence.findings
                ),
            }
            for evidence in assessment.evidence_scores
        ]

        content: dict[str, Any] = {
            "evidence_count": len(
                assessment.evidence_scores
            ),
            "evidence_scores": evidence_scores,
        }

        #
        # Support the extended AssessmentScore model where the
        # original collected evidence is retained.
        #
        # This keeps the reporting layer backward compatible with
        # existing AssessmentScore objects that do not yet have
        # an "evidence" attribute.
        #
        collected_evidence = getattr(
            assessment,
            "evidence",
            None,
        )

        if collected_evidence is not None:
            content["collected_evidence"] = (
                collected_evidence
            )

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
    ) -> ReportSection:
        """
        Produce the standard control-level evidence section.

        This section is deliberately evidence-driven.

        The reporting layer does NOT determine whether a control passes.
        It consumes the control assessment produced by the assessment
        pipeline.

        A normal control evidence record has the following structure:

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

        If no control-level evidence has been attached to the assessment,
        an empty list is returned rather than inventing an assessment.

        The method also supports the current ControlScore model produced
        by ScoringEngine. In that model, a control has:

            - control_id
            - score
            - evidence_count
            - findings

        No PASS/FAIL status is invented when the scoring model does not
        provide one.
        """

        control_assessments = (
            cls._get_control_assessments(
                assessment
            )
        )

        controls: list[dict[str, Any]] = []

        #
        # Build an evidence lookup once. This allows a richer control
        # assessment to reference evidence by evidence_id without
        # requiring the reporting layer to manufacture evidence.
        #
        evidence_lookup = cls._build_evidence_lookup(
            assessment
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
                normalized
            )

        return ReportSection(
            title="Live Control Evidence",
            content={
                "assessment_type": (
                    "Control-level evidence assessment"
                ),
                "controls": controls,
            },
        )

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
        """

        lookup: dict[str, dict[str, Any]] = {}

        collected_evidence = getattr(
            assessment,
            "evidence",
            None,
        )

        if not isinstance(
            collected_evidence,
            (list, tuple),
        ):
            return lookup

        for item in collected_evidence:

            if not isinstance(
                item,
                dict,
            ):
                continue

            evidence_id = item.get(
                "evidence_id"
            )

            if evidence_id is None:
                continue

            lookup[str(evidence_id)] = item

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

        The preferred attributes are:

        - control_assessments
        - controls
        - control_scores

        The method deliberately does not construct controls from
        framework names or scores. A control must come from the
        assessment pipeline.

        The current AssessmentScore model exposes ``control_scores``,
        so those results are explicitly supported.
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
                            item
                        )

                    elif isinstance(
                        item,
                        tuple,
                    ):
                        flattened.extend(
                            item
                        )

                    else:
                        flattened.append(
                            item
                        )

                return flattened

            if isinstance(
                value,
                (list, tuple),
            ):
                return list(value)

            #
            # A single control assessment object is also supported.
            #
            return [value]

        #
        # Backward compatibility:
        #
        # Some assessment models may expose control results through
        # framework scores. Only use them if they actually contain
        # control-level assessment objects.
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
                                item
                            )

                        elif isinstance(
                            item,
                            tuple,
                        ):
                            framework_controls.extend(
                                item
                            )

                        else:
                            framework_controls.append(
                                item
                            )

                elif isinstance(
                    value,
                    (list, tuple),
                ):
                    framework_controls.extend(
                        value
                    )

                else:
                    framework_controls.append(
                        value
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
        assessment layer to be expanded into the original evidence
        records when those records are available.
        """

        data = cls._object_to_dict(
            control
        )

        if not data:
            return {}

        evidence_lookup = evidence_lookup or {}

        #
        # Framework
        #
        framework = cls._first_value(
            data,
            (
                "framework",
                "framework_id",
                "framework_name",
            ),
        )

        framework = cls._object_name(
            framework
        )

        #
        # Control ID
        #
        control_id = cls._first_value(
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
        title = cls._first_value(
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
        status = cls._first_value(
            data,
            (
                "status",
                "result",
                "outcome",
            ),
        )

        status = cls._enum_value(
            status
        )

        #
        # Score
        #
        score = cls._first_value(
            data,
            (
                "score",
                "control_score",
            ),
        )

        #
        # Evidence count
        #
        evidence_count = cls._first_value(
            data,
            (
                "evidence_count",
                "mapped_evidence_count",
            ),
        )

        #
        # Coverage
        #
        coverage = cls._first_value(
            data,
            (
                "coverage",
                "control_coverage",
            ),
        )

        #
        # Reason
        #
        reason = cls._first_value(
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
        evidence_source = cls._first_value(
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
        findings = cls._first_value(
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
        observed_evidence = cls._first_value(
            data,
            (
                "observed_evidence",
                "evidence",
                "observations",
                "evidence_items",
            ),
        )

        observed_evidence = (
            cls._normalize_observed_evidence(
                observed_evidence
            )
        )

        #
        # If the assessment supplies evidence IDs but not expanded
        # evidence, resolve those IDs against the original collected
        # evidence where possible.
        #
        if not observed_evidence:

            evidence_ids = cls._first_value(
                data,
                (
                    "evidence_ids",
                    "mapped_evidence_ids",
                ),
            )

            resolved_evidence = (
                cls._resolve_evidence_ids(
                    evidence_ids,
                    evidence_lookup,
                )
            )

            if resolved_evidence:
                observed_evidence = resolved_evidence

        #
        # Build the standard reporting object.
        #
        result: dict[str, Any] = {}

        if framework is not None:
            result["framework"] = cls._serialise_value(
                framework
            )

        if control_id is not None:
            result["control_id"] = cls._serialise_value(
                control_id
            )

        if title is not None:
            result["title"] = cls._serialise_value(
                title
            )

        if status is not None:
            result["status"] = cls._serialise_value(
                status
            )

        if score is not None:
            result["score"] = cls._serialise_value(
                score
            )

        if evidence_count is not None:
            result["evidence_count"] = cls._serialise_value(
                evidence_count
            )

        if coverage is not None:
            result["coverage"] = cls._serialise_value(
                coverage
            )

        if reason is not None:
            result["reason"] = cls._serialise_value(
                reason
            )

        if evidence_source is not None:
            result["evidence_source"] = cls._serialise_value(
                evidence_source
            )

        if findings is not None:
            result["findings"] = cls._serialise_value(
                findings
            )

        #
        # Always provide observed_evidence as a list when the
        # assessment model supplied evidence.
        #
        if observed_evidence:
            result["observed_evidence"] = (
                observed_evidence
            )

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

            result[field_name] = cls._serialise_value(
                data[field_name]
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
        returned. Missing IDs are not converted into fabricated
        evidence.
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
                str(evidence_id)
            )

            if item is not None:
                resolved.append(
                    cls._serialise_value(
                        item
                    )
                )

        return resolved

    # ------------------------------------------------------------------
    # Object Conversion
    # ------------------------------------------------------------------

    @staticmethod
    def _object_to_dict(
        value: Any,
    ) -> dict[str, Any]:
        """
        Convert common assessment objects into dictionaries.

        Supports:

        - dictionaries
        - dataclasses
        - Pydantic-style model_dump()
        - Pydantic-style dict()
        - normal Python objects
        """

        if value is None:
            return {}

        if isinstance(
            value,
            dict,
        ):
            return dict(value)

        model_dump = getattr(
            value,
            "model_dump",
            None,
        )

        if callable(model_dump):

            try:
                dumped = model_dump()

            except Exception:
                dumped = None

            if isinstance(
                dumped,
                dict,
            ):
                return dumped

        dictionary = getattr(
            value,
            "dict",
            None,
        )

        if callable(dictionary):

            try:
                dumped = dictionary()

            except Exception:
                dumped = None

            if isinstance(
                dumped,
                dict,
            ):
                return dumped

        #
        # Dataclass support.
        #
        # Use dataclasses.fields() rather than asdict(). Pylance can
        # type is_dataclass() as accepting either a dataclass instance
        # or a dataclass class, which makes asdict(value) report a
        # narrowing error. fields() plus getattr() avoids that issue
        # while preserving nested dataclass values for serialization.
        #
        try:
            from dataclasses import fields, is_dataclass

            if not isinstance(
                value,
                type,
            ) and is_dataclass(value):

                return {
                    field.name: getattr(
                        value,
                        field.name,
                    )
                    for field in fields(value)
                }

        except Exception:
            pass

        #
        # Last-resort support for normal Python objects.
        #
        try:
            dumped = vars(value)

            if isinstance(
                dumped,
                dict,
            ):
                return dict(dumped)

        except TypeError:
            pass

        return {}

    # ------------------------------------------------------------------
    # Value Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _first_value(
        data: dict[str, Any],
        names: tuple[str, ...],
    ) -> Any:
        """
        Return the first non-None value from a collection of aliases.
        """

        for name in names:

            if name not in data:
                continue

            value = data[name]

            if value is not None:
                return value

        return None

    @staticmethod
    def _object_name(
        value: Any,
    ) -> Any:
        """
        Extract a useful display name from framework/control objects.
        """

        if value is None:
            return None

        if isinstance(
            value,
            str,
        ):
            return value

        if isinstance(
            value,
            dict,
        ):

            for key in (
                "name",
                "id",
                "framework",
            ):

                if value.get(key) is not None:
                    return value[key]

            return value

        for attribute_name in (
            "name",
            "id",
        ):

            attribute = getattr(
                value,
                attribute_name,
                None,
            )

            if attribute is not None:
                return attribute

        return value

    @staticmethod
    def _enum_value(
        value: Any,
    ) -> Any:
        """
        Convert enum-like status values to their underlying value.
        """

        if value is None:
            return None

        enum_value = getattr(
            value,
            "value",
            None,
        )

        if enum_value is not None:
            return enum_value

        return value

    @classmethod
    def _normalize_observed_evidence(
        cls,
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
                cls._serialise_value(
                    item
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
                cls._serialise_value(
                    evidence
                )
            ]

        return [
            cls._serialise_value(
                evidence
            )
        ]

    @classmethod
    def _serialise_value(
        cls,
        value: Any,
    ) -> Any:
        """
        Convert evidence objects into values that can safely be passed
        to the report/export layers.

        Serialization is recursive so nested evidence structures,
        dataclasses, enums, Pydantic models, lists, dictionaries,
        and other normal Python objects can be represented safely.
        """

        if value is None:
            return None

        if isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
            ),
        ):
            return value

        if isinstance(
            value,
            datetime,
        ):
            return value.isoformat()

        if isinstance(
            value,
            dict,
        ):
            return {
                str(key): cls._serialise_value(
                    item
                )
                for key, item in value.items()
            }

        if isinstance(
            value,
            (list, tuple, set),
        ):
            return [
                cls._serialise_value(
                    item
                )
                for item in value
            ]

        #
        # Enum-like values.
        #
        enum_value = getattr(
            value,
            "value",
            None,
        )

        if enum_value is not None:
            return cls._serialise_value(
                enum_value
            )

        #
        # Pydantic-style models.
        #
        model_dump = getattr(
            value,
            "model_dump",
            None,
        )

        if callable(model_dump):

            try:
                return cls._serialise_value(
                    model_dump()
                )
            except Exception:
                pass

        #
        # Older Pydantic-style dict() models.
        #
        dictionary = getattr(
            value,
            "dict",
            None,
        )

        if callable(dictionary):

            try:
                return cls._serialise_value(
                    dictionary()
                )
            except Exception:
                pass

        #
        # Dataclass instance.
        #
        # Do not use dataclasses.asdict() here because Pylance types
        # is_dataclass() as accepting both dataclass instances and
        # dataclass classes, which causes an argument narrowing error
        # when passed to asdict().
        #
        # fields() is used instead. The explicit isinstance(value, type)
        # guard ensures that only a dataclass instance is processed.
        #
        try:
            from dataclasses import fields, is_dataclass

            if (
                not isinstance(
                    value,
                    type,
                )
                and is_dataclass(value)
            ):
                return cls._serialise_value(
                    {
                        field.name: getattr(
                            value,
                            field.name,
                        )
                        for field in fields(value)
                    }
                )

        except Exception:
            pass

        #
        # Preserve the object as text rather than losing it.
        #
        return str(value)

    # ------------------------------------------------------------------
    # Framework Helpers
    # ------------------------------------------------------------------

    @classmethod
    def _framework_identifier(
        cls,
        framework: Any,
    ) -> str:
        """
        Return a stable framework identifier for report metadata.

        Supports the normal FrameworkResult -> framework object shape
        while remaining tolerant of dictionary-based results.
        """

        data = cls._object_to_dict(
            framework
        )

        framework_object = data.get(
            "framework",
            getattr(
                framework,
                "framework",
                None,
            ),
        )

        framework_object = cls._object_name(
            framework_object
        )

        if framework_object is None:
            return "Unknown"

        if isinstance(
            framework_object,
            str,
        ):
            return framework_object

        return str(
            cls._object_name(
                framework_object
            )
        )

    # ------------------------------------------------------------------
    # Framework Summary
    # ------------------------------------------------------------------

    @classmethod
    def framework_summary(
        cls,
        assessment: AssessmentScore,
    ) -> ReportSection:
        """
        Framework assessment summary.
        """

        frameworks: list[dict[str, Any]] = []

        for framework in assessment.framework_scores:

            framework_data = cls._object_to_dict(
                framework
            )

            framework_object = framework_data.get(
                "framework",
                getattr(
                    framework,
                    "framework",
                    None,
                ),
            )

            framework_object_data = cls._object_to_dict(
                framework_object
            )

            name = cls._first_value(
                framework_object_data,
                (
                    "name",
                    "id",
                ),
            )

            version = cls._first_value(
                framework_object_data,
                (
                    "version",
                ),
            )

            score = cls._first_value(
                framework_data,
                (
                    "score",
                ),
            )

            coverage = cls._first_value(
                framework_data,
                (
                    "coverage",
                ),
            )

            item: dict[str, Any] = {}

            if name is not None:
                item["framework"] = cls._serialise_value(
                    name
                )

            elif framework_object is not None:
                item["framework"] = cls._serialise_value(
                    cls._object_name(
                        framework_object
                    )
                )

            if version is not None:
                item["version"] = cls._serialise_value(
                    version
                )

            if score is not None:
                item["score"] = cls._serialise_value(
                    score
                )

            if coverage is not None:
                item["coverage"] = cls._serialise_value(
                    coverage
                )

            if item:
                frameworks.append(
                    item
                )

        return ReportSection(
            title="Framework Summary",
            content={
                "frameworks": frameworks,
            },
        )

    # ------------------------------------------------------------------
    # Capability Summary
    # ------------------------------------------------------------------

    @classmethod
    def capability_summary(
        cls,
        assessment: AssessmentScore,
    ) -> ReportSection:
        """
        Capability maturity summary.
        """

        capabilities: list[dict[str, Any]] = []

        for capability in assessment.capability_scores:

            capability_data = cls._object_to_dict(
                capability
            )

            capability_object = capability_data.get(
                "capability",
                getattr(
                    capability,
                    "capability",
                    None,
                ),
            )

            capability_object_data = cls._object_to_dict(
                capability_object
            )

            name = cls._first_value(
                capability_object_data,
                (
                    "name",
                    "id",
                ),
            )

            score = cls._first_value(
                capability_data,
                (
                    "score",
                ),
            )

            maturity = cls._first_value(
                capability_data,
                (
                    "maturity",
                ),
            )

            item: dict[str, Any] = {}

            if name is not None:
                item["capability"] = cls._serialise_value(
                    name
                )

            elif capability_object is not None:
                item["capability"] = cls._serialise_value(
                    cls._object_name(
                        capability_object
                    )
                )

            if score is not None:
                item["score"] = cls._serialise_value(
                    score
                )

            if maturity is not None:
                item["maturity"] = cls._serialise_value(
                    maturity
                )

            if item:
                capabilities.append(
                    item
                )

        return ReportSection(
            title="Capability Summary",
            content={
                "capabilities": capabilities,
            },
        )

    # ------------------------------------------------------------------
    # Risk Summary
    # ------------------------------------------------------------------

    @classmethod
    def risk_summary(
        cls,
        assessment: AssessmentScore,
    ) -> ReportSection:
        """
        Risk overview.
        """

        risks: list[dict[str, Any]] = []

        for result in assessment.risks:

            result_data = cls._object_to_dict(
                result
            )

            risk = result_data.get(
                "risk",
                getattr(
                    result,
                    "risk",
                    None,
                ),
            )

            risk_data = cls._object_to_dict(
                risk
            )

            risk_id = cls._first_value(
                risk_data,
                (
                    "id",
                ),
            )

            title = cls._first_value(
                risk_data,
                (
                    "title",
                    "name",
                ),
            )

            score = cls._first_value(
                result_data,
                (
                    "score",
                ),
            )

            level = cls._first_value(
                result_data,
                (
                    "level",
                ),
            )

            priority = cls._first_value(
                result_data,
                (
                    "priority",
                ),
            )

            level = cls._enum_value(
                level
            )

            priority = cls._enum_value(
                priority
            )

            item: dict[str, Any] = {}

            if risk_id is not None:
                item["id"] = cls._serialise_value(
                    risk_id
                )

            if title is not None:
                item["title"] = cls._serialise_value(
                    title
                )

            if score is not None:
                item["score"] = cls._serialise_value(
                    score
                )

            if level is not None:
                item["level"] = cls._serialise_value(
                    level
                )

            if priority is not None:
                item["priority"] = cls._serialise_value(
                    priority
                )

            if item:
                risks.append(
                    item
                )

        return ReportSection(
            title="Risk Summary",
            content={
                "risks": risks,
            },
        )


# ==============================================================================
# Public API
# ==============================================================================


def generate_report(
    assessment: AssessmentScore,
    tenant: str = "default",
) -> ReportDocument:
    """
    Convenience API for report generation.
    """

    generator = ReportGenerator()

    return generator.generate(
        assessment=assessment,
        tenant=tenant,
    )

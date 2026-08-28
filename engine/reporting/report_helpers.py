# engine/reporting/report_helpers.py

"""
Reporting Helpers

Shared, framework-agnostic helper functions used by the reporting layer.

This module contains only transformation, extraction, normalization, and
serialization helpers. It does not calculate compliance, determine control
results, or invent evidence.

The helpers are intentionally tolerant of different assessment model shapes
so the reporting layer remains backward compatible with existing
AssessmentScore, FrameworkScore, ControlScore, evidence, enum, dataclass,
and Pydantic-style objects.
"""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import datetime
from typing import Any


# ==============================================================================
# Object Conversion
# ==============================================================================


def object_to_dict(
    value: Any,
) -> dict[str, Any]:
    """
    Convert common assessment objects into dictionaries.

    Supports:

    - dictionaries
    - Pydantic-style model_dump()
    - older Pydantic-style dict()
    - dataclass instances
    - normal Python objects

    No values are calculated or inferred.
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
    # fields() is used instead of asdict() so nested objects remain
    # available for the reporting serializer.
    #
    try:

        if (
            not isinstance(
                value,
                type,
            )
            and is_dataclass(value)
        ):
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
    # Last-resort support for ordinary Python objects.
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


# ==============================================================================
# Generic Value Helpers
# ==============================================================================


def first_value(
    data: dict[str, Any],
    names: tuple[str, ...],
) -> Any:
    """
    Return the first non-None value from the supplied aliases.
    """

    for name in names:

        if name not in data:
            continue

        value = data[name]

        if value is not None:
            return value

    return None


def object_name(
    value: Any,
) -> Any:
    """
    Extract a useful display name from framework, control, or other
    assessment-layer objects.
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
            "title",
        ):

            if value.get(key) is not None:
                return value[key]

        return value

    for attribute_name in (
        "name",
        "id",
        "title",
    ):

        attribute = getattr(
            value,
            attribute_name,
            None,
        )

        if attribute is not None:
            return attribute

    return value


def enum_value(
    value: Any,
) -> Any:
    """
    Convert enum-like values to their underlying value.

    Plain values are returned unchanged.
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


# ==============================================================================
# Serialization
# ==============================================================================


def serialise_value(
    value: Any,
) -> Any:
    """
    Recursively convert assessment objects into report-safe values.

    Supports:

    - None
    - strings
    - numbers
    - booleans
    - datetimes
    - dictionaries
    - lists / tuples / sets
    - enum-like values
    - Pydantic models
    - dataclasses
    - ordinary Python objects

    Objects that cannot otherwise be represented are converted to text
    rather than silently discarded.
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
            str(key): serialise_value(
                item
            )
            for key, item in value.items()
        }

    if isinstance(
        value,
        (list, tuple, set),
    ):
        return [
            serialise_value(
                item
            )
            for item in value
        ]

    #
    # Enum-like values.
    #
    enum = getattr(
        value,
        "value",
        None,
    )

    if enum is not None:
        return serialise_value(
            enum
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
            return serialise_value(
                model_dump()
            )
        except Exception:
            pass

    #
    # Older Pydantic-style models.
    #
    dictionary = getattr(
        value,
        "dict",
        None,
    )

    if callable(dictionary):

        try:
            return serialise_value(
                dictionary()
            )
        except Exception:
            pass

    #
    # Dataclass instances.
    #
    try:

        if (
            not isinstance(
                value,
                type,
            )
            and is_dataclass(value)
        ):
            return serialise_value(
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
    # Preserve unknown objects as text rather than losing them.
    #
    return str(value)


# ==============================================================================
# Collection Helpers
# ==============================================================================


def flatten_collection(
    value: Any,
) -> list[Any]:
    """
    Flatten a control/framework collection into a list.

    Handles:

    - None
    - dictionaries containing grouped collections
    - lists
    - tuples
    - sets
    - individual objects

    Dictionary keys are not treated as assessment results; only their
    values are flattened.
    """

    if value is None:
        return []

    if isinstance(
        value,
        dict,
    ):

        flattened: list[Any] = []

        for item in value.values():
            flattened.extend(
                flatten_collection(
                    item
                )
            )

        return flattened

    if isinstance(
        value,
        (list, tuple, set),
    ):
        return list(value)

    return [value]


# ==============================================================================
# Framework Helpers
# ==============================================================================


def framework_identifier(
    framework: Any,
) -> str:
    """
    Return a stable framework identifier.

    Supports framework result objects, dictionaries, enums, and plain
    framework names.
    """

    data = object_to_dict(
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

    framework_object = object_name(
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
        object_name(
            framework_object
        )
    )


def framework_name(
    framework_score: Any,
) -> str | None:
    """
    Extract the display name of a framework from a framework score/result.
    """

    data = object_to_dict(
        framework_score
    )

    framework_object = data.get(
        "framework",
        getattr(
            framework_score,
            "framework",
            None,
        ),
    )

    if framework_object is None:
        return None

    framework_object_data = object_to_dict(
        framework_object
    )

    name = first_value(
        framework_object_data,
        (
            "name",
            "id",
        ),
    )

    if name is not None:
        return str(
            serialise_value(
                name
            )
        )

    value = object_name(
        framework_object
    )

    if value is None:
        return None

    return str(
        serialise_value(
            value
        )
    )


def framework_version(
    framework_score: Any,
) -> str | None:
    """
    Extract a framework version when the assessment model provides one.
    """

    data = object_to_dict(
        framework_score
    )

    framework_object = data.get(
        "framework",
        getattr(
            framework_score,
            "framework",
            None,
        ),
    )

    framework_object_data = object_to_dict(
        framework_object
    )

    version = first_value(
        framework_object_data,
        (
            "version",
        ),
    )

    if version is None:
        version = first_value(
            data,
            (
                "version",
                "framework_version",
            ),
        )

    if version is None:
        return None

    return str(
        serialise_value(
            version
        )
    )


# ==============================================================================
# Control Assessment Helpers
# ==============================================================================


def get_control_assessments(
    assessment: Any,
) -> list[Any]:
    """
    Retrieve control assessments from an assessment object.

    Preferred attributes:

    - control_assessments
    - controls
    - control_scores

    If the top-level assessment does not expose controls, framework
    results are inspected for the same attributes.

    No controls are constructed from framework names or scores.
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

        return flatten_collection(
            value
        )

    #
    # Backward-compatible fallback through framework scores.
    #
    framework_controls: list[Any] = []

    for framework_score in getattr(
        assessment,
        "framework_scores",
        [],
    ):

        for attribute_name in candidate_attributes:

            value = getattr(
                framework_score,
                attribute_name,
                None,
            )

            if value is None:
                continue

            framework_controls.extend(
                flatten_collection(
                    value
                )
            )

            #
            # Prevent duplicate collection from multiple aliases.
            #
            break

    return framework_controls


def control_framework(
    control: Any,
) -> Any:
    """
    Extract the framework associated with a control assessment.
    """

    data = object_to_dict(
        control
    )

    framework = first_value(
        data,
        (
            "framework",
            "framework_id",
            "framework_name",
        ),
    )

    return object_name(
        framework
    )


def control_identifier(
    control: Any,
) -> Any:
    """
    Extract a control/requirement identifier.
    """

    data = object_to_dict(
        control
    )

    return first_value(
        data,
        (
            "control_id",
            "requirement_id",
            "control",
            "id",
        ),
    )


def control_title(
    control: Any,
) -> Any:
    """
    Extract a control/requirement title.
    """

    data = object_to_dict(
        control
    )

    return first_value(
        data,
        (
            "title",
            "control_title",
            "name",
            "requirement",
            "description",
        ),
    )


def control_status(
    control: Any,
) -> Any:
    """
    Extract an existing control status.

    The status is never calculated here.
    """

    data = object_to_dict(
        control
    )

    status = first_value(
        data,
        (
            "status",
            "result",
            "outcome",
        ),
    )

    return enum_value(
        status
    )


def control_confidence(
    control: Any,
) -> Any:
    """
    Extract an existing confidence value.

    The confidence value is never calculated here.
    """

    data = object_to_dict(
        control
    )

    confidence = first_value(
        data,
        (
            "confidence",
            "assessment_confidence",
        ),
    )

    return enum_value(
        confidence
    )


def control_score(
    control: Any,
) -> Any:
    """
    Extract an existing control score.
    """

    data = object_to_dict(
        control
    )

    return first_value(
        data,
        (
            "score",
            "control_score",
        ),
    )


def control_findings(
    control: Any,
) -> Any:
    """
    Extract existing control findings.
    """

    data = object_to_dict(
        control
    )

    return first_value(
        data,
        (
            "findings",
            "finding",
            "issues",
            "observations",
        ),
    )


def control_evidence(
    control: Any,
) -> Any:
    """
    Extract evidence attached to a control.

    This function only reads evidence supplied by the assessment layer.
    """

    data = object_to_dict(
        control
    )

    return first_value(
        data,
        (
            "observed_evidence",
            "evidence",
            "evidence_items",
        ),
    )


# ==============================================================================
# Evidence Helpers
# ==============================================================================


def build_evidence_lookup(
    assessment: Any,
) -> dict[str, dict[str, Any]]:
    """
    Build an evidence lookup indexed by evidence_id.

    Only evidence actually present on the assessment is included.
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
            item_data = object_to_dict(
                item
            )
        else:
            item_data = dict(item)

        if not item_data:
            continue

        evidence_id = item_data.get(
            "evidence_id"
        )

        if evidence_id is None:
            continue

        lookup[str(evidence_id)] = (
            item_data
        )

    return lookup


def normalize_observed_evidence(
    evidence: Any,
) -> list[Any]:
    """
    Normalize observed evidence into a report-friendly list.

    The underlying evidence is preserved.
    """

    if evidence is None:
        return []

    if isinstance(
        evidence,
        (list, tuple, set),
    ):
        return [
            serialise_value(
                item
            )
            for item in evidence
        ]

    if isinstance(
        evidence,
        dict,
    ):
        return [
            serialise_value(
                evidence
            )
        ]

    return [
        serialise_value(
            evidence
        )
    ]


def resolve_evidence_ids(
    evidence_ids: Any,
    evidence_lookup: dict[str, dict[str, Any]],
) -> list[Any]:
    """
    Resolve evidence IDs into original collected evidence records.

    Missing IDs are ignored rather than converted into fabricated evidence.
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
                serialise_value(
                    item
                )
            )

    return resolved


# ==============================================================================
# Status Helpers
# ==============================================================================


def normalize_status(
    status: Any,
) -> str | None:
    """
    Normalize an existing status value for report representation.

    This does not decide the status. It only normalizes its representation.
    """

    status = enum_value(
        status
    )

    if status is None:
        return None

    if isinstance(
        status,
        str,
    ):
        return status.upper().replace(
            " ",
            "_",
        )

    return str(
        status
    )


def status_bucket(
    status: Any,
) -> str | None:
    """
    Map an existing status to one of the report summary buckets.

    Supported buckets:

    - MET
    - PARTIALLY_MET
    - NOT_MET
    - NOT_APPLICABLE

    Unknown statuses return None.

    This helper does not infer a status from a score.
    """

    normalized = normalize_status(
        status
    )

    if normalized is None:
        return None

    aliases: dict[str, str] = {
        "MET": "MET",
        "PASS": "MET",
        "PASSED": "MET",
        "COMPLIANT": "MET",
        "FULLY_COMPLIANT": "MET",
        "PARTIAL": "PARTIALLY_MET",
        "PARTIALLY_MET": "PARTIALLY_MET",
        "PARTIALLY_COMPLIANT": "PARTIALLY_MET",
        "PARTIAL_COMPLIANCE": "PARTIALLY_MET",
        "NOT_MET": "NOT_MET",
        "FAIL": "NOT_MET",
        "FAILED": "NOT_MET",
        "NON_COMPLIANT": "NOT_MET",
        "NOT_APPLICABLE": "NOT_APPLICABLE",
        "N_A": "NOT_APPLICABLE",
        "NA": "NOT_APPLICABLE",
    }

    return aliases.get(
        normalized
    )


# ==============================================================================
# Safe Numeric Helpers
# ==============================================================================


def numeric_value(
    value: Any,
) -> float | None:
    """
    Convert a value to a float where possible.

    Invalid or missing values return None.
    """

    if value is None:
        return None

    if isinstance(
        value,
        bool,
    ):
        return None

    try:
        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return None


def integer_value(
    value: Any,
) -> int | None:
    """
    Convert a value to an integer where possible.

    Invalid or missing values return None.
    """

    if value is None:
        return None

    if isinstance(
        value,
        bool,
    ):
        return None

    try:
        return int(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return None


# ==============================================================================
# Assessment Attribute Helpers
# ==============================================================================


def assessment_framework_scores(
    assessment: Any,
) -> list[Any]:
    """
    Safely retrieve framework scores from an assessment.

    The reporting layer does not create framework scores when they are
    absent.
    """

    value = getattr(
        assessment,
        "framework_scores",
        None,
    )

    if value is None:
        return []

    return flatten_collection(
        value
    )


def assessment_evidence_scores(
    assessment: Any,
) -> list[Any]:
    """
    Safely retrieve evidence scores from an assessment.
    """

    value = getattr(
        assessment,
        "evidence_scores",
        None,
    )

    if value is None:
        return []

    return flatten_collection(
        value
    )


def assessment_capability_scores(
    assessment: Any,
) -> list[Any]:
    """
    Safely retrieve capability scores from an assessment.
    """

    value = getattr(
        assessment,
        "capability_scores",
        None,
    )

    if value is None:
        return []

    return flatten_collection(
        value
    )


def assessment_risks(
    assessment: Any,
) -> list[Any]:
    """
    Safely retrieve risk results from an assessment.
    """

    value = getattr(
        assessment,
        "risks",
        None,
    )

    if value is None:
        return []

    return flatten_collection(
        value
    )


# ==============================================================================
# Framework Control Filtering
# ==============================================================================


def controls_for_framework(
    controls: list[Any],
    framework: str,
) -> list[Any]:
    """
    Return controls belonging to the requested framework.

    If a control has no framework information, it is not assigned to a
    framework by this helper.

    Framework comparison is case-insensitive.
    """

    target = framework.strip().upper()

    matched: list[Any] = []

    for control in controls:

        control_framework_value = control_framework(
            control
        )

        if control_framework_value is None:
            continue

        control_framework_name = str(
            serialise_value(
                control_framework_value
            )
        ).strip().upper()

        if control_framework_name == target:
            matched.append(
                control
            )

    return matched


# ==============================================================================
# Framework Summary Counting
# ==============================================================================


def count_statuses(
    controls: list[Any],
) -> dict[str, int]:
    """
    Count existing control statuses.

    Only statuses explicitly supplied by the assessment layer are counted.

    Returns:

        {
            "met": ...,
            "partially_met": ...,
            "not_met": ...,
            "not_applicable": ...,
        }
    """

    counts = {
        "met": 0,
        "partially_met": 0,
        "not_met": 0,
        "not_applicable": 0,
    }

    for control in controls:

        bucket = status_bucket(
            control_status(
                control
            )
        )

        if bucket == "MET":
            counts["met"] += 1

        elif bucket == "PARTIALLY_MET":
            counts["partially_met"] += 1

        elif bucket == "NOT_MET":
            counts["not_met"] += 1

        elif bucket == "NOT_APPLICABLE":
            counts["not_applicable"] += 1

    return counts


# ==============================================================================
# Finding Helpers
# ==============================================================================


def finding_text(
    value: Any,
) -> str | None:
    """
    Convert an existing finding value into report text.

    Lists of findings are joined without creating new findings.
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
        (list, tuple, set),
    ):

        values = [
            str(
                serialise_value(
                    item
                )
            )
            for item in value
            if item is not None
        ]

        if not values:
            return None

        return "; ".join(
            values
        )

    return str(
        serialise_value(
            value
        )
    )

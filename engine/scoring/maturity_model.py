"""
Maturity Model

Defines maturity assessment models used by the
GRC Engineering Platform.

Supports:

- Capability maturity
- Framework maturity
- Security posture scoring
- Compliance maturity reporting

Scale:

0 - Not Implemented
1 - Initial
2 - Developing
3 - Defined
4 - Managed
5 - Optimised
"""

from __future__ import annotations


from dataclasses import dataclass, field


from typing import Any



# ==============================================================================
# Maturity Levels
# ==============================================================================


@dataclass(frozen=True, slots=True)
class MaturityLevel:
    """
    Defines a maturity stage.
    """

    level: int

    name: str

    description: str

    minimum_score: float

    maximum_score: float



# ==============================================================================
# Default Maturity Model
# ==============================================================================


DEFAULT_MATURITY_LEVELS = [

    MaturityLevel(

        level=0,

        name="Not Implemented",

        description=
            "No evidence of implementation.",

        minimum_score=0,

        maximum_score=0,

    ),


    MaturityLevel(

        level=1,

        name="Initial",

        description=
            "Processes are reactive and inconsistent.",

        minimum_score=1,

        maximum_score=20,

    ),


    MaturityLevel(

        level=2,

        name="Developing",

        description=
            "Basic processes exist but are not standardised.",

        minimum_score=21,

        maximum_score=40,

    ),


    MaturityLevel(

        level=3,

        name="Defined",

        description=
            "Processes are documented and repeatable.",

        minimum_score=41,

        maximum_score=60,

    ),


    MaturityLevel(

        level=4,

        name="Managed",

        description=
            "Processes are measured and controlled.",

        minimum_score=61,

        maximum_score=80,

    ),


    MaturityLevel(

        level=5,

        name="Optimised",

        description=
            "Processes are continuously improved.",

        minimum_score=81,

        maximum_score=100,

    ),

]



# ==============================================================================
# Scoring Bands
# ==============================================================================


@dataclass(frozen=True, slots=True)
class ScoringBand:
    """
    Score classification.
    """

    name: str

    minimum: float

    maximum: float

    rating: str



DEFAULT_SCORING_BANDS = [

    ScoringBand(

        name="Critical",

        minimum=0,

        maximum=20,

        rating="Critical",

    ),


    ScoringBand(

        name="High",

        minimum=21,

        maximum=40,

        rating="High",

    ),


    ScoringBand(

        name="Medium",

        minimum=41,

        maximum=60,

        rating="Medium",

    ),


    ScoringBand(

        name="Good",

        minimum=61,

        maximum=80,

        rating="Good",

    ),


    ScoringBand(

        name="Excellent",

        minimum=81,

        maximum=100,

        rating="Excellent",

    ),

]



# ==============================================================================
# Maturity Result Models
# ==============================================================================


@dataclass(slots=True)
class MaturityResult:
    """
    Result of maturity calculation.
    """

    score: float

    level: int

    name: str

    description: str

    metadata: dict[str, Any] = field(
        default_factory=dict
    )



# ==============================================================================
# Maturity Model Engine
# ==============================================================================


class MaturityModel:
    """
    Calculates maturity levels.
    """

    def __init__(
        self,
        levels: list[MaturityLevel] | None = None,
        bands: list[ScoringBand] | None = None,
    ) -> None:


        self.levels = (
            levels
            or DEFAULT_MATURITY_LEVELS
        )


        self.bands = (
            bands
            or DEFAULT_SCORING_BANDS
        )


    # ------------------------------------------------------------------

    def calculate(
        self,
        score: float,
    ) -> MaturityResult:
        """
        Convert score into maturity level.
        """

        score = max(
            0,
            min(
                score,
                100,
            )
        )


        selected = (
            self.levels[0]
        )


        for level in self.levels:

            if (

                score >= level.minimum_score

                and

                score <= level.maximum_score

            ):

                selected = level


        return MaturityResult(

            score=round(
                score,
                2,
            ),

            level=selected.level,

            name=selected.name,

            description=selected.description,

        )


    # ------------------------------------------------------------------

    def scoring_band(
        self,
        score: float,
    ) -> ScoringBand:
        """
        Return score classification.
        """

        score = max(
            0,
            min(
                score,
                100,
            )
        )


        for band in self.bands:

            if (

                score >= band.minimum

                and

                score <= band.maximum

            ):

                return band


        return self.bands[-1]



# ==============================================================================
# Capability Maturity
# ==============================================================================


def calculate_capability_maturity(
    capability_score: float,
) -> MaturityResult:
    """
    Calculate maturity for a capability.
    """

    model = MaturityModel()

    return model.calculate(
        capability_score
    )



# ==============================================================================
# Framework Maturity
# ==============================================================================


def calculate_framework_maturity(
    framework_score: float,
) -> MaturityResult:
    """
    Calculate maturity for a framework assessment.
    """

    model = MaturityModel()

    return model.calculate(
        framework_score
    )



# ==============================================================================
# Public API
# ==============================================================================


def get_maturity_model() -> MaturityModel:
    """
    Return default maturity model.
    """

    return MaturityModel()

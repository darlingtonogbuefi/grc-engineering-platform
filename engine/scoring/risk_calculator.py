# engine\scoring\risk_calculator.py

"""
Risk Calculator

Provides risk calculation capabilities for the
GRC Engineering Platform.

Supports:

- Risk objects
- Likelihood calculation
- Impact calculation
- Risk scoring
- Risk classification
- Risk register generation
- Treatment priority

Risk model:

Risk Score = Likelihood x Impact

Scale:

Likelihood:
1 - Rare
2 - Unlikely
3 - Possible
4 - Likely
5 - Almost Certain

Impact:
1 - Insignificant
2 - Minor
3 - Moderate
4 - Major
5 - Severe
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ==============================================================================
# Risk Enumerations
# ==============================================================================


class RiskLevel(str, Enum):
    """
    Risk severity classification.
    """

    LOW = "Low"

    MEDIUM = "Medium"

    HIGH = "High"

    CRITICAL = "Critical"


class TreatmentPriority(str, Enum):
    """
    Risk remediation priority.
    """

    LOW = "Low"

    NORMAL = "Normal"

    HIGH = "High"

    URGENT = "Urgent"


# ==============================================================================
# Risk Models
# ==============================================================================


@dataclass(slots=True)
class Risk:
    """
    Represents a security risk.
    """

    id: str

    title: str

    description: str

    likelihood: int = 1

    impact: int = 1

    owner: str | None = None

    framework: str | None = None

    capability: str | None = None

    controls: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RiskResult:
    """
    Calculated risk result.
    """

    risk: Risk

    score: int

    level: RiskLevel

    priority: TreatmentPriority

    recommendations: list[str] = field(default_factory=list)


# ==============================================================================
# Risk Calculator
# ==============================================================================


class RiskCalculator:
    """
    Calculates risk scores and classifications.
    """

    def calculate(
        self,
        risk: Risk,
    ) -> RiskResult:
        """
        Calculate risk.

        Formula:

            likelihood x impact
        """

        # ------------------------------------------------------------------
        # Validate documented 1-5 risk scales.
        # Existing Risk objects remain unchanged; the normalised values
        # are used only for this calculation.
        # ------------------------------------------------------------------

        likelihood = self._normalise_rating(risk.likelihood)

        impact = self._normalise_rating(risk.impact)

        score = likelihood * impact

        level = self.classify(score)

        priority = self.priority(level)

        recommendations = self.recommendations(level)

        return RiskResult(
            risk=risk,
            score=score,
            level=level,
            priority=priority,
            recommendations=recommendations,
        )

    # ------------------------------------------------------------------
    # Rating Normalisation
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise_rating(
        value: int,
    ) -> int:
        """
        Normalise a risk rating to the documented 1-5 scale.

        Values below 1 are treated as 1.
        Values above 5 are treated as 5.
        """

        return max(
            1,
            min(
                int(value),
                5,
            ),
        )

    # ------------------------------------------------------------------
    # Likelihood Calculation
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_likelihood(
        evidence_count: int,
        control_gap: float,
    ) -> int:
        """
        Calculate likelihood.

        Higher evidence gaps increase likelihood.
        """

        score = 1

        if evidence_count <= 0:

            score += 2

        if control_gap >= 50:

            score += 2

        elif control_gap >= 25:

            score += 1

        return min(
            score,
            5,
        )

    # ------------------------------------------------------------------
    # Impact Calculation
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_impact(
        asset_value: int,
        exposure: int,
    ) -> int:
        """
        Calculate impact.

        Both inputs are rated 1-5.
        """

        value = max(
            1,
            min(
                int(asset_value),
                5,
            ),
        )

        exposure = max(
            1,
            min(
                int(exposure),
                5,
            ),
        )

        result = round((value + exposure) / 2)

        return max(
            1,
            min(
                result,
                5,
            ),
        )

    # ------------------------------------------------------------------
    # Risk Classification
    # ------------------------------------------------------------------

    @staticmethod
    def classify(
        score: int,
    ) -> RiskLevel:
        """
        Convert numeric score into risk level.
        """

        if score >= 20:

            return RiskLevel.CRITICAL

        if score >= 12:

            return RiskLevel.HIGH

        if score >= 6:

            return RiskLevel.MEDIUM

        return RiskLevel.LOW

    # ------------------------------------------------------------------
    # Treatment Priority
    # ------------------------------------------------------------------

    @staticmethod
    def priority(
        level: RiskLevel,
    ) -> TreatmentPriority:
        """
        Determine remediation priority.
        """

        mapping = {
            RiskLevel.CRITICAL: TreatmentPriority.URGENT,
            RiskLevel.HIGH: TreatmentPriority.HIGH,
            RiskLevel.MEDIUM: TreatmentPriority.NORMAL,
            RiskLevel.LOW: TreatmentPriority.LOW,
        }

        return mapping[level]

    # ------------------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------------------

    @staticmethod
    def recommendations(
        level: RiskLevel,
    ) -> list[str]:
        """
        Generate remediation guidance.
        """

        recommendations = {
            RiskLevel.CRITICAL: [
                "Immediate remediation required.",
                "Escalate to security leadership.",
                "Implement compensating controls.",
            ],
            RiskLevel.HIGH: [
                "Prioritise remediation activity.",
                "Review affected controls.",
            ],
            RiskLevel.MEDIUM: [
                "Plan remediation activity.",
                "Monitor exposure.",
            ],
            RiskLevel.LOW: [
                "Accept or monitor risk.",
            ],
        }

        return recommendations[level]


# ==============================================================================
# Risk Register
# ==============================================================================


class RiskRegister:
    """
    Maintains calculated risks.
    """

    def __init__(self) -> None:

        self._risks: list[RiskResult] = []

    def add(
        self,
        result: RiskResult,
    ) -> None:

        self._risks.append(result)

    def all(
        self,
    ) -> list[RiskResult]:

        return sorted(
            self._risks,
            key=lambda item: item.score,
            reverse=True,
        )

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Produce risk summary.
        """

        return {
            "total": len(self._risks),
            "critical": len(
                [risk for risk in self._risks if risk.level == RiskLevel.CRITICAL]
            ),
            "high": len([risk for risk in self._risks if risk.level == RiskLevel.HIGH]),
        }


# ==============================================================================
# Public API
# ==============================================================================


def calculate_risk(
    risk: Risk,
) -> RiskResult:
    """
    Convenience risk calculation API.
    """

    calculator = RiskCalculator()

    return calculator.calculate(risk)

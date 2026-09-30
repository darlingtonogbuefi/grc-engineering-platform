# scoring

Shared module used by the GRC platform.
# Scoring Module

## Overview

The **Scoring** module is responsible for transforming normalized evidence into meaningful compliance assessments, risk ratings, and maturity evaluations.

It forms the decision-making layer of the GRC Engineering Platform by answering questions such as:

* Is this control compliant?
* What percentage of the framework has been satisfied?
* Which controls present the greatest risk?
* How mature is the organisation in a given capability?
* What should auditors and stakeholders focus on?

The module operates on normalized evidence produced by the Evidence and Mapping modules and produces structured assessment objects consumed by the Reporting and Dashboard modules.

---

# Architecture

```text
Collectors
      │
      ▼
Evidence
      │
      ▼
Normalization
      │
      ▼
Framework Mapping
      │
      ▼
ScoreControl.psm1
      │
      ▼
CalculateCompliance.psm1
      │
      ▼
RiskScore.psm1
      │
      ▼
Maturity.psm1
      │
      ▼
Reporting
```

---

# Module Components

## ScoreControl.psm1

Calculates compliance for individual controls.

### Responsibilities

* Evaluate collected evidence
* Determine control status
* Calculate control score
* Produce assessment objects

### Input

```text
Evidence Objects
```

### Output

```text
Framework
ControlId
Score
Status
EvidenceCount
PassedEvidence
FailedEvidence
AssessmentDate
```

---

## CalculateCompliance.psm1

Aggregates control results into framework and capability level compliance.

### Responsibilities

* Framework compliance
* Capability compliance
* Compliance statistics
* Executive summaries

### Example Output

```text
Framework: CAF

Compliance: 92%

Passed Controls: 182

Failed Controls: 14

Status: Compliant
```

---

## RiskScore.psm1

Converts compliance failures into prioritised security risks.

### Responsibilities

* Calculate risk score
* Determine risk rating
* Prioritise remediation
* Produce framework risk summaries

### Risk Ratings

| Score | Rating   |
| ----: | -------- |
|   0–7 | Low      |
|  8–14 | Medium   |
| 15–19 | High     |
| 20–25 | Critical |

---

## Maturity.psm1

Calculates organisational maturity from assessment results.

### Responsibilities

* Control maturity
* Capability maturity
* Framework maturity
* Organisation maturity

### Maturity Levels

|  Score | Level      |
| -----: | ---------- |
| 95–100 | Optimised  |
|  85–94 | Managed    |
|  70–84 | Defined    |
|  50–69 | Developing |
|   0–49 | Initial    |

---

# Processing Flow

```text
Raw Evidence
      │
      ▼
Mapped Controls
      │
      ▼
Individual Control Scores
      │
      ▼
Framework Compliance
      │
      ▼
Risk Assessment
      │
      ▼
Capability Maturity
      │
      ▼
Reports & Dashboards
```

---

# Evidence-Based Assessment

The scoring engine is designed to assess **evidence**, not assumptions.

Example:

```text
Control

CAF A3.2

Evidence

✔ Conditional Access enabled

✔ MFA enforced

✔ PIM configured

✖ Access Reviews missing

Assessment

Score: 75%

Status: Partial
```

The resulting assessment can then contribute to framework compliance, organisational risk, and maturity calculations.

---

# Design Principles

The scoring engine is designed to be:

* Deterministic
* Repeatable
* Evidence-driven
* Framework-agnostic
* Extensible
* Suitable for automated and manual assessments

No scores should be manually entered. Every assessment must be traceable to collected evidence.

---

# Dependencies

The Scoring module consumes data from:

* `modules/evidence`
* `modules/mapping`
* `modules/schema`

The Scoring module provides data to:

* `modules/reporting`
* `modules/dashboards`
* `modules/notifications`

---

# Future Enhancements

Planned enhancements include:

* Weighted control scoring
* Evidence confidence ratings
* Residual risk calculations
* Framework-specific scoring models
* Historical trend analysis
* Machine learning assisted risk prioritisation
* Custom organisational scoring profiles

---

# Directory Structure

```text
modules/
└── scoring/
    ├── ScoreControl.psm1
    ├── CalculateCompliance.psm1
    ├── RiskScore.psm1
    ├── Maturity.psm1
    └── README.md
```

---

# Version

**GRC Engineering Platform**

**Scoring Module**

Version **1.0.0**


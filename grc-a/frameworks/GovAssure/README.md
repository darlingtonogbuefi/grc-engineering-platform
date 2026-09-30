# GovAssure Security Assessment Framework

## Overview

This repository contains an implementation of the **UK Government GovAssure** security assessment controls represented as atomic assessment controls.

The framework is designed to support:

- Evidence-based cybersecurity assessment
- Security assurance
- Compliance evaluation
- Risk management
- Control scoring
- Assessment reporting
- Integration with governance, risk and compliance (GRC) platforms

The implementation maps GovAssure controls exclusively to the **NCSC Cyber Assessment Framework (CAF)**.

No mappings to ISO 27001, NIST CSF, CIS Controls, OWASP, Cyber Essentials or other frameworks are included.

---

# Framework Structure

```text
GovAssure/
│
├── controls.yml
├── evidence.yml
├── mappings.yml
├── metadata.yml
├── scoring.yml
└── README.md
```

---

# Files

## controls.yml

Contains the GovAssure atomic assessment controls.

Each control includes:

- Control identifier
- Security theme
- Category
- Title
- Requirement
- Assessment guidance
- Evidence expectations
- Applicability
- Priority
- Tags
- CAF mappings

Example control identifier:

```text
GA-GOV-001
```

Control naming format:

```text
GA-{DOMAIN}-{NUMBER}
```

Domains:

| Code | Domain |
|------|--------|
| GOV | Governance and Risk Management |
| AM | Asset Management |
| IAM | Identity and Access Management |
| SC | Secure Configuration |
| VULN | Vulnerability Management |
| MON | Security Monitoring |
| INC | Incident Management |
| SUP | Supplier Security |
| DATA | Data Protection |

---

## evidence.yml

Defines evidence items used to support GovAssure assessments.

Each evidence record contains:

- Evidence identifier
- Evidence description
- Evidence type
- Related controls

Evidence is linked using:

```text
related_controls
```

Example:

```text
GA-EV-001
```

Evidence should be:

- Current
- Attributable
- Relevant
- Verifiable
- Sufficient to support assessment decisions

Typical evidence includes:

- Security policies
- Risk registers
- Asset inventories
- Identity management reports
- Configuration baselines
- Vulnerability reports
- Security monitoring records
- Incident reports
- Supplier assurance documentation

---

## mappings.yml

Contains mappings between GovAssure controls and the **NCSC Cyber Assessment Framework (CAF)**.

Mapping rules:

- GovAssure controls are the source
- CAF references are the target
- Only CAF mappings are maintained

Example:

```text
GA-IAM-002
|
├── B2.c
└── B4.c
```

No mappings are provided for:

- ISO/IEC 27001
- NIST CSF
- CIS Controls
- OWASP
- Cyber Essentials

---

## scoring.yml

Defines the assessment scoring model.

Supported assessment outcomes:

| Result | Description |
|---------|-------------|
| Pass | Control implemented and evidence accepted |
| Partial | Control partially implemented |
| Fail | Control not implemented |
| Not Applicable | Control does not apply |

Scoring values:

| Outcome | Value |
|---------|------:|
| Pass | 1 |
| Partial | 0.5 |
| Fail | 0 |
| Not Applicable | Excluded |

Overall score:

```text
Overall Score =
Sum(Control Score × Control Weight) /
Sum(Applicable Control Weights) × 100
```

Priority weighting supports:

- Critical
- High
- Medium
- Low

---

## metadata.yml

Contains framework information including:

- Framework identity
- Version information
- Scope
- Governance
- Assessment model
- CAF alignment
- Validation status
- Production readiness

---

# Assessment Process

The recommended assessment workflow:

```text
Identify applicable controls
            │
            ▼
Collect supporting evidence
            │
            ▼
Assess each control
            │
            ▼
Record assessment result
            │
            ▼
Calculate compliance score
            │
            ▼
Produce assessment report
```

---

# Control Assessment Lifecycle

Each control follows:

```text
Control Requirement
        │
        ▼
Evidence Collection
        │
        ▼
Assessment Decision
        │
        ▼
Score Assignment
        │
        ▼
Reporting
```

---

# Evidence Requirements

Evidence should demonstrate:

- The control exists
- The control has been implemented
- The control operates effectively
- The control applies to the assessed environment

Examples include:

- Governance documentation
- Risk assessments
- Asset inventories
- Configuration exports
- Authentication records
- Vulnerability scans
- Security monitoring logs
- Incident response records
- Supplier assurance reports

---

# CAF Alignment

This framework aligns exclusively with the **NCSC Cyber Assessment Framework (CAF)**.

| CAF Domain | Purpose |
|------------|---------|
| A | Managing Security Risk |
| B | Protecting Against Cyber Attack |
| C | Detecting Cyber Security Events |
| D | Minimising the Impact of Cyber Security Incidents |

---

# Validation Status

Framework validation includes:

- YAML syntax validation
- Control identifier validation
- Evidence linkage verification
- CAF mapping validation
- Scoring model validation
- Metadata consistency checks

Current status:

```text
validated
```

---

# Maintenance

The framework should be reviewed:

- Annually
- Following GovAssure guidance updates
- Following CAF updates
- Following significant organisational changes
- Following major cybersecurity incidents

---

# Version History

| Version | Date | Description |
|---------|------|-------------|
| 2024 | Initial release | GovAssure atomic assessment control framework |

# NCSC Cyber Assessment Framework (CAF)

## Overview

This directory contains a machine-readable implementation of the UK National Cyber Security Centre (NCSC) Cyber Assessment Framework (CAF).

The framework has been structured to support automated assessments, evidence collection, scoring, reporting, and cross-framework mapping.

The content is organised into individual YAML files to separate framework metadata, controls, evidence requirements, mappings, and scoring logic.

---

## Directory Structure

```
frameworks/
└── CAF/
    ├── controls.yml
    ├── evidence.yml
    ├── mappings.yml
    ├── metadata.yml
    ├── scoring.yml
    └── README.md
```

---

## File Descriptions

### controls.yml

Contains the authoritative CAF control catalogue.

Each control includes:

- Control ID
- Domain
- Title
- Description
- Security principle
- References
- Cross-framework mappings

Example:

```yaml
id: B2.a
title: Identity verification, authentication and authorisation

description: >
  Only authorised users are granted access...

references:
  nist:
    - IA-2
    - IA-5

  cis:
    - "6.3 Require MFA"

  iso27001:
    - "A.5.15 Access control"
```

---

### evidence.yml

Defines the evidence expected for each CAF control.

Evidence entries include:

- Required documentation
- Technical evidence
- Operational evidence
- Interview evidence
- Recommended artefacts
- Example sources

This file is used during assessments to determine whether a control has been implemented.

---

### mappings.yml

Provides a normalised mapping between CAF controls and external frameworks.

Supported mappings include:

- NIST SP 800-53
- ISO/IEC 27001
- CIS Controls v8
- OWASP Top 10
- CAF Principles
- CAF Categories

This enables cross-framework reporting and control harmonisation.

---

### metadata.yml

Contains framework metadata including:

- Framework name
- Version
- Publisher
- Source
- Licensing
- Assessment scope
- Supported maturity model
- Control counts
- Taxonomy information

---

### scoring.yml

Defines the assessment methodology.

Includes:

- Assessment ratings
- Numerical scoring
- Compliance thresholds
- Weighting
- Reporting levels
- Overall maturity calculation

---

## CAF Structure

The framework is organised into four objectives.

### A — Managing Security Risk

- Governance
- Risk Management
- Asset Management
- Supply Chain

---

### B — Protecting Against Cyber Attack

- Policies
- Identity and Access Management
- Data Security
- System Security
- Resilience
- Training

---

### C — Detecting Cyber Security Events

- Security Monitoring

---

### D — Minimising the Impact of Incidents

- Incident Response
- Lessons Learned

---

## Assessment Workflow

Typical assessment flow:

```
metadata.yml
        │
        ▼
controls.yml
        │
        ▼
evidence.yml
        │
        ▼
scoring.yml
        │
        ▼
Assessment Report
```

Mappings can be applied throughout the assessment process to generate reports against multiple frameworks.

---

## Cross-Framework Mapping

CAF controls are mapped to common industry standards where applicable.

Supported mappings include:

- NCSC CAF Principles
- NIST SP 800-53
- ISO/IEC 27001
- CIS Controls Version 8
- OWASP Top 10

These mappings support organisations implementing multiple compliance frameworks simultaneously.

---

## Intended Use

This framework is designed for:

- Cyber security assessments
- Compliance auditing
- Gap analysis
- Governance reporting
- Evidence collection
- Maturity assessments
- Continuous assurance
- Risk management

---

## Version

Framework Version:

```
CAF 3.2
```

Repository Structure Version:

```
1.0
```

---

## Notes

- `controls.yml` should be treated as the primary source of control definitions.
- Supporting files should reference control IDs rather than duplicating control text.
- New CAF revisions should update `metadata.yml` before modifying control definitions.
- Cross-framework mappings should remain synchronised with the corresponding control entries.

---

## Future Extensions

Potential enhancements include:

- Automated evidence validation
- API export formats
- OSCAL generation
- ATT&CK technique mappings
- CAPEC mappings
- CWE mappings
- MITRE D3FEND mappings
- CIS Safeguard implementation guidance
- Assessment questionnaires
- Risk scoring integration

---

## References

- UK National Cyber Security Centre (NCSC) Cyber Assessment Framework
- NIST SP 800-53 Rev. 5
- ISO/IEC 27001
- CIS Controls Version 8
- OWASP Top 10 (2021)

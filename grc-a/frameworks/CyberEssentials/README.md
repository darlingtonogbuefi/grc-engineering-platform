# Cyber Essentials Control Framework

## Overview

This repository contains an implementation of the **Cyber Essentials 2023** technical controls represented as atomic assessment controls.

The framework is designed to support:

- Evidence-based cybersecurity assessment
- Compliance evaluation
- Control scoring
- Assessment reporting
- Integration with governance and risk platforms

The implementation maps Cyber Essentials requirements exclusively to the **NCSC Cyber Assessment Framework (CAF)**.

No mappings to NIST, CIS, ISO 27001, OWASP or other frameworks are included.


---

## Framework Structure

```
CyberEssentials/
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

Contains the Cyber Essentials assessment controls.

Each control includes:

- Control identifier
- Security theme
- Category
- Requirement statement
- Assessment guidance
- Evidence expectations
- Applicability
- Priority rating
- Tags
- CAF mappings

Example control identifier:

```
CE-FW-001
```

Control naming format:

```
CE-{DOMAIN}-{NUMBER}
```

Domains:

| Code | Domain |
|---|---|
| FW | Firewalls and Internet Gateways |
| SC | Secure Configuration |
| UA | User Access Control |
| MP | Malware Protection |
| SUM | Security Update Management |


---

## evidence.yml

Defines evidence items used to support control assessments.

Evidence records provide:

- Evidence identifier
- Evidence description
- Evidence type
- Related controls

Evidence is linked to controls using the `related_controls` field.

Example:

```
CE-EV-001
```

Evidence should be:

- Current
- Attributable
- Relevant to the assessed environment
- Sufficient to demonstrate control operation


---

## mappings.yml

Contains Cyber Essentials to NCSC CAF mappings.

Mapping rules:

- Cyber Essentials controls are the source
- NCSC CAF references are the target
- Only CAF mappings are maintained

Example:

```
CE-FW-001
|
├── B4.a
├── B4.b
└── B5.b
```

No external framework mappings are included.


---

## scoring.yml

Defines the assessment scoring model.

Supported assessment outcomes:

| Result | Description |
|---|---|
| Pass | Control implemented and evidence accepted |
| Partial | Control partially implemented |
| Fail | Control not implemented |
| Not Applicable | Control does not apply |

Scoring values:

| Outcome | Value |
|---|---|
| Pass | 1 |
| Partial | 0.5 |
| Fail | 0 |
| Not Applicable | Excluded |


Overall scoring:

```
Score =
Applicable Control Results /
Applicable Controls × 100
```

Priority weighting can be applied using:

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
- Governance information
- Validation status
- Framework ownership details


---

# Assessment Process

The recommended assessment workflow:

```
Identify applicable controls
        |
        v
Collect supporting evidence
        |
        v
Assess each control
        |
        v
Record assessment result
        |
        v
Calculate compliance score
        |
        v
Produce remediation report
```


---

# Control Assessment Lifecycle

Each control should follow:

```
Control Requirement
        |
        v
Evidence Collection
        |
        v
Assessment Decision
        |
        v
Score Assignment
        |
        v
Reporting
```


---

# Evidence Requirements

Evidence should demonstrate:

- The control exists
- The control is implemented
- The control operates effectively
- The control applies to the assessed environment


Examples of acceptable evidence:

- Configuration exports
- Security policies
- Access reviews
- System inventories
- Vulnerability reports
- Security monitoring records


---

# CAF Alignment

The framework uses the NCSC Cyber Assessment Framework domains:

| CAF Domain | Purpose |
|---|---|
| A | Managing security risk |
| B | Protecting against cyber attack |
| C | Detecting cyber security events |
| D | Minimising impact of incidents |


---

# Validation Status

Framework validation checks:

- YAML syntax validated
- Control identifiers verified
- Evidence references aligned
- CAF mappings validated
- Scoring model consistency checked


Current status:

```
validated
```


---

# Maintenance

The framework should be reviewed:

- Annually
- Following Cyber Essentials scheme updates
- Following CAF guidance changes
- Following significant changes to organisational technology environments


---

# Version History

| Version | Date | Description |
|---|---|---|
| 2023 | Initial release | Cyber Essentials control framework implementation |

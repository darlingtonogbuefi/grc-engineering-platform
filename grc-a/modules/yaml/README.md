# YAML Module

## Overview

The **YAML** module provides the configuration and framework definition loading layer for the GRC Engineering Platform.

The purpose of this module is to make the platform **configuration-driven** rather than code-driven.

Instead of modifying PowerShell modules when requirements change, administrators and GRC engineers can update YAML files that define:

* Tenants
* Collectors
* Frameworks
* Controls
* Reporting requirements
* Storage settings
* Platform behaviour

The YAML module converts these human-readable definitions into structured objects consumed by the GRC engine.

---

# Architecture

```text
YAML Configuration Files
          |
          ▼
      YAML Module
          |
          ├── ConfigLoader.psm1
          |
          ├── SchemaLoader.psm1
          |
          └── FrameworkLoader.psm1
          |
          ▼
    Validation Layer
          |
          ▼
    GRC Processing Engine
          |
          ▼
    Evidence Collection
    Scoring
    Reporting
```

---

# Module Components

## ConfigLoader.psm1

### Purpose

Loads general platform configuration files.

These files control how the GRC platform operates.

### Responsibilities

* Load YAML configuration files
* Convert YAML into PowerShell objects
* Provide tenant configuration
* Provide collector configuration
* Provide reporting configuration
* Validate configuration availability

### Supported Configuration Files

```text
config/

├── tenants.yml
├── collectors.yml
├── frameworks.yml
├── reporting.yml
└── storage.yml
```

---

## Example

`config/collectors.yml`

```yaml
entra:
  enabled: true
  authentication:
    type: certificate
  schedule: daily
  evidenceTypes:
    - users
    - groups
    - conditional-access
```

Loaded by:

```powershell
Get-CollectorConfiguration
```

Result:

```text
Collector

Enabled:
true

Authentication:
certificate

Schedule:
daily

Evidence:
users
groups
conditional-access
```

---

# SchemaLoader.psm1

## Purpose

Loads schemas used to validate YAML configuration files.

Schemas ensure configuration follows expected rules before execution.

### Responsibilities

* Load YAML schemas
* Discover available schemas
* Validate schema existence
* Provide schema metadata

---

# Schema Validation Flow

```text
Administrator creates YAML
            |
            ▼
SchemaLoader.psm1
            |
            ▼
Validation.psm1
            |
            ▼
Configuration accepted
            |
            ▼
Pipeline execution
```

---

## Example Validation

Invalid:

```yaml
collector:
  authentication:
    method: certificate
```

Problem:

```text
authentication.type missing
```

Valid:

```yaml
collector:
  authentication:
    type: certificate
```

---

# FrameworkLoader.psm1

## Purpose

Loads compliance framework definitions.

This allows the platform to support multiple compliance standards without changing the assessment engine.

Supported examples:

* Microsoft Cybersecurity Framework (CAF)
* ISO 27001
* SOC 2
* GovAssure
* Cyber Essentials

---

# Framework Structure

```text
frameworks/

├── CAF/
│
│   ├── framework.yml
│   └── controls.yml
│
├── ISO27001/
│
│   ├── framework.yml
│   └── controls.yml
│
└── SOC2/

    ├── framework.yml
    └── controls.yml
```

---

# Example Framework Definition

`framework.yml`

```yaml
name: CAF

version: 1.0

owner:
  Microsoft

description:
  Cloud security assessment framework
```

---

# Example Control Definition

`controls.yml`

```yaml
controls:

  - id: CAF-IAM-01

    title:
      Identity governance

    capability:
      identity

    evidence:

      - entra.users
      - entra.roles
      - entra.conditional-access

```

The framework loader provides these controls to:

```text
FrameworkLoader.psm1
          |
          ▼
FrameworkMapper.psm1
          |
          ▼
ControlMapper.psm1
          |
          ▼
ScoreControl.psm1
```

---

# Why YAML Is Used

The GRC platform uses YAML because it provides:

## Human Readability

Auditors and security teams can review configurations without understanding PowerShell.

---

## Version Control Friendly

Changes can be tracked through Git.

Example:

```text
Framework update

Commit:
Added ISO27001 Annex A controls

Changed:
controls.yml
```

---

## Extensibility

New frameworks can be added without code changes.

Example:

Adding:

```text
frameworks/

└── PCI-DSS/

    ├── framework.yml
    └── controls.yml
```

automatically enables future assessment support.

---

# GRC Platform Lifecycle

```text
1. Load Tenant Configuration

ConfigLoader.psm1


2. Load Framework

FrameworkLoader.psm1


3. Validate Configuration

SchemaLoader.psm1


4. Execute Collectors


5. Store Evidence


6. Score Controls


7. Generate Reports
```

---

# Relationship With Other Modules

The YAML module provides input to:

```text
authentication/
    |
    ▼
Collector modules


frameworks/
    |
    ▼
mapping/


schemas/
    |
    ▼
validation/


reporting/
    |
    ▼
report generation
```

---

# Design Principles

## Configuration Over Code

Business rules should live in YAML definitions where possible.

---

## Separation of Responsibilities

YAML defines:

```text
What should be assessed
```

PowerShell implements:

```text
How assessment is performed
```

---

## Audit Transparency

Auditors should be able to understand:

* Which framework was assessed
* Which controls were evaluated
* Which evidence was required
* Which configuration was active

---

# Directory Structure

```text
modules/

└── yaml/

    ├── ConfigLoader.psm1
    ├── SchemaLoader.psm1
    ├── FrameworkLoader.psm1
    └── README.md
```

---

# Future Enhancements

Planned improvements:

* JSON schema validation integration
* YAML versioning
* Framework package signing
* Remote framework repository support
* Framework marketplace support
* Automated control updates
* Configuration change auditing

---

# Version

**GRC Engineering Platform**

**YAML Module**

Version **1.0.0**


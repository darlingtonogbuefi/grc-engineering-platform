# Storage Module

## Overview

The **Storage** module provides the persistence layer for the GRC Engineering Platform.

Its purpose is to securely store, retrieve, track, and preserve the lifecycle of:

* Compliance evidence
* Assessment execution history
* Generated reports
* Archived audit packages

The storage layer ensures that every compliance assessment is traceable from:

```text
Collected Evidence
        |
        ▼
Assessment Run
        |
        ▼
Control Evaluation
        |
        ▼
Compliance Report
        |
        ▼
Long-Term Archive
```

The storage module does not collect or assess evidence. It provides the controlled storage foundation that allows auditors to verify:

* What evidence was collected
* When it was collected
* Which assessment produced it
* Which report was generated
* Whether evidence has been altered

---

# Architecture

```text
Collectors
    |
    ▼
Evidence
    |
    ▼
EvidenceStore.psm1
    |
    ▼
RunStore.psm1
    |
    ▼
Scoring Engine
    |
    ▼
Reporting Engine
    |
    ▼
ReportStore.psm1
    |
    ▼
ArchiveStore.psm1
```

---

# Module Components

## EvidenceStore.psm1

### Purpose

Stores and manages collected compliance evidence.

Evidence is the foundation of the GRC platform.

Examples:

* Microsoft Entra users
* Conditional Access policies
* Intune configuration
* Defender settings
* Azure resource security settings
* Audit logs

### Responsibilities

* Store raw evidence
* Store processed evidence
* Retrieve evidence
* Search evidence
* Generate evidence metadata
* Calculate evidence hashes

### Storage Example

```text
evidence/

├── raw/
│   └── entra-users.json

├── processed/
│   └── identity-controls.json

└── runs/
    └── assessment-results.json
```

---

# RunStore.psm1

## Purpose

Tracks every assessment execution.

A GRC platform must provide an audit trail showing how and when an assessment was performed.

### Responsibilities

* Create assessment runs
* Track execution status
* Store run metadata
* Retrieve previous assessments
* Maintain assessment history

### Example Run

```text
Assessment Run

Framework:
CAF

Tenant:
contoso.com

Started:
2026-07-18 09:00 UTC

Collectors:
✓ Entra
✓ Intune
✓ Defender

Controls:
312

Status:
Completed
```

---

# ReportStore.psm1

## Purpose

Stores generated compliance reports.

Reports are created by the reporting modules and persisted through the report storage layer.

### Supported Formats

* HTML
* Markdown
* JSON
* CSV
* PDF
* Word

### Responsibilities

* Store reports
* Retrieve reports
* Track report metadata
* Maintain report history
* Generate report hashes

### Example

```text
reports/

├── pdf/
│   └── CAF/
│       └── CAF-assessment.pdf

├── json/
│   └── CAF/
│       └── CAF-evidence.json

└── html/
    └── CAF/
        └── CAF-dashboard.html
```

---

# ArchiveStore.psm1

## Purpose

Provides long-term retention of compliance artefacts.

Archive storage ensures evidence remains available after an audit or assessment has completed.

### Responsibilities

* Archive evidence packages
* Preserve assessment history
* Maintain retention periods
* Support audit retrieval
* Preserve file integrity

### Example

```text
archive/

└── CAF/

    └── 20260718-assessment-package/

        ├── evidence/
        ├── reports/
        └── metadata.json
```

---

# Evidence Lifecycle

The storage lifecycle follows:

```text
1. Collection

Collector retrieves configuration
from target systems.


2. Storage

EvidenceStore saves raw output.


3. Processing

Evidence is normalized and mapped.


4. Assessment

Scoring modules evaluate controls.


5. Reporting

Reports are generated.


6. Archive

Final evidence package is preserved.
```

---

# Audit Traceability

Every stored object should support traceability.

Example:

```text
Evidence

ID:
EV-001245

Source:
Microsoft Entra ID

Collected:
2026-07-18 09:15 UTC

Assessment Run:
RUN-98765

Hash:
A93F8C21...

Framework:
CAF

Control:
IAM-03
```

This allows an auditor to prove:

> The compliance decision was based on identifiable evidence collected at a specific point in time.

---

# Storage Design Principles

The storage layer follows these principles:

## Integrity

Evidence should not change after collection.

Implemented through:

* SHA256 hashing
* Metadata tracking
* Immutable storage support

---

## Traceability

Every report must link back to:

* Evidence
* Assessment run
* Framework
* Control

---

## Separation of Data

Storage is separated by purpose:

```text
Evidence

=
technical proof


Runs

=
assessment history


Reports

=
human-readable output


Archive

=
long-term retention
```

---

## Platform Independence

The storage interface is designed so the backend can change.

Current:

```text
Local filesystem
```

Future:

```text
Azure Blob Storage

Azure Data Lake

SQL Database

SharePoint Records Centre

Immutable Storage
```

The rest of the GRC platform should not need modification.

---

# Dependencies

The Storage module is consumed by:

```text
Collectors
Evidence Processing
Pipeline Engine
Reporting Engine
Notifications
```

It provides data to:

```text
Scoring Module

Reporting Module

Dashboard Module

Audit Export
```

---

# Directory Structure

```text
modules/

└── storage/

    ├── EvidenceStore.psm1
    ├── RunStore.psm1
    ├── ReportStore.psm1
    ├── ArchiveStore.psm1
    └── README.md
```

---

# Future Enhancements

Planned improvements:

* Azure Blob Storage integration
* Immutable evidence retention
* Evidence encryption at rest
* Evidence approval workflow
* Digital signatures
* Automated audit package export
* Retention policy automation
* Multi-tenant storage isolation

---

# Version

**GRC Engineering Platform**

**Storage Module**

Version **1.0.0**


# Azure Evidence Collector

## Overview

The Azure collector retrieves Azure platform evidence for the GRC engineering platform.

It collects technical evidence from Azure services and converts it into a standard evidence format consumed by the evidence engine.

The collector does not contain compliance logic. Framework mappings such as ISO 27001, CAF, GovAssure, SOC 2, or Cyber Essentials are handled separately by the GRC engine.

---

## Responsibilities

The Azure collector is responsible for:

- Authenticating to Azure
- Retrieving Azure configuration data
- Collecting platform evidence
- Normalising Azure responses
- Producing audit-ready evidence artifacts

The Azure collector is not responsible for:

- Compliance decisions
- Control scoring
- Framework mappings
- Risk assessments
- Remediation recommendations

---

## Structure

```text
azure/
|
├── collector.py
|   Main collection workflow
|
├── auth.py
|   Azure authentication provider
|
├── client.py
|   Azure API communication layer
|
├── manifest.yml
|   Collector metadata and capabilities
|
├── profiles/
|   Evidence collection profiles
|
├── queries/
|   Azure API query definitions
|
├── normalizers/
|   Azure response transformations
|
├── fixtures/
|   Test API responses
|
└── tests/
    Collector tests

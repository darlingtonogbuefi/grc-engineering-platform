# Framework Importers

## Overview

The importer subsystem converts external compliance framework source documents
into the internal YAML format used by the GRC Engineering Platform.

Supported source formats:

- Excel (.xlsx)
- CSV (.csv)
- Future:
  - JSON
  - API integrations
  - PDF extraction


The importer design separates:

- Source reading
- Data transformation
- Framework modelling
- YAML generation
- Validation


This allows new frameworks to be added without creating new importer engines.

---

# Architecture

The importer pipeline:

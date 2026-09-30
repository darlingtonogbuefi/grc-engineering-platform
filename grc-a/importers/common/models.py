"""
Canonical Importer Data Models

These models define the platform's internal representation of a compliance
framework. Every importer (CAF, ISO 27001, SOC 2, Cyber Essentials, etc.)
should populate these models before they are written to YAML.

Source documents (Excel, CSV, API, PDF) are transformed into these models.

Framework Source
        │
        ▼
Importer
        │
        ▼
Canonical Models (this module)
        │
        ▼
YAML Writer
        │
        ▼
frameworks/<Framework>/
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Capability
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class Capability:
    """
    A reusable technical capability implemented by the platform.

    Examples:
        - Identity
        - Logging
        - Backup
        - Vulnerability Management
        - Endpoint Security
    """

    id: str
    name: str
    description: str = ""


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class Evidence:
    """
    Evidence required to demonstrate compliance.

    Evidence should describe WHAT is required rather than HOW it is collected.
    """

    id: str
    name: str
    description: str = ""

    capability: Optional[str] = None

    evidence_type: str = "manual"

    references: List[str] = field(default_factory=list)

    metadata: Dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Mapping
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class Mapping:
    """
    Cross-framework mapping.

    Stores relationships from a framework control to
    other standards or platform capabilities.
    """

    capability: Optional[str] = None

    nist: List[str] = field(default_factory=list)

    iso27001: List[str] = field(default_factory=list)

    cis: List[str] = field(default_factory=list)

    owasp: List[str] = field(default_factory=list)

    cloud_security_principles: List[str] = field(default_factory=list)

    custom: Dict[str, List[str]] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Control
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class Control:
    """
    A single control within a compliance framework.
    """

    id: str

    domain: str

    title: str

    description: str

    mappings: Mapping = field(default_factory=Mapping)

    evidence: List[Evidence] = field(default_factory=list)

    metadata: Dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Framework
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class Framework:
    """
    Canonical representation of a compliance framework.
    """

    id: str

    name: str

    version: str

    description: str = ""

    owner: str = ""

    source: str = ""

    controls: List[Control] = field(default_factory=list)

    metadata: Dict[str, str] = field(default_factory=dict)

    def add_control(self, control: Control) -> None:
        """Add a control to the framework."""
        self.controls.append(control)

    @property
    def control_count(self) -> int:
        """Return the number of controls."""
        return len(self.controls)

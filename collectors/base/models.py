#collectors\base\models.py


"""
Collector Data Models.

Shared models used by all evidence collectors.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class EvidenceRecord:
    """Single evidence item."""

    source: str
    resource_type: str
    resource_id: str

    data: Dict[str, Any]

    collected_at: datetime

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "data": self.data,
            "collected_at": self.collected_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class CollectionContext:
    """Execution context for a collection run."""

    collector: str
    run_id: str

    started_at: datetime

    profile: Optional[str] = None

    tenant: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class CollectionResult:
    """Result returned after collector execution."""

    collector: str
    run_id: str

    started_at: datetime
    completed_at: datetime

    records: int

    evidence_path: str

    status: str

    errors: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "collector": self.collector,
            "run_id": self.run_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "records": self.records,
            "evidence_path": self.evidence_path,
            "status": self.status,
            "errors": self.errors,
            "metadata": self.metadata,
        }


@dataclass
class Resource:
    """
    Normalised resource representation.

    Used before evidence mapping.
    """

    id: str

    type: str

    name: str

    source: str

    attributes: Dict[str, Any] = field(
        default_factory=dict
    )

    collected_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "source": self.source,
            "attributes": self.attributes,
            "collected_at": (
                self.collected_at.isoformat()
                if self.collected_at
                else None
            ),
        }

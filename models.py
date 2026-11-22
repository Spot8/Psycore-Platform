from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field

def utcnow():
    return datetime.now(timezone.utc)

class SecurityEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=utcnow, index=True)
    severity: str = "medium"
    source: str
    event_type: str
    description: str
    status: str = "new"
    analysis: Optional[str] = None

class Asset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hostname: str = Field(index=True)
    asset_type: str
    environment: str = "enterprise"
    criticality: str = "medium"
    owner: str = "Unassigned"
    status: str = "monitored"

class Vulnerability(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cve: str = Field(index=True)
    title: str
    severity: str
    affected_asset: str
    remediation: str
    status: str = "open"

class Incident(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    severity: str = "medium"
    status: str = "open"
    description: str
    owner: str = "Unassigned"
    created_at: datetime = Field(default_factory=utcnow)
    analyst_note: Optional[str] = None

class AuditEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=utcnow)
    actor: str
    action: str
    target: str
    detail: str

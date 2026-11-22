from typing import Optional
from sqlmodel import SQLModel

class IncidentCreate(SQLModel):
    title: str
    severity: str = "medium"
    description: str
    owner: str = "Unassigned"

class IncidentUpdate(SQLModel):
    status: Optional[str] = None
    owner: Optional[str] = None
    analyst_note: Optional[str] = None

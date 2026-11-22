from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from app.database import create_db, get_session
from app.models import SecurityEvent, Asset, Vulnerability, Incident, AuditEntry
from app.schemas import IncidentCreate, IncidentUpdate
from app.seed import seed
from app.services.analysis import analyze_event

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    from app.database import engine
    with Session(engine) as session:
        seed(session)
    yield

app = FastAPI(title="AegisFlo Defense API", version="0.1.0",
              description="Defensive cybersecurity operations starter. Demo mode only.",
              lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_credentials=False, allow_methods=["GET", "POST", "PATCH"],
                   allow_headers=["Content-Type"])

def audit(session: Session, action: str, target: str, detail: str):
    session.add(AuditEntry(actor="demo-analyst", action=action, target=target, detail=detail))
    session.commit()

@app.get("/health")
def health():
    return {"status": "ok", "service": "aegisflo-api", "mode": "development-demo"}

@app.get("/api/dashboard")
def dashboard(session: Session = Depends(get_session)):
    events = session.exec(select(SecurityEvent)).all()
    incidents = session.exec(select(Incident)).all()
    assets = session.exec(select(Asset)).all()
    vulns = session.exec(select(Vulnerability)).all()
    return {
        "events_total": len(events),
        "events_open": sum(e.status != "closed" for e in events),
        "critical_events": sum(e.severity == "critical" for e in events),
        "assets_monitored": len(assets),
        "vulnerabilities_open": sum(v.status == "open" for v in vulns),
        "incidents_open": sum(i.status != "closed" for i in incidents),
        "recent_events": [e.model_dump() for e in sorted(events, key=lambda x: x.timestamp, reverse=True)[:5]]
    }

@app.get("/api/events")
def list_events(session: Session = Depends(get_session)):
    return session.exec(select(SecurityEvent).order_by(SecurityEvent.timestamp.desc())).all()

@app.post("/api/events/{event_id}/analyze")
def analyze(event_id: int, session: Session = Depends(get_session)):
    event = session.get(SecurityEvent, event_id)
    if not event:
        raise HTTPException(404, "Event not found")
    result = analyze_event(event)
    event.analysis = result["recommendation"]
    event.status = "triaged"
    session.add(event)
    session.commit()
    audit(session, "analyze_event", f"event:{event_id}", f"Priority {result['priority']} score {result['score']}")
    return result

@app.get("/api/assets")
def list_assets(session: Session = Depends(get_session)):
    return session.exec(select(Asset)).all()

@app.get("/api/vulnerabilities")
def list_vulnerabilities(session: Session = Depends(get_session)):
    return session.exec(select(Vulnerability)).all()

@app.get("/api/incidents")
def list_incidents(session: Session = Depends(get_session)):
    return session.exec(select(Incident).order_by(Incident.created_at.desc())).all()

@app.post("/api/incidents")
def create_incident(payload: IncidentCreate, session: Session = Depends(get_session)):
    item = Incident(**payload.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    audit(session, "create_incident", f"incident:{item.id}", item.title)
    return item

@app.patch("/api/incidents/{incident_id}")
def update_incident(incident_id: int, payload: IncidentUpdate, session: Session = Depends(get_session)):
    item = session.get(Incident, incident_id)
    if not item:
        raise HTTPException(404, "Incident not found")
    changes = payload.model_dump(exclude_unset=True)
    if "status" in changes and changes["status"] not in {"open", "investigating", "contained", "resolved", "closed"}:
        raise HTTPException(400, "Invalid incident status")
    for key, value in changes.items():
        setattr(item, key, value)
    session.add(item)
    session.commit()
    session.refresh(item)
    audit(session, "update_incident", f"incident:{item.id}", str(changes))
    return item

@app.get("/api/audit")
def list_audit(session: Session = Depends(get_session)):
    return session.exec(select(AuditEntry).order_by(AuditEntry.timestamp.desc())).all()

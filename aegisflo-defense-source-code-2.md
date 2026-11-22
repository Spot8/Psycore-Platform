# AegisFlo Defense — Complete Starter Source Code

Copy each file into the matching path shown below. This is a local development starter, not a government-authorized or production-secure system.

## `.env.example`

```text
POSTGRES_DB=aegisflo
POSTGRES_USER=aegisflo
POSTGRES_PASSWORD=change-this-local-password
DATABASE_URL=postgresql+psycopg://aegisflo:change-this-local-password@db:5432/aegisflo
APP_SECRET=replace-with-a-long-random-secret
VITE_API_URL=http://localhost:8000
```

## `README.md`

```markdown
# AegisFlo Defense — Cyber Operations Platform

A defensive cybersecurity operations starter for authorized enterprise environments.
Includes a FastAPI backend, React/TypeScript frontend, PostgreSQL, Docker Compose,
demo security events, asset inventory, vulnerability tracking, incident workflow,
audit events, and a deterministic AI-analysis placeholder.

## Important deployment boundary
This repository is a development starter, not a government-authorized system and not
a FedRAMP/FISMA/CMMC certification. Do not enter classified information, CUI, real
credentials, production telemetry, or sensitive government data. Before any operational
government use, complete the applicable authorization, security assessment, supply-chain
review, identity integration, logging, encryption/key-management, backup, and incident
response requirements. Use only systems and data you are authorized to administer.

## Requirements
- Docker Desktop (or Docker Engine + Compose)
- Git
- Optional: Python 3.12 and Node 20 for development outside containers

## Quick start
```bash
cp .env.example .env
# Change APP_SECRET before any shared deployment.
docker compose up --build
```
Open:
- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

The demo API is intentionally unauthenticated for local-only evaluation. It binds to
localhost through Compose. Do not expose it to a network. Before deployment, implement
the production security checklist below.

## Demo workflow
1. Open the dashboard.
2. Review seeded events and assets.
3. Create an incident from an event.
4. Change incident status and add an analyst note.
5. Review audit entries.

## Repository structure
```text
backend/
  app/
    main.py
    database.py
    models.py
    schemas.py
    seed.py
    services/analysis.py
  requirements.txt
frontend/
  src/
    App.tsx
    main.tsx
    styles.css
  package.json
  vite.config.ts
docker-compose.yml
.env.example
```

## API
- `GET /health`
- `GET /api/dashboard`
- `GET /api/events`
- `POST /api/events/{event_id}/analyze`
- `GET /api/assets`
- `GET /api/vulnerabilities`
- `GET /api/incidents`
- `POST /api/incidents`
- `PATCH /api/incidents/{incident_id}`
- `GET /api/audit`

## Local development without Docker
Backend:
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
DATABASE_URL=sqlite:///./aegisflo.db uvicorn app.main:app --reload
```
Frontend:
```bash
cd frontend
npm install
npm run dev
```
For local non-Docker development, the frontend expects the API at `http://localhost:8000`.

## Production hardening gate — required before any shared or government deployment
1. Replace demo mode with enterprise OIDC/SAML SSO and phishing-resistant MFA.
2. Enforce server-side RBAC/ABAC on every endpoint; default deny.
3. Put the API behind an approved reverse proxy/WAF; TLS 1.2+ (prefer TLS 1.3).
4. Use managed PostgreSQL with encryption at rest, private networking, backups, and tested restore.
5. Store secrets in an approved secrets manager; rotate keys and credentials.
6. Add immutable centralized audit logging, time synchronization, retention, and alerting.
7. Add tenant isolation, data classification labels, and CUI handling controls where applicable.
8. Add dependency/container scanning, SBOM generation, signed builds, and CI security gates.
9. Conduct threat modeling, penetration testing, code review, and independent assessment.
10. Map controls to the agency/contract's actual requirements and obtain the required authorization
    (for example, applicable FedRAMP authorization for cloud services and system-level ATO).
11. Validate the exact CMMC/NIST contract obligations with the contracting organization.
12. Disable demo seed data, sample credentials, public API docs, and development CORS settings.

## AI integration
The current analyzer is deterministic and local: it produces explainable triage suggestions from
event fields and does not send telemetry to an external service. If adding a hosted model later,
obtain authorization for the data flow, redact sensitive data, define retention, validate outputs,
and require human approval for actions. AI recommendations never execute containment actions.

## Scope
This starter is for defensive monitoring, triage, documentation, and compliance workflows.
It does not scan arbitrary public targets, exploit vulnerabilities, deploy payloads, or disrupt
communications.
```

## `backend/Dockerfile`

```text
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## `backend/app/__init__.py`

```python

```

## `backend/app/database.py`

```python
import os
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aegisflo.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

def create_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

## `backend/app/main.py`

```python
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
```

## `backend/app/models.py`

```python
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
```

## `backend/app/schemas.py`

```python
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
```

## `backend/app/seed.py`

```python
from sqlmodel import Session, select
from app.models import SecurityEvent, Asset, Vulnerability, Incident, AuditEntry

def seed(session: Session):
    if session.exec(select(SecurityEvent)).first():
        return
    events = [
        SecurityEvent(severity="high", source="Identity Gateway", event_type="Repeated failed login",
          description="Multiple failed authentication attempts against a privileged account."),
        SecurityEvent(severity="critical", source="Endpoint Sensor", event_type="Malware detection",
          description="Endpoint protection reported a ransomware-like behavior pattern in a test fixture."),
        SecurityEvent(severity="medium", source="Network Monitor", event_type="Unusual outbound traffic",
          description="A monitored workstation generated traffic outside its normal baseline."),
        SecurityEvent(severity="low", source="Configuration Monitor", event_type="Policy drift",
          description="A workstation configuration differs from the approved baseline.")
    ]
    assets = [
        Asset(hostname="HQ-AD-01", asset_type="Identity server", criticality="critical", owner="IT Operations"),
        Asset(hostname="FIN-WS-014", asset_type="Workstation", criticality="high", owner="Finance IT"),
        Asset(hostname="APP-SRV-03", asset_type="Application server", criticality="high", owner="Platform Team"),
        Asset(hostname="LAB-VM-22", asset_type="Virtual machine", criticality="low", owner="Engineering")
    ]
    vulns = [
        Vulnerability(cve="CVE-2024-DEMO1", title="Example: outdated web component", severity="high",
          affected_asset="APP-SRV-03", remediation="Upgrade to the vendor-fixed supported release."),
        Vulnerability(cve="CVE-2024-DEMO2", title="Example: missing security update", severity="medium",
          affected_asset="FIN-WS-014", remediation="Apply the approved operating-system security update.")
    ]
    session.add_all(events + assets + vulns)
    session.add(Incident(title="Privileged account authentication review", severity="high",
      description="Investigate repeated authentication failures in the identity gateway.", owner="SOC Tier 1"))
    session.add(AuditEntry(actor="system", action="demo_seed", target="database",
      detail="Loaded synthetic demonstration records."))
    session.commit()
```

## `backend/app/services/__init__.py`

```python

```

## `backend/app/services/analysis.py`

```python
from app.models import SecurityEvent

SEVERITY_SCORE = {"critical": 90, "high": 70, "medium": 40, "low": 15, "info": 5}

def analyze_event(event: SecurityEvent) -> dict:
    """Deterministic local triage. Not a substitute for analyst judgment."""
    score = SEVERITY_SCORE.get(event.severity.lower(), 25)
    text = f"{event.event_type} {event.description}".lower()
    indicators = []
    if "failed login" in text or "authentication" in text:
        indicators.append("Review authentication logs and verify whether activity is expected.")
        score += 10
    if "malware" in text or "ransomware" in text:
        indicators.append("Preserve endpoint evidence and follow the approved malware response playbook.")
        score += 20
    if "privilege" in text or "admin" in text:
        indicators.append("Validate privileged-account use and review recent access changes.")
        score += 15
    if not indicators:
        indicators.append("Correlate with adjacent events and validate against known-good activity.")
    priority = "critical" if score >= 90 else "high" if score >= 70 else "medium" if score >= 40 else "low"
    return {
        "priority": priority,
        "score": min(score, 100),
        "recommendation": " ".join(indicators) + " Human analyst review is required; no action was executed."
    }
```

## `backend/requirements.txt`

```text
fastapi==0.115.12
uvicorn[standard]==0.34.2
sqlmodel==0.0.24
psycopg[binary]==3.2.9
```

## `docker-compose.yml`

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-aegisflo}
      POSTGRES_USER: ${POSTGRES_USER:-aegisflo}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-local-only-change-me}
    volumes:
      - aegisflo_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-aegisflo} -d ${POSTGRES_DB:-aegisflo}"]
      interval: 5s
      timeout: 5s
      retries: 10
    networks: [internal]
  api:
    build: ./backend
    environment:
      DATABASE_URL: ${DATABASE_URL:-postgresql+psycopg://aegisflo:local-only-change-me@db:5432/aegisflo}
      APP_SECRET: ${APP_SECRET:-local-development-only}
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "127.0.0.1:8000:8000"
    networks: [internal]
  web:
    build: ./frontend
    environment:
      VITE_API_URL: ${VITE_API_URL:-http://localhost:8000}
    depends_on: [api]
    ports:
      - "127.0.0.1:5173:5173"
    networks: [internal]
volumes:
  aegisflo_data:
networks:
  internal:
    driver: bridge
```

## `frontend/Dockerfile`

```text
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

## `frontend/index.html`

```html
<!doctype html>
<html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/><title>AegisFlo Defense</title></head><body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body></html>
```

## `frontend/package.json`

```json
{
  "name": "aegisflo-defense",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite --host 0.0.0.0",
    "build": "tsc -b && vite build"
  },
  "dependencies": {
    "@vitejs/plugin-react": "latest",
    "vite": "latest",
    "typescript": "latest",
    "react": "latest",
    "react-dom": "latest",
    "lucide-react": "latest"
  },
  "devDependencies": {
    "@types/react": "latest",
    "@types/react-dom": "latest"
  }
}
```

## `frontend/src/App.tsx`

```tsx
import { useEffect, useState } from 'react'
import { Shield, LayoutDashboard, RadioTower, Server, Bug, Siren, ClipboardCheck, Settings, Search, Bell, RefreshCw, ArrowUpRight, Activity, CheckCircle2, AlertTriangle, Menu } from 'lucide-react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
type Row = Record<string, any>
type Tab = 'Overview'|'Events'|'Assets'|'Vulnerabilities'|'Incidents'|'Audit'
const nav: {name:Tab, icon:any}[] = [
  {name:'Overview',icon:LayoutDashboard},{name:'Events',icon:RadioTower},{name:'Assets',icon:Server},
  {name:'Vulnerabilities',icon:Bug},{name:'Incidents',icon:Siren},{name:'Audit',icon:ClipboardCheck}
]
async function get(path:string){const r=await fetch(API+path); if(!r.ok) throw new Error(await r.text()); return r.json()}
async function send(path:string, method:string, body?:any){const r=await fetch(API+path,{method,headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});if(!r.ok)throw new Error(await r.text());return r.json()}
function Pill({value}:{value:string}){return <span className={'pill '+value.toLowerCase()}>{value}</span>}
export default function App(){
  const [tab,setTab]=useState<Tab>('Overview'),[data,setData]=useState<Row>({}),[rows,setRows]=useState<Row[]>([]),[busy,setBusy]=useState(false),[notice,setNotice]=useState('')
  async function refresh(){setBusy(true);try{if(tab==='Overview')setData(await get('/api/dashboard'));else setRows(await get('/api/'+tab.toLowerCase()))}catch(e:any){setNotice('API connection error: '+e.message)}finally{setBusy(false)}}
  useEffect(()=>{refresh()},[tab])
  async function analyze(id:number){try{const r=await send(`/api/events/${id}/analyze`,'POST');setNotice(`Analysis complete: ${r.priority.toUpperCase()} priority · score ${r.score}/100. ${r.recommendation}`);refresh()}catch(e:any){setNotice(e.message)}}
  async function createIncident(event:Row){try{await send('/api/incidents','POST',{title:`Investigation: ${event.event_type}`,severity:event.severity,description:event.description,owner:'SOC analyst'});setNotice('Incident created.');setTab('Incidents')}catch(e:any){setNotice(e.message)}}
  async function updateIncident(id:number,status:string){try{await send(`/api/incidents/${id}`,'PATCH',{status});setNotice('Incident updated.');refresh()}catch(e:any){setNotice(e.message)}}
  const stats=[['Open events',data.events_open,'Activity'],['Critical events',data.critical_events,'AlertTriangle'],['Monitored assets',data.assets_monitored,'Server'],['Open vulnerabilities',data.vulnerabilities_open,'Bug'],['Open incidents',data.incidents_open,'Siren']]
  return <div className="shell">
    <aside className="sidebar">
      <div className="brand"><div className="brandmark"><Shield size={24}/></div><div><b>AEGISFLO</b><small>DEFENSE SYSTEMS</small></div></div>
      <div className="workspace"><span className="dot"/> DEMO ENVIRONMENT</div>
      <div className="navlabel">OPERATIONS</div>
       {nav.map(n=>{const Icon=n.icon;return <button key={n.name} className={'navitem '+(tab===n.name?'active':'')} onClick={()=>setTab(n.name)}><Icon size={17}/>{n.name}{n.name==='Events'&&data.events_open>0&&<em>{data.events_open}</em>}</button>})}
      <div className="sidebottom"><div className="secure"><Shield size={17}/><div><b>Defensive operations</b><small>Authorized assets only</small></div></div><small className="version">AEGISFLO PLATFORM · v0.1.0</small></div>
    </aside>
    <main className="main">
      <header><div className="crumb"><span>AEGISFLO</span><b>/</b>{tab}</div><div className="headright"><span className="live"><i/> SYSTEM ONLINE</span><button className="iconbtn" onClick={refresh} title="Refresh"><RefreshCw size={17}/></button><button className="iconbtn"><Bell size={17}/></button><div className="avatar">DA</div></div></header>
      <section className="content">
        <div className="pagehead"><div><div className="eyebrow">CYBER OPERATIONS CENTER</div><h1>{tab==='Overview'?'Security overview':tab}</h1><p>Defensive security monitoring and response workspace.</p></div><button className="refresh" onClick={refresh}><RefreshCw size={15}/> Refresh data</button></div>
        {notice&&<div className="notice"><span>{notice}</span><button onClick={()=>setNotice('')}>×</button></div>}
        {busy&&<div className="loading">Refreshing operational data…</div>}
        {tab==='Overview'&&<><div className="statgrid">{stats.map(([label,value,ic]:any)=>{const Icon=ic==='Activity'?Activity:ic==='AlertTriangle'?AlertTriangle:ic==='Server'?Server:ic==='Bug'?Bug:Siren;return <div className="stat" key={label}><div className="stathead">{label}<Icon size={17}/></div><strong>{value??'—'}</strong><small>Current demo environment</small></div>})}</div>
          <div className="panel"><div className="panelhead"><div><h2>Recent security events</h2><p>Latest detections across monitored demo assets</p></div><button className="textbtn" onClick={()=>setTab('Events')}>View all <ArrowUpRight size={14}/></button></div><EventTable rows={data.recent_events||[]} analyze={analyze} create={createIncident}/></div>
          <div className="bottomgrid"><div className="panel"><h2>Operational posture</h2><div className="posture"><div className="postureicon"><Shield size={25}/></div><div><b>Defensive monitoring active</b><p>Sample records are loaded. Connect approved telemetry sources during implementation.</p></div></div></div><div className="panel"><h2>Platform boundary</h2><p className="muted">This starter is a local demo. It is not authorized for CUI, classified information, or production government workloads.</p></div></div>
        </>}
        {tab==='Events'&&<div className="panel"><div className="panelhead"><div><h2>Security event queue</h2><p>Analyze and escalate events for human review</p></div></div><EventTable rows={rows} analyze={analyze} create={createIncident}/></div>}
        {tab==='Assets'&&<DataTable rows={rows} cols={['hostname','asset_type','criticality','owner','status']}/>}
        {tab==='Vulnerabilities'&&<DataTable rows={rows} cols={['cve','title','severity','affected_asset','status','remediation']}/>}
        {tab==='Incidents'&&<div className="panel"><h2>Incident response queue</h2><p className="muted">Update workflow status after following your approved response procedures.</p><div className="tablewrap"><table><thead><tr><th>ID</th><th>Incident</th><th>Severity</th><th>Owner</th><th>Status</th><th>Workflow</th></tr></thead><tbody>{rows.map(r=><tr key={r.id}><td>#{r.id}</td><td><b>{r.title}</b><small>{r.description}</small></td><td><Pill value={r.severity}/></td><td>{r.owner}</td><td><Pill value={r.status}/></td><td><select value={r.status} onChange={e=>updateIncident(r.id,e.target.value)}><option>open</option><option>investigating</option><option>contained</option><option>resolved</option><option>closed</option></select></td></tr>)}</tbody></table></div></div>}
        {tab==='Audit'&&<DataTable rows={rows} cols={['timestamp','actor','action','target','detail']}/>}
        <footer><span>AEGISFLO DEFENSE SYSTEMS</span><span>DEVELOPMENT DEMO · SYNTHETIC DATA ONLY</span></footer>
      </section>
    </main>
  </div>
}
function EventTable({rows,analyze,create}: {rows:Row[],analyze:(id:number)=>void,create:(r:Row)=>void}){
 return <div className="tablewrap"><table><thead><tr><th>Event</th><th>Source</th><th>Severity</th><th>Status</th><th>Actions</th></tr></thead><tbody>{rows.map(r=><tr key={r.id}><td><b>{r.event_type}</b><small>{r.description}</small></td><td>{r.source}</td><td><Pill value={r.severity}/></td><td><Pill value={r.status}/></td><td><div className="actions"><button onClick={()=>analyze(r.id)}>Analyze</button><button onClick={()=>create(r)}>Create incident</button></div></td></tr>)}</tbody></table>{!rows.length&&<div className="empty">No events available.</div>}</div>
}
function DataTable({rows,cols}:{rows:Row[],cols:string[]}){return <div className="panel tablewrap"><table><thead><tr>{cols.map(c=><th key={c}>{c.replaceAll('_',' ')}</th>)}</tr></thead><tbody>{rows.map((r,i)=><tr key={r.id||i}>{cols.map(c=><td key={c}>{c==='severity'||c==='status'||c==='criticality'?<Pill value={String(r[c]??'—')}/>:String(r[c]??'—')}</td>)}</tr>)}</tbody></table>{!rows.length&&<div className="empty">No records available.</div>}</div>}
```

## `frontend/src/main.tsx`

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles.css'
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>)
```

## `frontend/src/styles.css`

```css
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{font-family:'DM Sans',sans-serif;color:#e8edf3;background:#08111d;font-synthesis:none}*{box-sizing:border-box}body{margin:0}.shell{min-height:100vh;display:flex;background:#08111d}.sidebar{width:248px;background:#0b1725;border-right:1px solid #1b2b3c;padding:25px 15px;display:flex;flex-direction:column;flex-shrink:0}.brand{display:flex;align-items:center;gap:11px;padding:0 9px 28px}.brandmark{width:40px;height:40px;border-radius:11px;background:#b7f36b;color:#102019;display:grid;place-items:center}.brand b{font:700 17px 'Space Grotesk';letter-spacing:1.5px;display:block}.brand small{font-size:9px;color:#8193a7;letter-spacing:2px}.workspace{margin:0 5px 29px;padding:10px;background:#122437;border:1px solid #1e354b;border-radius:7px;color:#a9bdce;font-size:9px;letter-spacing:1px}.dot,.live i{display:inline-block;width:7px;height:7px;border-radius:50%;background:#9fe85e;margin-right:7px}.navlabel,.eyebrow{font-size:10px;letter-spacing:1.7px;color:#6f849a;font-weight:700;padding:0 10px 11px}.navitem{display:flex;align-items:center;gap:12px;width:100%;border:0;background:none;color:#91a2b4;padding:12px 11px;border-radius:7px;text-align:left;font:500 13px 'DM Sans';cursor:pointer;margin:2px 0}.navitem:hover,.navitem.active{background:#172c40;color:#c3f77a}.navitem.active{box-shadow:inset 2px 0 #b7f36b}.navitem em{font-style:normal;margin-left:auto;font-size:10px;background:#33485b;padding:2px 6px;border-radius:10px}.sidebottom{margin-top:auto}.secure{display:flex;gap:10px;align-items:center;padding:13px 8px;border-top:1px solid #203044;color:#b8ed7a}.secure b,.secure small{display:block}.secure b{font-size:11px;color:#d7e2ec}.secure small{font-size:10px;color:#8294a6;margin-top:3px}.version{display:block;color:#5f7184;font-size:8px;letter-spacing:1px;padding:18px 8px 0}.main{flex:1;min-width:0}header{height:69px;border-bottom:1px solid #1b2b3c;display:flex;align-items:center;justify-content:space-between;padding:0 34px;background:#0b1725}.crumb{font-size:12px;color:#e3eaf1}.crumb span{color:#8295a8;letter-spacing:1px;font-size:10px}.crumb b{color:#42576b;margin:0 12px}.headright{display:flex;align-items:center;gap:17px}.live{font-size:9px;letter-spacing:1px;color:#a7c28e}.iconbtn{background:none;border:0;color:#8fa2b4;cursor:pointer}.avatar{width:30px;height:30px;border-radius:50%;background:#20364a;display:grid;place-items:center;font-size:10px;color:#c7f28e}.content{max-width:1500px;margin:auto;padding:34px}.pagehead{display:flex;align-items:end;justify-content:space-between;margin-bottom:26px}.eyebrow{padding:0 0 8px;color:#9fce6d}.pagehead h1{font:600 29px 'Space Grotesk';margin:0 0 5px}.pagehead p,.panelhead p{color:#8294a6;font-size:12px;margin:0}.refresh{display:flex;gap:8px;align-items:center;background:#14283b;border:1px solid #2b4257;color:#c5d2de;padding:9px 13px;border-radius:6px;font-size:11px;cursor:pointer}.statgrid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:13px;margin-bottom:19px}.stat,.panel{background:#0e1c2b;border:1px solid #1e3042;border-radius:9px}.stat{padding:17px}.stathead{display:flex;justify-content:space-between;align-items:center;color:#94a7b9;font-size:11px}.stathead svg{color:#a9db70}.stat strong{display:block;font:600 29px 'Space Grotesk';margin:17px 0 3px}.stat small{color:#61778b;font-size:10px}.panel{padding:20px;margin-bottom:17px}.panel h2{font:600 15px 'Space Grotesk';margin:0 0 7px}.panelhead{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px}.textbtn{display:flex;align-items:center;gap:5px;background:none;border:0;color:#b8ec7a;font-size:11px;cursor:pointer}.tablewrap{overflow-x:auto}table{width:100%;border-collapse:collapse;text-align:left;min-width:650px}th{font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#70869a;font-weight:600;padding:11px 12px;border-bottom:1px solid #24384a}td{font-size:11px;color:#b6c3cf;padding:13px 12px;border-bottom:1px solid #1b2c3d;vertical-align:middle}td b,td small{display:block}td b{font-size:11px;color:#e0e8ef;margin-bottom:4px}td small{font-size:10px;color:#74899d;max-width:400px;line-height:1.5}.pill{font-size:9px;text-transform:uppercase;letter-spacing:.5px;border-radius:4px;padding:4px 7px;background:#1d3447;color:#b7c7d5;white-space:nowrap}.pill.critical,.pill.high{background:#48272a;color:#ff9b94}.pill.medium,.pill.investigating{background:#443a23;color:#f2ca72}.pill.low,.pill.new,.pill.open{background:#1c3540;color:#8fd5c0}.pill.closed,.pill.resolved,.pill.contained,.pill.triaged{background:#243c2b;color:#b9ed91}.actions{display:flex;gap:6px}.actions button{background:#172d40;border:1px solid #2b465d;color:#b9e985;border-radius:5px;padding:6px 8px;font-size:9px;cursor:pointer;white-space:nowrap}.bottomgrid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.posture{display:flex;align-items:center;gap:13px;margin-top:17px}.postureicon{width:43px;height:43px;border-radius:8px;background:#1d382a;color:#b8ec7a;display:grid;place-items:center}.posture b{font-size:12px}.posture p,.muted{font-size:11px;color:#8295a7;line-height:1.6}.notice{padding:12px 15px;background:#172e25;border:1px solid #3b6040;border-radius:7px;color:#c6e7b1;font-size:11px;margin-bottom:16px;display:flex;justify-content:space-between;gap:10px}.notice button{background:none;border:0;color:inherit;cursor:pointer}.loading,.empty{padding:22px;color:#8194a7;font-size:11px}select{background:#14283b;color:#dbe5ee;border:1px solid #30465a;border-radius:5px;padding:6px;font-size:10px}footer{display:flex;justify-content:space-between;padding:20px 2px;color:#53677b;font-size:8px;letter-spacing:1.2px}@media(max-width:1000px){.statgrid{grid-template-columns:repeat(3,1fr)}}@media(max-width:720px){.sidebar{width:64px;padding:18px 7px}.brand{padding:0 5px 24px}.brand>div:last-child,.workspace,.navlabel,.navitem:not(.active),.navitem em,.secure,.version{display:none}.navitem{justify-content:center;font-size:0;padding:13px 0}.navitem svg{width:19px;height:19px}.content{padding:22px 14px}header{padding:0 15px}.statgrid{grid-template-columns:repeat(2,1fr)}.bottomgrid{grid-template-columns:1fr}.pagehead h1{font-size:23px}.refresh{font-size:0}.refresh svg{width:17px;height:17px}}
```

## `frontend/tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": [
      "ES2020",
      "DOM",
      "DOM.Iterable"
    ],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "types": [
      "vite/client"
    ]
  },
  "include": [
    "src"
  ]
}
```

## `frontend/vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({ plugins: [react()] })
```


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

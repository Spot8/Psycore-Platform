from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Alert, Asset, Incident, Vulnerability

SEVERITIES = ("critical", "high", "medium", "low")
OPEN_VULN = ("open", "in_progress")
ACTIVE_INCIDENT = ("new", "investigating", "contained")


def _count_by(db: Session, col, *where) -> dict[str, int]:
    rows = db.execute(select(col, func.count()).where(*where).group_by(col)).all()
    return {k: v for k, v in rows}


def _fill(d: dict[str, int]) -> dict[str, int]:
    return {s: d.get(s, 0) for s in SEVERITIES}


def posture_score(vulns: dict[str, int], alerts: dict[str, int], incidents: dict[str, int]) -> int:
    """Placeholder heuristic for the prototype: start at 100 and subtract weighted open findings.
    Replace with an organization-approved risk model before operational use."""
    penalty = (
        vulns["critical"] * 4 + vulns["high"] * 2 + vulns["medium"] * 0.5
        + alerts["critical"] * 3 + alerts["high"] * 1.5
        + incidents["critical"] * 5 + incidents["high"] * 2.5
    )
    return max(0, min(100, round(100 - penalty)))


def rating(score: int) -> str:
    if score >= 85:
        return "Strong"
    if score >= 70:
        return "Stable"
    if score >= 50:
        return "Elevated risk"
    return "Critical risk"


def build_summary(db: Session, org_id: int) -> dict:
    vulns = _fill(_count_by(db, Vulnerability.severity, Vulnerability.org_id == org_id, Vulnerability.status.in_(OPEN_VULN)))
    alerts = _fill(_count_by(db, Alert.severity, Alert.org_id == org_id, Alert.status != "closed"))
    incidents = _fill(_count_by(db, Incident.severity, Incident.org_id == org_id, Incident.status.in_(ACTIVE_INCIDENT)))
    incident_status = _count_by(db, Incident.status, Incident.org_id == org_id)
    asset_risk = _fill(_count_by(db, Asset.risk_level, Asset.org_id == org_id))
    asset_total = db.scalar(select(func.count()).select_from(Asset).where(Asset.org_id == org_id)) or 0

    top_vulns = db.scalars(
        select(Vulnerability)
        .where(Vulnerability.org_id == org_id, Vulnerability.status.in_(OPEN_VULN))
        .order_by(Vulnerability.cvss_score.desc()).limit(5)
    ).all()
    recent_alerts = db.scalars(
        select(Alert).where(Alert.org_id == org_id, Alert.status != "closed").order_by(Alert.created_at.desc()).limit(6)
    ).all()
    recent_incidents = db.scalars(
        select(Incident).where(Incident.org_id == org_id).order_by(Incident.created_at.desc()).limit(6)
    ).all()

    timeline = [
        {"kind": "alert", "title": a.rule, "severity": a.severity, "at": a.created_at.isoformat()} for a in recent_alerts
    ] + [
        {"kind": "incident", "title": i.title, "severity": i.severity, "at": i.created_at.isoformat()} for i in recent_incidents
    ]
    timeline.sort(key=lambda e: e["at"], reverse=True)

    score = posture_score(vulns, alerts, incidents)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "posture": {"score": score, "rating": rating(score)},
        "assets": {"total": asset_total, "by_risk": asset_risk},
        "vulnerabilities": {
            "open_by_severity": vulns,
            "top": [
                {"id": v.id, "cve_id": v.cve_id, "title": v.title, "cvss_score": v.cvss_score, "severity": v.severity,
                 "affected_software": v.affected_software, "status": v.status}
                for v in top_vulns
            ],
        },
        "alerts": {
            "open_by_severity": alerts,
            "recent": [
                {"id": a.id, "rule": a.rule, "severity": a.severity, "source": a.source,
                 "asset_hostname": a.asset_hostname, "status": a.status, "created_at": a.created_at.isoformat()}
                for a in recent_alerts
            ],
        },
        "incidents": {"active_by_severity": incidents, "by_status": incident_status},
        "timeline": timeline[:10],
    }

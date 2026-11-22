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

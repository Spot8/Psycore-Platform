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

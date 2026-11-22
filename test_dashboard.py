from app.services.dashboard import posture_score, rating


def test_summary_shape_and_values(client, login):
    body = client.get("/api/v1/dashboard/summary", headers=login("viewer@demo.example")).json()
    assert body["assets"]["total"] == 12
    assert body["vulnerabilities"]["open_by_severity"]["critical"] == 2
    assert 0 <= body["posture"]["score"] <= 100
    assert len(body["alerts"]["recent"]) == 6
    assert body["vulnerabilities"]["top"][0]["cvss_score"] == 9.8
    assert body["timeline"] == sorted(body["timeline"], key=lambda e: e["at"], reverse=True)


def test_remediated_vulnerabilities_are_excluded(client, login):
    body = client.get("/api/v1/dashboard/summary", headers=login("viewer@demo.example")).json()
    assert "CVE-2099-0010" not in [v["cve_id"] for v in body["vulnerabilities"]["top"]]


def test_posture_score_bounds():
    zero = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    assert posture_score(zero, zero, zero) == 100
    assert posture_score({**zero, "critical": 50}, zero, zero) == 0
    assert rating(90) == "Strong" and rating(40) == "Critical risk"

import pytest

from app.core.config import Settings


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_unauthenticated_requests_rejected(client):
    assert client.get("/api/v1/dashboard/summary").status_code == 401
    assert client.get("/api/v1/auth/me").status_code == 401


def test_invalid_token_rejected(client):
    r = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-token"})
    assert r.status_code == 401


def test_unknown_user_login_fails_and_is_audited(client, db_session):
    from sqlalchemy import select

    from app.models import AuditLog

    assert client.post("/api/v1/auth/mock-login", json={"email": "nobody@demo.example"}).status_code == 401
    assert db_session.scalar(select(AuditLog).where(AuditLog.action == "auth.login_failed")) is not None


def test_me_returns_role_and_permissions(client, login):
    body = client.get("/api/v1/auth/me", headers=login("analyst@demo.example")).json()
    assert body["role"] == "analyst"
    assert "dashboard:read" in body["permissions"] and "users:read" not in body["permissions"]


@pytest.mark.parametrize("email,status", [
    ("admin@demo.example", 200), ("compliance@demo.example", 403), ("analyst@demo.example", 403), ("viewer@demo.example", 403)])
def test_user_listing_is_admin_only(client, login, email, status):
    assert client.get("/api/v1/admin/users", headers=login(email)).status_code == status


@pytest.mark.parametrize("email,status", [
    ("admin@demo.example", 200), ("compliance@demo.example", 200), ("analyst@demo.example", 403), ("viewer@demo.example", 403)])
def test_audit_log_access(client, login, email, status):
    assert client.get("/api/v1/admin/audit-logs", headers=login(email)).status_code == status


def test_denied_access_is_audited(client, login):
    client.get("/api/v1/admin/users", headers=login("viewer@demo.example"))
    logs = client.get("/api/v1/admin/audit-logs", headers=login("admin@demo.example")).json()
    assert any(entry["action"] == "access.denied" for entry in logs)


def test_production_refuses_mock_auth():
    with pytest.raises(RuntimeError):
        Settings(environment="production", auth_mode="mock", secret_key="x" * 40).validate_runtime()


def test_production_refuses_default_secret():
    with pytest.raises(RuntimeError):
        Settings(environment="production", auth_mode="oidc", oidc_issuer="i", oidc_audience="a", oidc_jwks_url="u").validate_runtime()


def test_oidc_requires_settings():
    with pytest.raises(RuntimeError):
        Settings(auth_mode="oidc").validate_runtime()

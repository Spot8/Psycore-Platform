"""initial schema

Revision ID: 0001
Revises:
"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

TS = lambda: sa.Column("created_at", sa.DateTime(timezone=True), nullable=False)  # noqa: E731


def _org() -> sa.Column:
    return sa.Column("org_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=False, index=True)


def upgrade() -> None:
    op.create_table("organizations", sa.Column("id", sa.Integer, primary_key=True),
                    sa.Column("name", sa.String(200), nullable=False, unique=True), TS())
    op.create_table("users", sa.Column("id", sa.Integer, primary_key=True), _org(),
                    sa.Column("email", sa.String(320), nullable=False, unique=True, index=True),
                    sa.Column("full_name", sa.String(200), nullable=False), sa.Column("role", sa.String(32), nullable=False),
                    sa.Column("is_active", sa.Boolean, nullable=False), TS())
    op.create_table("audit_logs", sa.Column("id", sa.Integer, primary_key=True),
                    sa.Column("org_id", sa.Integer, sa.ForeignKey("organizations.id"), index=True),
                    sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
                    sa.Column("action", sa.String(100), nullable=False, index=True),
                    sa.Column("resource", sa.String(200), nullable=False), sa.Column("detail", sa.Text, nullable=False),
                    sa.Column("ip_address", sa.String(64), nullable=False), TS())
    op.create_table("assets", sa.Column("id", sa.Integer, primary_key=True), _org(),
                    sa.Column("hostname", sa.String(200), nullable=False), sa.Column("asset_type", sa.String(32), nullable=False),
                    sa.Column("os_name", sa.String(100), nullable=False), sa.Column("os_version", sa.String(100), nullable=False),
                    sa.Column("risk_score", sa.Float, nullable=False),
                    sa.Column("risk_level", sa.String(16), nullable=False, index=True),
                    sa.Column("last_seen", sa.DateTime(timezone=True), nullable=False))
    op.create_table("vulnerabilities", sa.Column("id", sa.Integer, primary_key=True), _org(),
                    sa.Column("cve_id", sa.String(32), nullable=False, index=True),
                    sa.Column("title", sa.String(300), nullable=False), sa.Column("description", sa.Text, nullable=False),
                    sa.Column("cvss_score", sa.Float, nullable=False),
                    sa.Column("severity", sa.String(16), nullable=False, index=True),
                    sa.Column("affected_software", sa.String(300), nullable=False),
                    sa.Column("status", sa.String(24), nullable=False, index=True), TS())
    op.create_table("alerts", sa.Column("id", sa.Integer, primary_key=True), _org(),
                    sa.Column("source", sa.String(64), nullable=False), sa.Column("rule", sa.String(300), nullable=False),
                    sa.Column("severity", sa.String(16), nullable=False, index=True),
                    sa.Column("status", sa.String(24), nullable=False, index=True),
                    sa.Column("asset_hostname", sa.String(200), nullable=False), TS())
    op.create_table("incidents", sa.Column("id", sa.Integer, primary_key=True), _org(),
                    sa.Column("title", sa.String(300), nullable=False),
                    sa.Column("severity", sa.String(16), nullable=False, index=True),
                    sa.Column("status", sa.String(24), nullable=False, index=True),
                    sa.Column("assignee_id", sa.Integer, sa.ForeignKey("users.id")), TS(),
                    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))


def downgrade() -> None:
    for t in ("incidents", "alerts", "vulnerabilities", "assets", "audit_logs", "users", "organizations"):
        op.drop_table(t)

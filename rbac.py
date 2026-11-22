ROLES = ("admin", "analyst", "compliance_officer", "viewer")

# Permission names are "<resource>:<action>". New modules add entries here.
PERMISSIONS: dict[str, set[str]] = {
    "admin": {"dashboard:read", "users:read", "users:write", "audit:read"},
    "analyst": {"dashboard:read"},
    "compliance_officer": {"dashboard:read", "audit:read"},
    "viewer": {"dashboard:read"},
}


def role_has(role: str, permission: str) -> bool:
    return permission in PERMISSIONS.get(role, set())

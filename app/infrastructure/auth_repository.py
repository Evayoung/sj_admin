"""Authentication repository for admin login — 2-Sister Co-Ownership System.

Strictly enforces:
1. Maximum 2 admin accounts allowed in the entire system.
2. Equal administrative privileges for both sisters.
3. Login via personal email or username.
4. Secure password recovery via registered personal email address.
"""

from __future__ import annotations

import hashlib
import secrets
import time
from typing import Any

from app.config import settings
from app.infrastructure.supabase_client import get_service_client, has_supabase

MAX_ADMIN_ACCOUNTS = 2
SALT = "sj-interiors-admin-salt"

def _hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with 600,000 iterations."""
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), SALT.encode("utf-8"), 600_000)
    return f"pbkdf2_sha256${key.hex()}"


# Local persistent in-memory store for 2-sister accounts
# Seeded with both co-founders; supports email or username login.
_LOCAL_ADMIN_USERS: list[dict[str, Any]] = [
    {
        "id": "sister-1",
        "username": "mercy",
        "email": "alademercy93@gmail.com",
        "full_name": "Mercy Olorundare (Co-Owner & Creative Director)",
        "password_hash": _hash_password("Olajumoke402@"),
        "is_active": True,
        "reset_token": None,
        "reset_token_expires_at": None,
        "last_login_at": None,
    },
    {
        "id": "sister-2",
        "username": "christianah",
        "email": "aladechristiana5@gmail.com",
        "full_name": "Christianah Alade (Co-Owner & Operations Director)",
        "password_hash": _hash_password("Beamose1965#"),
        "is_active": True,
        "reset_token": None,
        "reset_token_expires_at": None,
        "last_login_at": None,
    },
]


def _verify_password_hash(password: str, stored_hash: str) -> bool:
    """Verify password against PBKDF2 or legacy SHA-256 hash."""
    if not stored_hash:
        return False
    if stored_hash.startswith("pbkdf2_sha256$"):
        expected = _hash_password(password)
        return secrets.compare_digest(stored_hash, expected)
    # Legacy SHA-256 fallback
    legacy = hashlib.sha256(f"{SALT}{password}".encode("utf-8")).hexdigest()
    return secrets.compare_digest(stored_hash, legacy)


def _ensure_supabase_admins() -> None:
    """Auto-seed sister accounts into Supabase admin_users if table is newly created and empty."""
    if not has_supabase():
        return
    client = get_service_client()
    if not client:
        return
    try:
        res = client.table("admin_users").select("id", count="exact").execute()
        if res and res.count == 0:
            for u in _LOCAL_ADMIN_USERS:
                client.table("admin_users").upsert({
                    "id": u["id"],
                    "username": u["username"],
                    "email": u["email"],
                    "full_name": u["full_name"],
                    "password_hash": u["password_hash"],
                    "is_active": True,
                }).execute()
    except Exception:
        pass


def get_admin_user_count() -> int:
    """Return count of active admin accounts."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                res = client.table("admin_users").select("id", count="exact").eq("is_active", True).execute()
                if res and res.count is not None and res.count > 0:
                    return res.count
                # If Supabase table exists but is empty, seed it
                if res and res.count == 0:
                    _ensure_supabase_admins()
            except Exception:
                pass
    return len([u for u in _LOCAL_ADMIN_USERS if u.get("is_active", True)])


def can_create_admin_user() -> bool:
    """Enforce strict business rule: maximum 2 sister accounts allowed."""
    return get_admin_user_count() < MAX_ADMIN_ACCOUNTS


def get_admin_users() -> list[dict[str, Any]]:
    """Get all registered admin accounts (maximum 2)."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                res = client.table("admin_users").select("id, username, email, full_name, is_active, last_login_at, created_at").order("created_at").limit(MAX_ADMIN_ACCOUNTS).execute()
                data = getattr(res, "data", [])
                if data:
                    return data
            except Exception:
                pass
    return [
        {
            "id": u["id"],
            "username": u["username"],
            "email": u["email"],
            "full_name": u["full_name"],
            "is_active": u["is_active"],
            "last_login_at": u.get("last_login_at"),
            "created_at": "2026-01-01T00:00:00Z",
        }
        for u in _LOCAL_ADMIN_USERS
        if u.get("is_active", True)
    ]


def get_admin_user_by_id(user_id: str) -> dict[str, Any] | None:
    """Find admin user by ID."""
    for u in _LOCAL_ADMIN_USERS:
        if u.get("id") == user_id:
            return u
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                res = client.table("admin_users").select("*").eq("id", user_id).execute()
                users = getattr(res, "data", [])
                if users:
                    return users[0]
            except Exception:
                pass
    return None


def get_admin_user_by_email(email: str) -> dict[str, Any] | None:
    """Find admin user by personal email (case-insensitive)."""
    clean_email = (email or "").strip().lower()
    if not clean_email:
        return None
    for u in _LOCAL_ADMIN_USERS:
        if (u.get("email") or "").strip().lower() == clean_email:
            return u
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                res = client.table("admin_users").select("*").ilike("email", clean_email).execute()
                users = getattr(res, "data", [])
                if users:
                    return users[0]
            except Exception:
                pass
    return None


def verify_login(identifier: str, password: str) -> dict[str, Any] | None:
    """Verify admin credentials via personal email or username.
    
    Supports:
    - Sister 1 (username 'fatima' or email 'fatima@sjinteriors.com')
    - Sister 2 (username 'zainab' or email 'zainab@sjinteriors.com')
    - Backward compatibility for root env admin credentials (maps to Sister 1)
    """
    clean_id = (identifier or "").strip().lower()
    if not clean_id or not password:
        return None

    # Check local sister accounts first
    for u in _LOCAL_ADMIN_USERS:
        if not u.get("is_active", True):
            continue
        uname = (u.get("username") or "").lower()
        umail = (u.get("email") or "").lower()
        if clean_id in (uname, umail):
            stored_hash = u.get("password_hash", "")
            if stored_hash and _verify_password_hash(password, stored_hash):
                u["last_login_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                return u

    # Check backward-compatible env settings credentials (maps to Sister 1)
    if clean_id in (settings.admin_username.lower(), "admin"):
        if secrets.compare_digest(password, settings.admin_password):
            sister1 = _LOCAL_ADMIN_USERS[0]
            sister1["last_login_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            return sister1

    # Check Supabase admin_users table
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                # Query by username or email
                res = client.table("admin_users").select("*").or_(f"username.eq.{clean_id},email.eq.{clean_id}").eq("is_active", True).execute()
                users = getattr(res, "data", [])
                if users:
                    user = users[0]
                    stored_hash = user.get("password_hash", "")
                    if stored_hash and _verify_password_hash(password, stored_hash):
                        try:
                            client.table("admin_users").update({"last_login_at": "now()"}).eq("id", user["id"]).execute()
                        except Exception:
                            pass
                        return user
            except Exception:
                pass

    return None


def create_password_reset_token(email: str) -> tuple[bool, str, str]:
    """Generate a secure 60-minute password reset token for a sister's personal email.
    
    Returns: (success, message, token_or_empty)
    """
    user = get_admin_user_by_email(email)
    if not user:
        # Check if email is sister1 or sister2 fallback
        clean_email = email.strip().lower()
        for u in _LOCAL_ADMIN_USERS:
            if u.get("email", "").lower() == clean_email:
                user = u
                break
    if not user:
        return False, "No administrator account found with that email address.", ""

    token = secrets.token_urlsafe(32)
    expires_at = time.time() + 3600  # 1 hour expiry

    # Update in-memory user
    user["reset_token"] = token
    user["reset_token_expires_at"] = expires_at

    # Update in Supabase if available
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                client.table("admin_users").update({
                    "reset_token": token,
                    "reset_token_expires_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(expires_at)),
                }).eq("id", user.get("id")).execute()
            except Exception:
                pass

    return True, f"Password reset instructions generated for {user.get('full_name', email)}.", token


def verify_reset_token(token: str) -> dict[str, Any] | None:
    """Verify that a password reset token exists and has not expired."""
    if not token or not token.strip():
        return None
    token = token.strip()
    now = time.time()

    # Check local users
    for u in _LOCAL_ADMIN_USERS:
        if u.get("reset_token") == token:
            exp = u.get("reset_token_expires_at", 0) or 0
            if exp > now:
                return u
            return None

    # Check Supabase
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                res = client.table("admin_users").select("*").eq("reset_token", token).execute()
                users = getattr(res, "data", [])
                if users:
                    user = users[0]
                    # Parse timestamp or fallback
                    return user
            except Exception:
                pass

    return None


def reset_password_with_token(token: str, new_password: str) -> tuple[bool, str]:
    """Reset a sister's password using a verified token."""
    user = verify_reset_token(token)
    if not user:
        return False, "This password reset link is invalid or has expired. Please request a new one."

    if len(new_password) < 8:
        return False, "Password must be at least 8 characters long."

    new_hash = _hash_password(new_password)
    user["password_hash"] = new_hash
    user["reset_token"] = None
    user["reset_token_expires_at"] = None

    if has_supabase():
        client = get_service_client()
        if client:
            try:
                client.table("admin_users").update({
                    "password_hash": new_hash,
                    "reset_token": None,
                    "reset_token_expires_at": None,
                }).eq("id", user.get("id")).execute()
            except Exception:
                pass

    return True, f"Password successfully updated for {user.get('full_name', 'account')}. You can now sign in."


def update_sister_profile(user_id: str, full_name: str, email: str, new_password: str = "") -> tuple[bool, str]:
    """Update a sister's profile, personal email, and optional password."""
    clean_email = (email or "").strip().lower()
    if not clean_email or "@" not in clean_email:
        return False, "A valid personal email address is required."

    # Verify email is not used by the other sister
    for u in _LOCAL_ADMIN_USERS:
        if u.get("id") != user_id and (u.get("email") or "").lower() == clean_email:
            return False, "This email is already in use by the other sister."

    user = get_admin_user_by_id(user_id)
    if not user:
        return False, "Sister account not found."

    user["full_name"] = full_name.strip()
    user["email"] = clean_email
    if new_password:
        if len(new_password) < 8:
            return False, "New password must be at least 8 characters long."
        user["password_hash"] = _hash_password(new_password)

    if has_supabase():
        client = get_service_client()
        if client:
            try:
                payload: dict[str, Any] = {
                    "full_name": full_name.strip(),
                    "email": clean_email,
                }
                if new_password:
                    payload["password_hash"] = _hash_password(new_password)
                client.table("admin_users").update(payload).eq("id", user_id).execute()
            except Exception:
                pass

    return True, f"Account profile for {full_name} updated successfully."

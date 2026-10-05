"""Authentication routes — login, logout, and 2-sister password recovery."""

from __future__ import annotations

import time
from typing import Any
from urllib.parse import unquote

from starlette.responses import RedirectResponse

from app.infrastructure.audit_repository import log_activity
from app.infrastructure.auth_repository import (
    create_password_reset_token,
    reset_password_with_token,
    verify_login,
    verify_reset_token,
)
from app.infrastructure.email_service import send_password_reset_email
from app.presentation.pages.auth import (
    forgot_password_page as render_forgot_password,
    login_page as render_login,
    reset_password_page as render_reset_password,
)


SESSION_TTL = 8 * 3600  # 8 hours


def register_auth_routes(app: Any) -> None:
    """Register /login, /logout, /forgot-password, and /reset-password routes."""

    def _safe_next_path(path: str | None) -> str:
        if not path:
            return "/"
        clean = unquote(path).strip()
        if not clean.startswith("/") or clean.startswith("//") or "\\" in clean:
            return "/"
        return clean

    @app.get("/login")
    def login_page(req, session, next_path: str = "/"):
        if session.get("admin_authenticated"):
            return RedirectResponse(url="/", status_code=303)
        return render_login(next_path=_safe_next_path(next_path))

    @app.post("/login")
    def login_submit(req, session, username: str, password: str, next_path: str = "/"):
        safe_path = _safe_next_path(next_path)
        user = verify_login(username, password)
        if not user:
            log_activity(
                req,
                session=None,
                action="LOGIN_FAILED",
                target_type="auth",
                target_id=username,
                details=f"Failed login attempt for identifier '{username}'",
                actor_override={"name": "Unknown Visitor", "email": username, "id": "unknown"},
            )
            return render_login(error="Invalid email, username, or password.", next_path=safe_path)

        # Record rich sister session data
        session["admin_authenticated"] = True
        session["admin_user"] = user.get("username", username)
        session["admin_user_id"] = user.get("id", "sister-1")
        session["admin_user_name"] = user.get("full_name") or user.get("username", username)
        session["admin_email"] = user.get("email", "admin@sjinteriors.com")
        session["expires_at"] = time.time() + SESSION_TTL

        # Log successful login in audit trail
        log_activity(
            req,
            session,
            action="LOGIN_SUCCESS",
            target_type="auth",
            target_id=str(user.get("id")),
            details=f"Successful login as {session['admin_user_name']} ({session['admin_email']})",
        )

        return RedirectResponse(url=safe_path, status_code=303)

    @app.get("/logout")
    def logout(req, session):
        actor_name = session.get("admin_user_name") or session.get("admin_user") or "Admin"
        log_activity(
            req,
            session,
            action="LOGOUT",
            target_type="auth",
            target_id=str(session.get("admin_user_id", "")),
            details=f"{actor_name} logged out.",
        )
        session.clear()
        return RedirectResponse(url="/login", status_code=303)

    # ── 2-Sister Password Recovery Flow ──────────────────────────────────────

    @app.get("/forgot-password")
    def forgot_password_get(req, session):
        if session.get("admin_authenticated"):
            return RedirectResponse(url="/", status_code=303)
        return render_forgot_password()

    @app.post("/forgot-password")
    def forgot_password_post(req, session, email: str = ""):
        clean_email = (email or "").strip().lower()
        if not clean_email or "@" not in clean_email:
            return render_forgot_password(error="Please provide a valid personal email address.")

        ok, msg, token = create_password_reset_token(clean_email)
        if not ok:
            log_activity(
                req,
                session=None,
                action="PASSWORD_RESET_REJECTED",
                target_type="auth",
                target_id=clean_email,
                details=f"Password recovery requested for unauthorized email '{clean_email}'",
                actor_override={"name": "Unknown Visitor", "email": clean_email, "id": "unknown"},
            )
            return render_forgot_password(error=msg)

        # Build full reset URL using public site URL or request host
        try:
            base_url = str(req.base_url).rstrip("/")
        except Exception:
            from app.config import settings as _settings
            base_url = f"http://localhost:{_settings.port}"
        reset_url = f"{base_url}/reset-password?token={token}"

        log_activity(
            req,
            session=None,
            action="PASSWORD_RESET_REQUESTED",
            target_type="auth",
            target_id=clean_email,
            details=f"Password recovery token generated for {clean_email}",
            actor_override={"name": clean_email, "email": clean_email, "id": "reset-user"},
        )

        # Attempt to send the recovery email
        from app.infrastructure.auth_repository import get_admin_user_by_email as _get_user
        user_obj = _get_user(clean_email)
        sister_name = (user_obj or {}).get("full_name", "Sister")

        email_sent, email_msg = send_password_reset_email(clean_email, sister_name, reset_url)

        if email_sent:
            success_msg = (
                f"A password reset link has been sent to <strong>{clean_email}</strong>. "
                "Check your inbox (and spam/junk folder) and click the link within 60 minutes."
            )
            return render_forgot_password(success=success_msg)
        else:
            # SMTP not configured or failed — show the link on-screen as fallback
            success_msg = (
                f"Recovery token generated. Email delivery is not yet configured ({email_msg}). "
                "Use the link below to reset your password:"
            )
            return render_forgot_password(success=success_msg, reset_link=f"/reset-password?token={token}")


    @app.get("/reset-password")
    def reset_password_get(req, session, token: str = ""):
        user = verify_reset_token(token)
        if not user:
            return render_login(error="This password reset link is invalid or has expired. Please request a new one.")
        return render_reset_password(token=token, user_name=user.get("full_name") or user.get("username", ""))

    @app.post("/reset-password")
    def reset_password_post(req, session, token: str, new_password: str, confirm_password: str):
        if new_password != confirm_password:
            return render_reset_password(token=token, error="Passwords do not match. Please re-enter both.")
        if len(new_password) < 8:
            return render_reset_password(token=token, error="Password must be at least 8 characters long.")

        user = verify_reset_token(token)
        if not user:
            return render_login(error="This password reset link has expired. Please request a new one.")

        ok, msg = reset_password_with_token(token, new_password)
        if not ok:
            return render_reset_password(token=token, error=msg)

        # Log password reset in audit trail
        log_activity(
            req,
            session=None,
            action="PASSWORD_RESET",
            target_type="auth",
            target_id=str(user.get("id")),
            details=f"Password reset successfully completed for {user.get('full_name')} ({user.get('email')})",
            actor_override={"name": user.get("full_name", "Sister"), "email": user.get("email", ""), "id": str(user.get("id"))},
        )

        return render_login(success="Password updated successfully! You can now sign in with your new password.")

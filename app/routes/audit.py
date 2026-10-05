"""Audit trail route — activity monitoring for store administrators."""

from __future__ import annotations

from typing import Any

from app.infrastructure.audit_repository import get_audit_logs
from app.presentation.pages.audit import audit_trail_page
from app.presentation.shell import page_frame


def register_audit_routes(app: Any) -> None:
    """Register /audit-trail route."""

    @app.get("/audit-trail")
    def audit_trail(req, session, actor: str = "all", action: str = "all"):
        target_type = None
        action_filter = None

        if action in {"product", "document", "order", "auth"}:
            target_type = action
        elif action != "all":
            action_filter = action

        logs = get_audit_logs(
            limit=150,
            actor=actor if actor != "all" else None,
            action=action_filter,
            target_type=target_type,
        )

        return page_frame(
            *audit_trail_page(logs, active_actor=actor, active_action=action),
            current="/audit-trail",
            title="Audit Trail",
        )

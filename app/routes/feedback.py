"""Routes for managing client feedback, reviews, and service complaints."""

from __future__ import annotations

from fasthtml.common import Request
from starlette.responses import HTMLResponse

from app.infrastructure.audit_repository import log_activity
from app.infrastructure.feedback_repository import (
    get_all_feedback,
    get_feedback_by_id,
    toggle_publish_testimonial,
    update_complaint_status,
)
from app.presentation.pages.feedback import feedback_page, feedback_row_fragment
from app.presentation.shell import page_frame


def register_feedback_routes(app):
    """Register feedback and complaints management endpoints."""

    @app.get("/feedback")
    def feedback_index(req: Request, filter: str = "all"):
        items = get_all_feedback()
        body = feedback_page(items, active_filter=filter)
        return page_frame(*body, current="/feedback", title="Feedback & Reviews")

    @app.post("/feedback/toggle-publish/{fb_id}")
    def feedback_toggle_publish(fb_id: str, req: Request = None, session: dict = None):
        sess = session or (req.session if req else {})
        updated = toggle_publish_testimonial(fb_id)
        if not updated:
            return HTMLResponse("Item not found", status_code=404)

        is_pub = updated.get("is_published", False)
        act = "PUBLISH_TESTIMONIAL" if is_pub else "UNPUBLISH_TESTIMONIAL"
        log_activity(
            req, sess, act, "feedback", fb_id,
            f"{'Published' if is_pub else 'Unpublished'} testimonial by {updated.get('customer_name')} for storefront display"
        )
        return feedback_row_fragment(updated)

    @app.post("/feedback/resolve/{fb_id}")
    async def feedback_resolve(fb_id: str, req: Request = None, session: dict = None):
        sess = session or (req.session if req else {})
        form = await req.form() if req else {}
        status = form.get("status", "investigating")
        notes = form.get("notes", "")
        assigned_to = form.get("assigned_to", "Mercy")

        updated = update_complaint_status(
            fb_id, status=status, resolution_notes=notes, assigned_to=assigned_to
        )
        if not updated:
            return HTMLResponse("Item not found", status_code=404)

        log_activity(
            req, sess, "RESOLVE_COMPLAINT", "feedback", fb_id,
            f"Updated ticket for {updated.get('customer_name')} to '{status}' (Assigned: {assigned_to}): {notes[:60]}"
        )
        return feedback_row_fragment(updated)

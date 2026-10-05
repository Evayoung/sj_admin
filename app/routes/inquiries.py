"""Inquiry management routes."""

from __future__ import annotations

from typing import Any

from fasthtml.common import Div

try:
    from ..infrastructure.inquiry_repository import get_all_inquiries, get_inquiry_by_id, update_inquiry_status
    from ..presentation.page_helpers import oob_alert, toast_fragment
    from ..presentation.shell import page_frame
    from ..presentation.pages.inquiries import inquiries_page, inquiry_detail_fragment
except ImportError:
    from app.infrastructure.inquiry_repository import get_all_inquiries, get_inquiry_by_id, update_inquiry_status
    from app.presentation.page_helpers import oob_alert, toast_fragment
    from app.presentation.shell import page_frame
    from app.presentation.pages.inquiries import inquiries_page, inquiry_detail_fragment


def register_inquiry_routes(app: Any) -> None:

    @app.get("/inquiries")
    def inquiries_list(status: str = "all"):
        inquiries = get_all_inquiries(status)
        return page_frame(*inquiries_page(inquiries, status), current="/inquiries", title="Inquiries")

    @app.get("/inquiries/detail")
    def inquiry_detail(inquiry_id: str = ""):
        """HTMX: return inquiry detail."""
        inquiry = None
        if inquiry_id:
            inquiry = get_inquiry_by_id(inquiry_id)
        return inquiry_detail_fragment(inquiry)

    @app.post("/inquiries/status")
    def inquiry_status_update(id: str = "", status: str = "", notes: str = ""):
        """HTMX: update inquiry status."""
        if not id or not status:
            return oob_alert("Missing parameters.", variant="danger", target="inquiry-detail-result"), toast_fragment("Missing parameters.", variant="danger")
        result = update_inquiry_status(id, status, notes)
        if result:
            return oob_alert(f"Inquiry status updated to {status.upper()}.", variant="success", target="inquiry-detail-result"), toast_fragment(f"Inquiry status updated to {status.upper()}.", variant="success")
        return oob_alert("Failed to update status.", variant="danger", target="inquiry-detail-result"), toast_fragment("Failed to update status.", variant="danger")

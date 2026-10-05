"""Service management routes — full CRUD."""

from __future__ import annotations

from typing import Any

from fasthtml.common import Div, HttpHeader
from starlette.responses import JSONResponse

try:
    from ..infrastructure.service_repository import (
        get_all_services, get_service_by_id, create_service, update_service, delete_service,
    )
    from ..presentation.page_helpers import oob_alert, toast_fragment
    from ..presentation.shell import page_frame
    from ..presentation.pages.services import services_page, service_editor_fragment, _services_list
except ImportError:
    from app.infrastructure.service_repository import (
        get_all_services, get_service_by_id, create_service, update_service, delete_service,
    )
    from app.presentation.page_helpers import oob_alert, toast_fragment
    from app.presentation.shell import page_frame
    from app.presentation.pages.services import services_page, service_editor_fragment, _services_list


def register_service_routes(app: Any) -> None:

    @app.get("/services")
    def services_list(new: int = 0):
        services = get_all_services()
        editor = service_editor_fragment(None) if new else None
        return page_frame(*services_page(services, selected_fragment=editor), current="/services", title="Services")

    @app.get("/services/list")
    def services_list_fragment():
        """HTMX: return updated services list fragment."""
        services = get_all_services()
        return _services_list(services)

    @app.get("/services/editor")
    def service_editor(service_id: str = ""):
        """HTMX: return service editor form."""
        service = None
        if service_id:
            service = get_service_by_id(service_id)
        return service_editor_fragment(service)

    @app.post("/services/save")
    def service_save(
        id: str = "",
        title: str = "",
        slug: str = "",
        summary: str = "",
        description: str = "",
        icon: str = "",
        image_url: str = "",
        sort_order: int = 0,
        is_active: bool = True,
    ):
        """HTMX: save service (create or update)."""
        data = {
            "title": title,
            "slug": slug or title.lower().replace(" ", "-").replace("&", "and"),
            "summary": summary,
            "description": description,
            "icon": icon,
            "image_url": image_url,
            "sort_order": int(sort_order or 0),
            "is_active": bool(is_active),
        }

        if id:
            result = update_service(id, data)
        else:
            result = create_service(data)

        if result:
            return service_editor_fragment(result), toast_fragment("Service saved successfully.", variant="success"), HttpHeader("HX-Trigger", "refreshList")

        return oob_alert("Failed to save service.", variant="danger", target="save-result"), toast_fragment("Failed to save service.", variant="danger")

    @app.post("/services/delete")
    def service_delete(id: str = ""):
        """HTMX: delete service."""
        if not id:
            return JSONResponse({"error": "Missing id"}, status_code=400)
        success = delete_service(id)
        if success:
            return service_editor_fragment(None), toast_fragment("Service deleted successfully.", variant="success"), HttpHeader("HX-Trigger", "refreshList")
        return oob_alert("Failed to delete service.", variant="danger", target="save-result"), toast_fragment("Failed to delete service.", variant="danger")

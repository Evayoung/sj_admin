"""Category management routes — full CRUD."""

from __future__ import annotations

from typing import Any

from fasthtml.common import Div, HttpHeader
from starlette.responses import JSONResponse

try:
    from ..infrastructure.category_repository import (
        get_all_categories, get_category_by_id, create_category, update_category, delete_category,
    )
    from ..presentation.page_helpers import oob_alert, toast_fragment
    from ..presentation.shell import page_frame
    from ..presentation.pages.categories import categories_page, category_editor_fragment, _categories_list
except ImportError:
    from app.infrastructure.category_repository import (
        get_all_categories, get_category_by_id, create_category, update_category, delete_category,
    )
    from app.presentation.page_helpers import oob_alert, toast_fragment
    from app.presentation.shell import page_frame
    from app.presentation.pages.categories import categories_page, category_editor_fragment, _categories_list


def register_category_routes(app: Any) -> None:

    @app.get("/categories")
    def categories_list(new: int = 0):
        categories = get_all_categories()
        editor = category_editor_fragment(None) if new else None
        return page_frame(*categories_page(categories, selected_fragment=editor), current="/categories", title="Categories")

    @app.get("/categories/list")
    def categories_list_fragment():
        """HTMX: return updated categories list fragment."""
        categories = get_all_categories()
        return _categories_list(categories)

    @app.get("/categories/editor")
    def category_editor(category_id: str = ""):
        """HTMX: return category editor form."""
        category = None
        if category_id:
            category = get_category_by_id(category_id)
        return category_editor_fragment(category)

    @app.post("/categories/save")
    def category_save(
        id: str = "",
        label: str = "",
        slug: str = "",
        description: str = "",
        icon: str = "",
        image_url: str = "",
        sort_order: int = 0,
        is_active: bool = True,
    ):
        """HTMX: save category (create or update)."""
        data = {
            "label": label,
            "slug": slug or label.lower().replace(" ", "-").replace("&", "and"),
            "description": description,
            "icon": icon,
            "image_url": image_url,
            "sort_order": int(sort_order or 0),
            "is_active": bool(is_active),
        }

        if id:
            result = update_category(id, data)
        else:
            result = create_category(data)

        if result:
            return category_editor_fragment(result), toast_fragment("Category saved successfully.", variant="success"), HttpHeader("HX-Trigger", "refreshList")

        return oob_alert("Failed to save category.", variant="danger", target="save-result"), toast_fragment("Failed to save category.", variant="danger")

    @app.post("/categories/delete")
    def category_delete(id: str = ""):
        """HTMX: delete category."""
        if not id:
            return JSONResponse({"error": "Missing id"}, status_code=400)
        success = delete_category(id)
        if success:
            empty_editor = category_editor_fragment(None)
            return empty_editor, toast_fragment("Category deleted successfully.", variant="success"), HttpHeader("HX-Trigger", "refreshList")
        return oob_alert("Failed to delete category.", variant="danger", target="save-result"), toast_fragment("Failed to delete category.", variant="danger")

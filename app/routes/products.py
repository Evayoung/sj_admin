"""Product management routes — full CRUD."""

from __future__ import annotations

from typing import Any

from fasthtml.common import Div, HttpHeader
from starlette.responses import JSONResponse

try:
    from ..infrastructure.product_repository import (
        get_all_products, get_product_by_id, create_product, update_product, delete_product,
    )
    from ..infrastructure.category_repository import get_all_categories
    from ..presentation.page_helpers import oob_alert, toast_fragment
    from ..presentation.shell import page_frame
    from ..presentation.pages.products import products_page, product_editor_fragment, _products_list
except ImportError:
    from app.infrastructure.product_repository import (
        get_all_products, get_product_by_id, create_product, update_product, delete_product,
    )
    from app.infrastructure.category_repository import get_all_categories
    from app.presentation.page_helpers import oob_alert, toast_fragment
    from app.presentation.shell import page_frame
    from app.presentation.pages.products import products_page, product_editor_fragment, _products_list


def register_product_routes(app: Any) -> None:

    @app.get("/products")
    def products_list(category: str = "all", new: int = 0):
        products = get_all_products(category)
        categories = get_all_categories()
        editor = product_editor_fragment(None, categories) if new else None
        return page_frame(*products_page(products, categories, category, selected_fragment=editor), current="/products", title="Products")

    @app.get("/products/list")
    def products_list_fragment(category: str = "all"):
        """HTMX: return updated products list fragment."""
        products = get_all_products(category)
        return _products_list(products, category)

    @app.get("/products/editor")
    def product_editor(product_id: str = ""):
        """HTMX: return product editor form."""
        product = None
        if product_id:
            product = get_product_by_id(product_id)
        categories = get_all_categories()
        return product_editor_fragment(product, categories)

    @app.post("/products/save")
    def product_save(
        req=None,
        session=None,
        id: str = "",
        name: str = "",
        slug: str = "",
        category_slug: str = "",
        price: str = "",
        description: str = "",
        highlight: str = "",
        image_url: str = "",
        images_raw: str = "",
        stock_status: str = "in_stock",
        is_featured: bool = False,
        is_active: bool = True,
    ):
        """HTMX: save product (create or update)."""
        # Parse images list
        gallery_images = []
        if images_raw:
            for item in images_raw.replace(",", "\n").splitlines():
                clean_url = item.strip()
                if clean_url:
                    gallery_images.append(clean_url)

        data = {
            "name": name,
            "slug": slug or name.lower().replace(" ", "-").replace("&", "and"),
            "category_slug": category_slug,
            "price": price,
            "description": description,
            "highlight": highlight,
            "image_url": image_url,
            "images": gallery_images,
            "stock_status": stock_status,
            "is_featured": bool(is_featured),
            "is_active": bool(is_active),
        }

        from app.infrastructure.audit_repository import log_activity

        if id:
            result = update_product(id, data)
            if result:
                log_activity(req, session, "UPDATE_PRODUCT", "product", str(id), f"Updated product '{name}' (Price: {price})")
        else:
            result = create_product(data)
            if result:
                log_activity(req, session, "CREATE_PRODUCT", "product", str(result.get("id", name)), f"Created product '{name}' (Price: {price})")

        if result:
            categories = get_all_categories()
            return product_editor_fragment(result, categories), toast_fragment("Product saved successfully.", variant="success"), HttpHeader("HX-Trigger", "refreshList")

        return oob_alert("Failed to save product.", variant="danger", target="save-result"), toast_fragment("Failed to save product.", variant="danger")

    @app.post("/products/delete")
    def product_delete(req=None, session=None, id: str = ""):
        """HTMX: delete product."""
        if not id:
            return JSONResponse({"error": "Missing id"}, status_code=400)
        from app.infrastructure.audit_repository import log_activity
        success = delete_product(id)
        if success:
            log_activity(req, session, "DELETE_PRODUCT", "product", str(id), f"Deleted product with ID '{id}'")
            categories = get_all_categories()
            return product_editor_fragment(None, categories), toast_fragment("Product deleted successfully.", variant="success"), HttpHeader("HX-Trigger", "refreshList")
        return oob_alert("Failed to delete product.", variant="danger", target="save-result"), toast_fragment("Failed to delete product.", variant="danger")

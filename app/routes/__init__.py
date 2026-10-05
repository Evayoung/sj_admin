"""Central route registration for SJ Interiors Admin."""

from __future__ import annotations

from typing import Any


def setup_routes(app: Any) -> None:
    """Register all route modules in dependency order."""
    from .auth import register_auth_routes
    from .dashboard import register_dashboard_routes
    from .categories import register_category_routes
    from .products import register_product_routes
    from .services import register_service_routes
    from .inquiries import register_inquiry_routes
    from .orders import register_order_routes
    from .documents import register_document_routes
    from .media import register_media_routes
    from .settings import register_settings_routes
    from .audit import register_audit_routes
    from .feedback import register_feedback_routes

    register_auth_routes(app)
    register_dashboard_routes(app)
    register_category_routes(app)
    register_product_routes(app)
    register_service_routes(app)
    register_inquiry_routes(app)
    register_order_routes(app)
    register_document_routes(app)
    register_media_routes(app)
    register_settings_routes(app)
    register_audit_routes(app)
    register_feedback_routes(app)

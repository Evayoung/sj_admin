"""Shared layout helpers for the SJ Interiors Admin UI."""

from __future__ import annotations

import time as _time

from fasthtml.common import A, Aside, Button, Div, Footer, H1, Li, Main, Nav, P, Small, Span, Style, Ul
from faststrap import BottomNav, BottomNavItem, Container, Drawer, Icon, SidebarNavbar, SidebarNavItem
from faststrap.components.feedback.confirm import ConfirmDialog
from faststrap.components.feedback.modern_toast import ModernToastStack, ToastPlacement

from app.config import settings


# ── Navigation Configuration ──────────────────────────────────────────────

NAV_ITEMS = (
    ("Overview", "/", "grid"),
    ("Categories", "/categories", "tags"),
    ("Products", "/products", "box-seam"),
    ("Services", "/services", "wrench"),
    ("Inquiries", "/inquiries", "inbox"),
    ("Feedback", "/feedback", "chat-square-quote"),
    ("Orders", "/orders", "cart"),
    ("Documents", "/documents", "file-earmark-text"),
    ("Media", "/media", "images"),
    ("Settings", "/settings", "sliders"),
    ("Audit Trail", "/audit-trail", "clock-history"),
)

NAV_GROUPS = (
    {
        "label": "Content",
        "items": [
            ("Categories", "/categories", "tags"),
            ("Products", "/products", "box-seam"),
            ("Services", "/services", "wrench"),
        ],
    },
    {
        "label": "Business",
        "items": [
            ("Inquiries", "/inquiries", "inbox"),
            ("Feedback", "/feedback", "chat-square-quote"),
            ("Orders", "/orders", "cart"),
            ("Documents", "/documents", "file-earmark-text"),
        ],
    },
    {
        "label": "Tools",
        "items": [
            ("Media", "/media", "images"),
            ("Settings", "/settings", "sliders"),
            ("Audit Trail", "/audit-trail", "clock-history"),
        ],
    },
)

BOTTOM_NAV_ITEMS = (
    ("Overview", "/", "grid"),
    ("Products", "/products", "box-seam"),
    ("Inquiries", "/inquiries", "inbox"),
    ("Documents", "/documents", "file-earmark-text"),
)


# ── Brand Helpers ─────────────────────────────────────────────────────────

def _brand_initials() -> tuple[str, str]:
    return ("S", "J")


def admin_logo() -> Span:
    first, second = _brand_initials()
    return Span(
        Span(first, cls="admin-logo-letter"),
        Span(second, cls="admin-logo-letter admin-logo-letter-alt"),
        cls="admin-logo",
    )


# ── Navigation Components ────────────────────────────────────────────────

def _nav_link(label: str, href: str, icon: str, current: str, *, compact: bool = False) -> A:
    base_cls = "admin-nav-link" if not compact else "admin-bottom-link"
    if href == current:
        base_cls += " active"
    return A(
        Icon(icon, cls="admin-nav-icon"),
        Span(label, cls="admin-nav-label"),
        href=href,
        cls=base_cls,
        aria_label=label,
    )


def _sidebar_group_nav(current: str, group: dict) -> Div:
    items = group["items"]
    nav = SidebarNavbar(
        *[
            SidebarNavItem(
                label, href=href, icon=icon,
                active=href == current, theme="dark",
                cls="admin-nav-link",
            )
            for label, href, icon in items
        ],
        theme="dark", sticky=False, collapsible=False, width="100%",
        cls="admin-sidebar-nav",
    )
    return Div(
        Span(group["label"], cls="admin-sidebar-kicker"),
        nav,
        cls="admin-sidebar-group",
    )


def admin_sidebar(current: str = "/") -> Aside:
    overview_item = NAV_ITEMS[0]
    overview_nav = SidebarNavbar(
        SidebarNavItem(
            overview_item[0], href=overview_item[1], icon=overview_item[2],
            active=overview_item[1] == current, theme="dark",
            cls="admin-nav-link",
        ),
        theme="dark", sticky=False, collapsible=False, width="100%",
        cls="admin-sidebar-nav",
    )
    grouped_navs = [_sidebar_group_nav(current, group) for group in NAV_GROUPS]

    return Aside(
        Div(
            A(
                admin_logo(),
                Div(
                    Span("SJ Interiors", cls="admin-brand-title"),
                    Span("Admin Dashboard", cls="admin-brand-subtitle"),
                    cls="admin-brand-text",
                ),
                href="/",
                cls="admin-brand",
            ),
            Div(overview_nav, cls="admin-sidebar-group"),
            *grouped_navs,
            Div(
                Div(
                    A(
                        Icon("box-arrow-up-right", cls="me-2"),
                        "Public Site",
                        href=settings.public_site_url,
                        target="_blank", rel="noreferrer",
                        cls="btn admin-nav-btn w-100",
                    ),
                    A(
                        Icon("box-arrow-right", cls="me-2"),
                        "Sign Out",
                        href="#",
                        data_bs_toggle="modal",
                        data_bs_target="#sign-out-confirm-modal",
                        cls="btn admin-install-btn w-100",
                    ),
                    cls="admin-sidebar-actions",
                ),
                cls="admin-sidebar-panel",
            ),
            cls="admin-sidebar-inner",
        ),
        cls="admin-sidebar d-none d-lg-flex",
    )


def admin_mobile_header(current: str = "/", title: str = "Overview") -> Div:
    active_item = next((label for label, href, _ in NAV_ITEMS if href == current), title)
    return Div(
        Container(
            Div(
                A(admin_logo(), href="/", cls="admin-mobile-brand"),
                Div(Span(active_item, cls="admin-mobile-title"), cls="admin-mobile-text"),
                cls="admin-mobile-header-row",
            ),
        ),
        cls="admin-mobile-header d-lg-none",
    )


def admin_bottom_nav(current: str = "/") -> Div:
    main_items = BOTTOM_NAV_ITEMS[:4]
    return BottomNav(
        *[
            BottomNavItem(
                label, href=href, icon=icon,
                active=href == current,
                cls="admin-bottom-link",
            )
            for label, href, icon in main_items
        ],
        A(
            Icon("list", size="1.25em", cls="mb-1"),
            Small("Menu", cls="d-block admin-bottom-small"),
            href="#",
            data_bs_toggle="offcanvas",
            data_bs_target="#adminMobileDrawer",
            aria_label="Open menu",
            cls="nav-link d-flex flex-column align-items-center justify-content-center w-100 flex-grow-1 py-2 admin-bottom-link",
        ),
        variant="light",
        cls="admin-bottom-nav d-lg-none",
        id="admin-bottom-nav",
    )


def admin_mobile_drawer(current: str = "/") -> Div:
    overview_section = Div(
        _nav_link("Overview", "/", "grid", current),
        cls="admin-sidebar-links mt-0",
    )
    group_sections = []
    for group in NAV_GROUPS:
        group_div = Div(
            P(group["label"], cls="admin-sidebar-kicker mb-2 mt-3"),
            Div(
                *[_nav_link(label, href, icon, current) for label, href, icon in group["items"]],
                cls="admin-sidebar-links mt-0",
            ),
        )
        group_sections.append(group_div)

    actions = Div(
        A(
            Icon("box-arrow-up-right", cls="me-2"),
            "Public Site",
            href=settings.public_site_url,
            target="_blank", rel="noreferrer",
            cls="btn admin-nav-btn w-100",
        ),
        A(
            Icon("box-arrow-right", cls="me-2"),
            "Sign Out",
            href="#",
            data_bs_toggle="modal",
            data_bs_target="#sign-out-confirm-modal",
            cls="btn admin-install-btn w-100",
        ),
        cls="admin-sidebar-actions mt-4",
    )
    return Drawer(
        Div(
            P("Workspace", cls="admin-sidebar-kicker mb-3"),
            overview_section,
            *group_sections,
            actions,
            cls="admin-mobile-drawer-stack",
        ),
        drawer_id="adminMobileDrawer",
        title="Menu",
        placement="start",
        cls="admin-mobile-drawer d-lg-none",
        body_cls="admin-mobile-drawer-body",
        dark=False,
    )


def _sign_out_confirm_dialog() -> Div:
    return ConfirmDialog(
        "You will be signed out of the admin dashboard.",
        confirm_text="Sign Out",
        cancel_text="Stay Signed In",
        title="Sign Out",
        variant="danger",
        dialog_id="sign-out-confirm-modal",
        hx_confirm_method="get",
        hx_confirm_url="/logout",
        data_bs_focus_trap="true",
    )


def _media_picker_modal() -> Div:
    return Div(
        Div(
            Div(
                Div(
                    Span("Select Image from Media Library", cls="modal-title h5 fw-bold"),
                    Button(type="button", cls="btn-close", data_bs_dismiss="modal", aria_label="Close"),
                    cls="modal-header border-bottom",
                ),
                Div(
                    Div(
                        "Loading media files...",
                        cls="text-center py-4 text-muted",
                        hx_get="/media/picker-modal",
                        hx_trigger="intersect once, shown.bs.modal from:#mediaPickerModal",
                        hx_target="#mediaPickerBody",
                        hx_swap="innerHTML",
                    ),
                    cls="modal-body", id="mediaPickerBody",
                ),
                cls="modal-content",
            ),
            cls="modal-dialog modal-lg modal-dialog-scrollable",
        ),
        cls="modal fade", id="mediaPickerModal", tabindex="-1", aria_hidden="true", data_bs_focus_trap="true",
    )


PAGE_SUBTITLES = {
    "/": "Store performance metrics, recent customer inquiries, and quick actions.",
    "/categories": "Organize catalog products into customer departments and navigation filters.",
    "/products": "Manage store catalog items, pricing, photography, and inventory status.",
    "/services": "Configure the 6 core interior styling divisions, specifications, and scope.",
    "/inquiries": "Review incoming customer leads and consultation requests from the public site.",
    "/feedback": "Review client testimonials for website publishing and resolve incoming service complaints.",
    "/orders": "Fulfill customer orders, track payments, and update delivery status.",
    "/documents": "Create and dispatch proposals, quotations, invoices, and payment receipts.",
    "/media": "High-resolution store assets, project photography, and image library.",
    "/settings": "Configure store branding, hero banners, testimonials, and sister co-owner accounts.",
    "/audit-trail": "Live activity log of operations performed by the sister administrators.",
}


_SHELL_LAYOUT_CSS = Style("""
    html, body {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }
    .admin-layout {
        max-width: 100vw !important;
        overflow-x: hidden !important;
    }
    @media (max-width: 991.98px) {
        .admin-layout {
            grid-template-columns: minmax(0, 1fr) !important;
        }
    }
    .admin-app,
    main.admin-app {
        min-width: 0 !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
    }
    .admin-content-wrap {
        min-width: 0 !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
    }
    .container.admin-shell,
    .admin-shell {
        min-width: 0 !important;
        max-width: 100% !important;
    }
""")


def page_frame(*children, current: str = "/", title: str = "Overview", subtitle: str | None = None):
    effective_subtitle = subtitle or PAGE_SUBTITLES.get(current, "Manage products, orders, and business documents.")
    return (
        _SHELL_LAYOUT_CSS,
        admin_mobile_header(current, title),
        Div(
            admin_sidebar(current),
            Main(
                Div(
                    Container(
                        Div(
                            P("SJ Interiors", cls="admin-kicker"),
                            H1(title, cls="admin-page-title"),
                            Div(cls="admin-page-header-divider"),
                            P(
                                effective_subtitle,
                                cls="admin-page-copy",
                            ),
                            cls="admin-page-header",
                        ),
                        *children,
                        cls="admin-shell",
                    ),
                    Footer(
                        Container(
                            Div(
                                Span("© 2026 SJ Interiors", cls="admin-footer-link"),
                                Span("·", cls="admin-footer-sep"),
                                A("Public Site", href=settings.public_site_url, target="_blank", rel="noreferrer", cls="admin-footer-link"),
                                Span("·", cls="admin-footer-sep"),
                                A("Sign Out", href="#", cls="admin-footer-link", data_bs_toggle="modal", data_bs_target="#sign-out-confirm-modal"),
                                cls="admin-footer-inner",
                            ),
                        ),
                        cls="admin-footer",
                    ),
                    cls="admin-content-wrap",
                ),
                cls="admin-app",
            ),
            cls="admin-layout",
        ),
        admin_bottom_nav(current),
        admin_mobile_drawer(current),
        _sign_out_confirm_dialog(),
        _media_picker_modal(),
        ModernToastStack(placement=ToastPlacement("top-end"), gap=2, id="toast-container"),
        Div(cls="admin-loading-bar", id="admin-loading-bar"),
    )

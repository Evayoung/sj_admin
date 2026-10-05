"""Shared form widgets and UI helpers for the admin."""

from __future__ import annotations

from typing import Any

from fasthtml.common import Div, Form, H3, H5, Input, Label, Option, P, Select, Small, Span, Textarea, A
from faststrap import Alert, Badge, Button, Card, Icon


def oob_alert(message: str, variant: str = "success", target: str = "save-result") -> Div:
    """Standardized out-of-band HTMX alert message."""
    return Div(
        Alert(message, variant=variant, dismissible=True),
        hx_swap_oob=f"true:#{target}",
    )


def floating_field(name: str, label: str, value: str = "", kind: str = "text",
                   required: bool = False, placeholder: str = "", full: bool = False,
                   readonly: bool = False, hidden: bool = False) -> Div:
    """Floating label input field."""
    if hidden:
        return Input(type="hidden", name=name, value=value)
    width_cls = "col-12" if full else "col-md-6"
    return Div(
        Label(label, fr=f"field-{name}", cls="form-label"),
        Input(
            type=kind,
            name=name,
            id=f"field-{name}",
            value=value or "",
            required=required,
            placeholder=placeholder,
            readonly=readonly,
            cls="form-control",
        ),
        cls=f"{width_cls} mb-3",
    )


def textarea_field(name: str, label: str, value: str = "", required: bool = False,
                   rows: int = 3, full: bool = True, placeholder: str = "") -> Div:
    """Textarea field with label."""
    width_cls = "col-12" if full else "col-md-6"
    return Div(
        Label(label, fr=f"field-{name}", cls="form-label"),
        Textarea(
            name=name,
            id=f"field-{name}",
            rows=rows,
            required=required,
            placeholder=placeholder,
            cls="form-control",
        )(value or ""),
        cls=f"{width_cls} mb-3",
    )


def select_field(name: str, label: str, options: list[tuple[str, str]],
                 value: str = "", full: bool = False) -> Div:
    """Select dropdown field."""
    width_cls = "col-12" if full else "col-md-6"
    option_tags = [
        Option(opt_label, value=opt_val, selected=opt_val == value)
        for opt_val, opt_label in options
    ]
    return Div(
        Label(label, fr=f"field-{name}", cls="form-label"),
        Select(*option_tags, name=name, id=f"field-{name}", cls="form-select"),
        cls=f"{width_cls} mb-3",
    )


def toggle_field(name: str, label: str, checked: bool = False) -> Div:
    """Toggle switch field."""
    return Div(
        Div(
            Input(
                type="checkbox",
                name=name,
                id=f"field-{name}",
                cls="form-check-input",
                checked=checked,
            ),
            Label(label, fr=f"field-{name}", cls="form-check-label"),
            cls="form-check form-switch",
        ),
        cls="col-12 mb-3",
    )


def summary_card(title: str, value: str, icon: str, delta: str = "",
                 delta_color: str = "success") -> Card:
    """Metric summary card for dashboard."""
    delta_elem = ""
    if delta:
        delta_elem = Badge(delta, variant=delta_color, cls="ms-2")
    return Card(
        Div(
            Div(Icon(icon, cls="admin-metric-icon"), cls="admin-metric-icon-wrap"),
            Div(
                P(title, cls="admin-metric-label"),
                H3(value, cls="admin-metric-value"),
                delta_elem,
                cls="d-flex align-items-center gap-2",
            ),
            cls="d-flex align-items-center gap-3",
        ),
        cls="admin-surface-card p-2",
    ) 


def section_wrap(title: str, *children) -> Div:
    """Section with Space Grotesk title."""
    return Div(
        H3(title, cls="admin-section-title"),
        *children,
        cls="admin-section mb-4",
    )


def filter_pill(label: str, href: str, active: bool, cls_suffix: str = "") -> A:
    """Render a polished Faststrap button filter pill with native active state."""
    variant_cls = "btn-primary shadow-xs" if active else "btn-outline-secondary"
    active_attr = {"aria_current": "page"} if active else {}
    return A(
        Span(label),
        href=href,
        cls=f"btn btn-sm rounded-pill px-3 fw-medium filter-pill text-decoration-none {variant_cls} {cls_suffix}".strip(),
        **active_attr,
    )


def status_alert(message: str, variant: str = "danger") -> Div:
    """Status alert for form feedback."""
    return Div(
        Alert(message, variant=variant, dismissible=True),
        role="alert",
    )


def toast_fragment(message: str, variant: str = "success", title: str = "") -> Div:
    """Toast notification fragment for OOB swap into toast stack."""
    icon_map = {
        "success": "check-circle-fill",
        "danger": "x-circle-fill",
        "warning": "exclamation-triangle-fill",
        "info": "info-circle-fill",
    }
    icon_name = icon_map.get(variant, "bell-fill")
    display_title = title or ("Success" if variant == "success" else "Notice" if variant == "info" else "Alert")
    return Div(
        Div(
            Div(
                Icon(icon_name, cls=f"text-{variant} me-2 fs-5"),
                Div(
                    P(display_title, cls="fw-bold mb-0 text-dark small"),
                    P(message, cls="text-secondary small mb-0"),
                ),
                cls="d-flex align-items-center flex-grow-1",
            ),
            Button(type="button", cls="btn-close ms-2", data_bs_dismiss="toast", aria_label="Close"),
            cls="toast-header bg-transparent border-0 d-flex justify-content-between align-items-center p-3",
        ),
        cls=f"toast show shadow-lg border-0 modern-toast-card modern-toast-{variant}",
        style="background: rgba(255, 255, 255, 0.96); backdrop-filter: blur(12px); border-radius: 0.75rem; min-width: 280px; margin-bottom: 0.5rem;",
        role="alert",
        aria_live="assertive",
        aria_atomic="true",
        hx_swap_oob="afterbegin:#toast-container",
    )


def empty_state(title: str, message: str, action_label: str = "",
                action_href: str = "") -> Div:
    """Empty state placeholder."""
    elements = [
        Icon("inbox", cls="admin-empty-icon"),
        H3(title, cls="admin-empty-title"),
        P(message, cls="admin-empty-message"),
    ]
    if action_label and action_href:
        elements.append(Button(action_label, href=action_href, cls="btn btn-primary mt-3"))
    return Div(*elements, cls="text-center py-5 admin-empty-state")


def loading_button(label: str, endpoint: str, target: str = "#save-result",
                   variant: str = "primary", icon: str = "check2-circle",
                   cls_suffix: str = "") -> Button:
    """HTMX loading button with spinner and auto-disable."""
    return Button(
        Span(Icon(icon, cls="me-1"), label),
        type="submit",
        cls=f"btn btn-{variant} px-4 {cls_suffix}".strip(),
        hx_post=endpoint,
        hx_target=target,
        hx_swap="innerHTML",
        hx_disabled_elt="this",
    )

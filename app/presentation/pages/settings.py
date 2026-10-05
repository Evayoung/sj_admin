"""Settings page — brand config and dynamic content management studio."""

from __future__ import annotations

import json
from typing import Any

from fasthtml.common import (
    A, Button, Div, Form, H3, H4, H5, Input, Label, Li, P, Small, Span, Style,
    Textarea, Ul,
)

from faststrap import Badge, Card, Col, Icon, Row

from app.infrastructure.auth_repository import get_admin_users


def settings_page(config: dict, active_tab: str = "general") -> list:
    """Render comprehensive multi-tab settings & brand studio."""
    hero_slides = config.get("hero_slides", []) or []
    testimonials = config.get("testimonials", []) or []
    transformations = config.get("transformations", []) or []

    if isinstance(hero_slides, str):
        try: hero_slides = json.loads(hero_slides)
        except Exception: hero_slides = []
    if isinstance(testimonials, str):
        try: testimonials = json.loads(testimonials)
        except Exception: testimonials = []
    if isinstance(transformations, str):
        try: transformations = json.loads(transformations)
        except Exception: transformations = []

    # CSS: tab scrollbar strictly INSIDE the card; page never gets a horizontal scrollbar
    _settings_tab_css = Style("""
        /* Lock the outer tab wrapper: never wider than viewport */
        .settings-tabs-wrapper {
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
            overflow: hidden !important;
            position: relative !important;
        }
        /* The pill-shaped card that holds the scroller */
        .settings-tabs-card {
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
            overflow: hidden !important;
            background: #ffffff !important;
            border: 1px solid rgba(0, 0, 0, 0.08) !important;
            border-radius: 1rem !important;
        }
        /* The actual horizontally-scrollable track */
        .settings-tabs-scroll {
            display: block !important;
            overflow-x: auto !important;
            overflow-y: hidden !important;
            -webkit-overflow-scrolling: touch !important;
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
            scrollbar-width: thin !important;
            scrollbar-color: rgba(111, 66, 193, 0.25) transparent !important;
            padding: 0.5rem 0.65rem !important;
            margin: 0 !important;
        }
        .settings-tabs-scroll::-webkit-scrollbar {
            height: 3px !important;
        }
        .settings-tabs-scroll::-webkit-scrollbar-thumb {
            background: rgba(111, 66, 193, 0.25) !important;
            border-radius: 3px !important;
        }
        /* The flex list of tab pills — allowed to be as wide as needed */
        .settings-tabs-scroll ul {
            display: inline-flex !important;
            flex-wrap: nowrap !important;
            gap: 0.5rem !important;
            margin: 0 !important;
            padding: 0 !important;
            list-style: none !important;
            width: max-content !important;
        }
        .settings-tabs-scroll li {
            flex-shrink: 0 !important;
            margin: 0 !important;
        }
        /* Tab pane content area: never overflow horizontally */
        .tab-content {
            overflow-x: hidden !important;
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }
        /* Individual tab pill styles */
        .settings-nav-tab {
            display: inline-flex !important;
            align-items: center !important;
            gap: 0.35rem !important;
            padding: 0.42rem 0.95rem !important;
            font-size: 0.84rem !important;
            font-weight: 500 !important;
            border-radius: 9999px !important;
            color: #4b5563 !important;
            background-color: #f8fafc !important;
            border: 1px solid #e2e8f0 !important;
            text-decoration: none !important;
            transition: all 0.15s ease-in-out !important;
            white-space: nowrap !important;
            cursor: pointer !important;
        }
        .settings-nav-tab:hover {
            background-color: #f3e8ff !important;
            color: #6b21a8 !important;
            border-color: #d8b4fe !important;
        }
        .settings-nav-tab.active,
        .settings-nav-tab.active:focus {
            background-color: #6f42c1 !important;
            color: #ffffff !important;
            border-color: #6f42c1 !important;
            box-shadow: 0 2px 6px rgba(111, 66, 193, 0.25) !important;
        }
    """)

    # Card containing the horizontal scroller strictly inside it
    nav_tabs = Div(
        _settings_tab_css,
        Div(
            Div(
                Ul(
                    Li(A(Icon("building", cls="me-2 text-primary"), "Brand & Contact", href="#tab-general", cls="settings-nav-tab active", **{"data-bs-toggle": "tab"}), cls="flex-shrink-0"),
                    Li(A(Icon("images", cls="me-2 text-secondary"), "Hero Slides", href="#tab-hero", cls="settings-nav-tab", **{"data-bs-toggle": "tab"}), cls="flex-shrink-0"),
                    Li(A(Icon("star-fill", cls="me-2 text-warning"), "Testimonials", href="#tab-testimonials", cls="settings-nav-tab", **{"data-bs-toggle": "tab"}), cls="flex-shrink-0"),
                    Li(A(Icon("magic", cls="me-2 text-primary"), "Transformations", href="#tab-transformations", cls="settings-nav-tab", **{"data-bs-toggle": "tab"}), cls="flex-shrink-0"),
                    Li(A(Icon("envelope-fill", cls="me-2 text-danger"), "Notifications", href="#tab-notifications", cls="settings-nav-tab", **{"data-bs-toggle": "tab"}), cls="flex-shrink-0"),
                    Li(A(Icon("people-fill", cls="me-2 text-success"), "Sister Co-Owners (Max 2)", href="#tab-sisters", cls="settings-nav-tab", **{"data-bs-toggle": "tab"}), cls="flex-shrink-0"),

                    cls="nav nav-pills flex-nowrap align-items-center m-0 p-0",
                ),
                cls="settings-tabs-scroll",
            ),
            cls="settings-tabs-card mb-4 shadow-sm",
        ),
        cls="mb-1",
        style="width: 100%; max-width: 100%; overflow: hidden;",
    )

    # ── Tab 1: General Brand Info ────────────────────────────────────────────
    biz_name = config.get("business_name") or "SJ Interiors"
    biz_subtitle = config.get("business_subtitle") or "Deco and Beddings"
    tagline = config.get("tagline") or "Redefining Your Space • Simplicity. Comfort. Style."
    whatsapp_num = config.get("whatsapp_number") or "2348026022672"
    location = config.get("location_short") or "Ilorin, Kwara State"
    address = config.get("address") or "Limca Junction Shopping Complex, Along Asa Dam Road, Ilorin, Kwara State"

    tab_general = Div(
        Row(
            Col(
                Card(
                    H3("Brand Identity & Store Contact Information", cls="h5 fw-bold mb-3 text-dark"),
                    P("Update your store name, tagline, WhatsApp order number, and contact details shown across the public website.", cls="small text-muted mb-4"),
                    Form(
                        Div(id="settings-result"),
                        _field("business_name", "Business Name", biz_name),
                        _field("business_subtitle", "Business Subtitle", biz_subtitle),
                        _field("tagline", "Brand Tagline", tagline),
                        _field("whatsapp_number", "Official WhatsApp Number (No '+' sign)", whatsapp_num, placeholder="e.g. 2348026022672"),
                        _field("phone_numbers", "Phone Numbers (Comma-separated)", ", ".join(config.get("phone_numbers", [])) if isinstance(config.get("phone_numbers"), list) else str(config.get("phone_numbers") or "08026022672, 09115076282"), placeholder="e.g. 08026022672, 09115076282"),
                        _field("address", "Physical Showroom Address", address),
                        _field("location_short", "Short Location / State", location, placeholder="e.g. Ilorin, Kwara State"),
                        Button(
                            Span(Icon("check-circle", cls="me-1"), "Save Brand Settings"),
                            type="submit", cls="btn btn-primary px-4 mt-2 fw-bold",
                            hx_post="/settings/save",
                            hx_include="closest form",
                            hx_target="#settings-result",
                            hx_swap="innerHTML",
                            hx_disabled_elt="this",
                        ),
                        action="/settings/save",
                        method="post",
                    ),
                    cls="p-4 border-0 shadow-sm",
                ),
                span=12, md=6, cls="mb-4",
            ),
            Col(
                Card(
                    H3("Live Brand Overview", cls="h6 fw-bold mb-3 text-dark"),
                    Div(
                        P(Span("Store Name: ", cls="fw-bold text-dark"), Span(biz_name, cls="text-secondary"), cls="mb-2 small"),
                        P(Span("Tagline: ", cls="fw-bold text-dark"), Span(tagline, cls="text-secondary"), cls="mb-2 small"),
                        P(Span("WhatsApp: ", cls="fw-bold text-dark"), Span(whatsapp_num, cls="text-secondary"), cls="mb-2 small"),
                        P(Span("Showroom: ", cls="fw-bold text-dark"), Span(location, cls="text-secondary"), cls="mb-0 small"),
                        cls="bg-light p-3 rounded-2 border",
                    ),
                    cls="p-4 border-0 shadow-sm",
                ),
                span=12, md=6, cls="mb-4",
            ),
            cls="g-4",
        ),
        id="tab-general", cls="tab-pane fade show active",
    )

    # ── Tab 2: Hero Slides ───────────────────────────────────────────────────
    slides_inputs = []
    for idx, slide in enumerate(hero_slides):
        title_val = slide.get("title", "") if isinstance(slide, dict) else str(slide)
        desc_val = slide.get("description", "") if isinstance(slide, dict) else ""
        img_val = slide.get("image_url", "") if isinstance(slide, dict) else ""
        slides_inputs.append(
            Div(
                Row(
                    Col(
                        Label("Slide Title", cls="form-label small fw-bold"),
                        Input(type="text", name="slide_title[]", value=title_val, class_="form-control form-control-sm mb-2", required=True),
                        Label("Image URL", cls="form-label small fw-bold"),
                        Input(type="url", name="slide_image[]", value=img_val, class_="form-control form-control-sm", required=True),
                        lg=5,
                    ),
                    Col(
                        Label("Description / Subtitle", cls="form-label small fw-bold"),
                        Textarea(desc_val, name="slide_desc[]", rows="3", class_="form-control form-control-sm mb-2"),
                        Button(Icon("trash"), type="button", cls="btn btn-outline-danger btn-sm", onclick="this.closest('.p-3').remove();"),
                        lg=7,
                    ),
                    cls="g-2",
                ),
                cls="p-3 bg-light border rounded-3 mb-3",
            )
        )

    tab_hero = Div(
        Card(
            Div(
                H3("Hero Banner Slides", cls="h5 fw-bold mb-1 text-dark"),
                P("Configure dynamic image slides, headings, and descriptions for the homepage showcase.", cls="small text-muted mb-4"),
                Form(
                    Div(id="hero-result"),
                    Div(*slides_inputs, id="hero-slides-container"),
                    Button(
                        Span(Icon("plus-circle", cls="me-1"), "Add New Slide"),
                        type="button", cls="btn btn-outline-secondary btn-sm me-2",
                        onclick="""
                            const container = document.getElementById('hero-slides-container');
                            const div = document.createElement('div');
                            div.className = 'p-3 bg-light border rounded-3 mb-3';
                            div.innerHTML = `
                                <div class="row g-2">
                                    <div class="col-lg-5">
                                        <label class="form-label small fw-bold">Slide Title</label>
                                        <input type="text" name="slide_title[]" class="form-control form-control-sm mb-2" required placeholder="Slide Title" />
                                        <label class="form-label small fw-bold">Image URL</label>
                                        <input type="url" name="slide_image[]" class="form-control form-control-sm" required placeholder="https://..." />
                                    </div>
                                    <div class="col-lg-7">
                                        <label class="form-label small fw-bold">Description / Subtitle</label>
                                        <textarea name="slide_desc[]" rows="3" class="form-control form-control-sm mb-2" placeholder="Subtitle"></textarea>
                                        <button type="button" class="btn btn-outline-danger btn-sm" onclick="this.closest('.p-3').remove();"><i class="bi bi-trash"></i></button>
                                    </div>
                                </div>
                            `;
                            container.appendChild(div);
                        """,
                    ),
                    Button(
                        Span(Icon("check-circle", cls="me-1"), "Save Hero Slides"),
                        type="submit", cls="btn btn-primary btn-sm fw-bold px-4",
                        hx_post="/settings/hero/save",
                        hx_include="closest form",
                        hx_target="#hero-result",
                        hx_swap="innerHTML",
                        hx_disabled_elt="this",
                    ),
                    cls="mt-3",
                ),
                action="/settings/hero/save",
                method="post",
            ),
            cls="p-4 border-0 shadow-sm",
        ),
        id="tab-hero", cls="tab-pane fade",
    )

    # ── Tab 3: Testimonials ──────────────────────────────────────────────────
    test_inputs = []
    for idx, t in enumerate(testimonials):
        name = t.get("name", "") if isinstance(t, dict) else ""
        role = t.get("role", "") if isinstance(t, dict) else ""
        text = t.get("text", "") if isinstance(t, dict) else ""
        test_inputs.append(
            Div(
                Row(
                    Col(
                        Label("Client Name", cls="form-label small fw-bold"),
                        Input(type="text", name="test_name[]", value=name, class_="form-control form-control-sm mb-2", required=True),
                        Label("Role / Location", cls="form-label small fw-bold"),
                        Input(type="text", name="test_role[]", value=role, class_="form-control form-control-sm", placeholder="e.g. Homeowner, GRA Ilorin"),
                        lg=4,
                    ),
                    Col(
                        Label("Review / Feedback Quote", cls="form-label small fw-bold"),
                        Textarea(text, name="test_text[]", rows="3", class_="form-control form-control-sm mb-2", required=True),
                        Button(Icon("trash"), type="button", cls="btn btn-outline-danger btn-sm", onclick="this.closest('.p-3').remove();"),
                        lg=8,
                    ),
                    cls="g-2",
                ),
                cls="p-3 bg-light border rounded-3 mb-3",
            )
        )

    tab_testimonials = Div(
        Card(
            Div(
                H3("Client Testimonials", cls="h5 fw-bold mb-1 text-dark"),
                P("Manage authentic customer reviews displayed on the public storefront.", cls="small text-muted mb-4"),
                Form(
                    Div(id="testimonials-result"),
                    Div(*test_inputs, id="testimonials-container"),
                    Button(
                        Span(Icon("plus-circle", cls="me-1"), "Add Testimonial"),
                        type="button", cls="btn btn-outline-secondary btn-sm me-2",
                        onclick="""
                            const container = document.getElementById('testimonials-container');
                            const div = document.createElement('div');
                            div.className = 'p-3 bg-light border rounded-3 mb-3';
                            div.innerHTML = `
                                <div class="row g-2">
                                    <div class="col-lg-4">
                                        <label class="form-label small fw-bold">Client Name</label>
                                        <input type="text" name="test_name[]" class="form-control form-control-sm mb-2" required placeholder="e.g. Mrs. Funke" />
                                        <label class="form-label small fw-bold">Role / Location</label>
                                        <input type="text" name="test_role[]" class="form-control form-control-sm" placeholder="e.g. Tanke, Ilorin" />
                                    </div>
                                    <div class="col-lg-8">
                                        <label class="form-label small fw-bold">Review / Feedback Quote</label>
                                        <textarea name="test_text[]" rows="3" class="form-control form-control-sm mb-2" required placeholder="Their review..."></textarea>
                                        <button type="button" class="btn btn-outline-danger btn-sm" onclick="this.closest('.p-3').remove();"><i class="bi bi-trash"></i></button>
                                    </div>
                                </div>
                            `;
                            container.appendChild(div);
                        """,
                    ),
                    Button(
                        Span(Icon("check-circle", cls="me-1"), "Save Testimonials"),
                        type="submit", cls="btn btn-primary btn-sm fw-bold px-4",
                        hx_post="/settings/testimonials/save",
                        hx_include="closest form",
                        hx_target="#testimonials-result",
                        hx_swap="innerHTML",
                        hx_disabled_elt="this",
                    ),
                    cls="mt-3",
                ),
                action="/settings/testimonials/save",
                method="post",
            ),
            cls="p-4 border-0 shadow-sm",
        ),
        id="tab-testimonials", cls="tab-pane fade",
    )

    # ── Tab 4: Space Transformations ─────────────────────────────────────────
    tr_inputs = []
    for idx, tr in enumerate(transformations):
        title = tr.get("title", "") if isinstance(tr, dict) else ""
        tag = tr.get("tag", "") if isinstance(tr, dict) else ""
        before = tr.get("before", "") if isinstance(tr, dict) else ""
        after = tr.get("after", "") if isinstance(tr, dict) else ""
        img = tr.get("image_url", "") if isinstance(tr, dict) else ""
        tr_inputs.append(
            Div(
                Row(
                    Col(
                        Label("Project Title", cls="form-label small fw-bold"),
                        Input(type="text", name="tr_title[]", value=title, class_="form-control form-control-sm mb-2", required=True),
                        Label("Category / Tag", cls="form-label small fw-bold"),
                        Input(type="text", name="tr_tag[]", value=tag, class_="form-control form-control-sm mb-2", placeholder="e.g. Window Styling"),
                        Label("Showcase Image URL", cls="form-label small fw-bold"),
                        Input(type="url", name="tr_image[]", value=img, class_="form-control form-control-sm", required=True),
                        lg=4,
                    ),
                    Col(
                        Label("Before State", cls="form-label small fw-bold"),
                        Input(type="text", name="tr_before[]", value=before, class_="form-control form-control-sm mb-2"),
                        Label("After Transformation", cls="form-label small fw-bold"),
                        Textarea(after, name="tr_after[]", rows="3", class_="form-control form-control-sm mb-2"),
                        Button(Icon("trash"), type="button", cls="btn btn-outline-danger btn-sm", onclick="this.closest('.p-3').remove();"),
                        lg=8,
                    ),
                    cls="g-3",
                ),
                cls="p-3 bg-light border rounded-3 mb-3",
            )
        )

    tab_transformations = Div(
        Card(
            Div(
                H3("Space Transformations Showcase", cls="h5 fw-bold mb-1 text-dark"),
                P("Curate before-and-after case studies highlighting dramatic room improvements.", cls="small text-muted mb-4"),
                Form(
                    Div(id="transformations-result"),
                    Div(*tr_inputs, id="transformations-container"),
                    Button(
                        Span(Icon("plus-circle", cls="me-1"), "Add Transformation"),
                        type="button", cls="btn btn-outline-secondary btn-sm me-2",
                        onclick="""
                            const container = document.getElementById('transformations-container');
                            const div = document.createElement('div');
                            div.className = 'p-3 bg-light border rounded-3 mb-3';
                            div.innerHTML = `
                                <div class="row g-3">
                                    <div class="col-lg-4">
                                        <label class="form-label small fw-bold">Project Title</label>
                                        <input type="text" name="tr_title[]" class="form-control form-control-sm mb-2" required placeholder="e.g. GRA 4-Bedroom Duplex" />
                                        <label class="form-label small fw-bold">Category / Tag</label>
                                        <input type="text" name="tr_tag[]" class="form-control form-control-sm mb-2" placeholder="e.g. Full House Dressing" />
                                        <label class="form-label small fw-bold">Showcase Image URL</label>
                                        <input type="url" name="tr_image[]" class="form-control form-control-sm" required placeholder="https://..." />
                                    </div>
                                    <div class="col-lg-8">
                                        <label class="form-label small fw-bold">Before State</label>
                                        <input type="text" name="tr_before[]" class="form-control form-control-sm mb-2" placeholder="e.g. Bare windows" />
                                        <label class="form-label small fw-bold">After Transformation</label>
                                        <textarea name="tr_after[]" rows="3" class="form-control form-control-sm" placeholder="e.g. Styled eyelet drapes"></textarea>
                                        <button type="button" class="btn btn-outline-danger btn-sm mt-2" onclick="this.closest('.p-3').remove();"><i class="bi bi-trash"></i></button>
                                    </div>
                                </div>
                            `;
                            container.appendChild(div);
                        """,
                    ),
                    Button(
                        Span(Icon("check-circle", cls="me-1"), "Save Transformations"),
                        type="submit", cls="btn btn-primary btn-sm fw-bold px-4",
                        hx_post="/settings/transformations/save",
                        hx_include="closest form",
                        hx_target="#transformations-result",
                        hx_swap="innerHTML",
                        hx_disabled_elt="this",
                    ),
                    cls="mt-3",
                ),
                action="/settings/transformations/save",
                method="post",
            ),
            cls="p-4 border-0 shadow-sm",
        ),
        id="tab-transformations", cls="tab-pane fade",
    )

    # ── Tab 5: Notifications & Email / SMTP Config ────────────────────────────
    from app.config import settings as _cfg  # noqa: PLC0415

    smtp_host      = config.get("smtp_host")      or _cfg.smtp_host
    smtp_port      = config.get("smtp_port")      or str(_cfg.smtp_port)
    smtp_user      = config.get("smtp_user")      or _cfg.smtp_user
    smtp_password  = config.get("smtp_password")  or _cfg.smtp_password
    smtp_from_name = config.get("smtp_from_name") or _cfg.smtp_from_name
    smtp_from_email= config.get("smtp_from_email")or _cfg.smtp_from_email or _cfg.smtp_user

    tab_notifications = Div(
        Row(
            Col(
                Card(
                    H3("Email & SMTP Configuration", cls="h5 fw-bold mb-1 text-dark"),
                    P(
                        "Configure the email account used for sending password recovery emails to the co-owners. "
                        "Changes here take effect immediately — no restart required.",
                        cls="small text-muted mb-4",
                    ),
                    Div(
                        Icon("info-circle-fill", cls="me-2 text-primary"),
                        Span(
                            "Currently using a Gmail App Password. Never put your normal Gmail password here — "
                            "generate an App Password at ",
                            cls="small",
                        ),
                        A("myaccount.google.com/apppasswords", href="https://myaccount.google.com/apppasswords",
                          target="_blank", rel="noreferrer", cls="small text-primary"),
                        cls="d-flex align-items-start gap-1 p-3 bg-light border rounded-3 mb-4 small text-muted",
                    ),
                    Form(
                        Div(id="notifications-result"),
                        Row(
                            Col(_field("smtp_host", "SMTP Host", str(smtp_host), placeholder="smtp.gmail.com"), span=12, md=8),
                            Col(_field("smtp_port", "Port", str(smtp_port), placeholder="587"), span=12, md=4),
                        ),
                        _field("smtp_user", "SMTP Username / Email Account", str(smtp_user), placeholder="skuphase@gmail.com"),
                        Div(
                            Label("SMTP Password (App Password)", fr="settings-smtp_password", cls="form-label small fw-bold text-dark"),
                            Input(type="password", name="smtp_password", id="settings-smtp_password",
                                  value=str(smtp_password),
                                  cls="form-control form-control-sm",
                                  placeholder="Gmail App Password (16 chars, no spaces)"),
                            cls="mb-3",
                        ),
                        _field("smtp_from_name", "From Name (displayed to recipient)", str(smtp_from_name), placeholder="SJ Interiors"),
                        _field("smtp_from_email", "From Email Address", str(smtp_from_email), placeholder="skuphase@gmail.com"),
                        Button(
                            Span(Icon("check-circle", cls="me-1"), "Save Email Settings"),
                            type="submit", cls="btn btn-primary px-4 mt-2 fw-bold",
                            hx_post="/settings/notifications/save",
                            hx_include="closest form",
                            hx_target="#notifications-result",
                            hx_swap="innerHTML",
                            hx_disabled_elt="this",
                        ),
                        action="/settings/notifications/save",
                        method="post",
                    ),
                    cls="p-4 border-0 shadow-sm",
                ),
                span=12, md=7, cls="mb-4",
            ),
            Col(
                Card(
                    H3("Test Email Delivery", cls="h6 fw-bold mb-2 text-dark"),
                    P("Send a test email to verify your SMTP settings are working correctly.", cls="small text-muted mb-3"),
                    Form(
                        Div(id="test-email-result"),
                        Div(
                            Label("Send Test Email To", cls="form-label small fw-bold"),
                            Input(type="email", name="test_to", placeholder="e.g. alademercy93@gmail.com",
                                  cls="form-control form-control-sm mb-3", required=True),
                        ),
                        Button(
                            Span(Icon("send", cls="me-1"), "Send Test Email"),
                            type="submit", cls="btn btn-outline-primary btn-sm fw-bold px-4",
                            hx_post="/settings/notifications/test",
                            hx_include="closest form",
                            hx_target="#test-email-result",
                            hx_swap="innerHTML",
                            hx_disabled_elt="this",
                        ),
                        action="/settings/notifications/test",
                        method="post",
                    ),
                    cls="p-4 border-0 shadow-sm mb-4",
                ),
                Card(
                    H3("Current SMTP Status", cls="h6 fw-bold mb-3 text-dark"),
                    Div(
                        P(Span("Host: ", cls="fw-bold text-dark"), Span(f"{smtp_host}:{smtp_port}", cls="text-secondary font-monospace"), cls="mb-2 small"),
                        P(Span("Account: ", cls="fw-bold text-dark"), Span(smtp_user or "Not configured", cls="text-secondary"), cls="mb-2 small"),
                        P(Span("From Name: ", cls="fw-bold text-dark"), Span(smtp_from_name or "SJ Interiors", cls="text-secondary"), cls="mb-0 small"),
                        cls="bg-light p-3 rounded-2 border",
                    ),
                    cls="p-4 border-0 shadow-sm",
                ),
                span=12, md=5, cls="mb-4",
            ),
            cls="g-4",
        ),
        id="tab-notifications", cls="tab-pane fade",
    )


    sisters = get_admin_users()
    sister_cards = []
    for idx, s in enumerate(sisters[:2]):
        u_id = s.get("id", f"sister-{idx+1}")
        full_name = s.get("full_name") or f"Sister {idx+1}"
        email = s.get("email") or f"sister{idx+1}@sjinteriors.com"
        username = s.get("username") or f"sister{idx+1}"
        last_login = s.get("last_login_at") or "Not yet recorded"

        sister_cards.append(
            Col(
                Card(
                    Div(
                        Div(
                            Span(f"Co-Owner {idx+1}", cls="badge bg-primary text-white me-2 small"),
                            H4(full_name, cls="h6 fw-bold mb-0 text-dark"),
                            cls="d-flex align-items-center mb-2",
                        ),
                        P(f"Username: {username} · Equal Superadmin Access", cls="text-muted small mb-3"),
                        Form(
                            Div(id=f"sister-{u_id}-result"),
                            Input(type="hidden", name="user_id", value=u_id),
                            Div(
                                Label("Full Name & Role", cls="form-label small fw-bold"),
                                Input(type="text", name="full_name", value=full_name, required=True, cls="form-control form-control-sm mb-2"),
                            ),
                            Div(
                                Label("Personal Email (for Login & Password Recovery)", cls="form-label small fw-bold"),
                                Input(type="email", name="email", value=email, required=True, cls="form-control form-control-sm mb-2"),
                            ),
                            Div(
                                Label("Change Password (leave blank to keep current)", cls="form-label small fw-bold"),
                                Input(type="password", name="new_password", placeholder="Enter new password (min 8 chars)", minlength="8", cls="form-control form-control-sm mb-3"),
                            ),
                            Div(
                                Small(f"Last Login: {last_login[:19].replace('T', ' ')}", cls="text-muted d-block mb-3"),
                                Button(
                                    Icon("check2", cls="me-1"), f"Update {username.title()}'s Profile",
                                    type="submit", cls="btn btn-outline-primary btn-sm fw-semibold w-100",
                                    hx_post="/settings/save-sister",
                                    hx_include="closest form",
                                    hx_target=f"#sister-{u_id}-result",
                                    hx_swap="innerHTML",
                                    hx_disabled_elt="this",
                                ),
                            ),
                            action="/settings/save-sister",
                            method="post",
                        ),
                        cls="p-3",
                    ),
                    cls="border-0 shadow-sm",
                ),
                span=12, md=6, cls="mb-4",
            )
        )

    tab_sisters = Div(
        Card(
            Div(
                Div(
                    H3("Sister Co-Owners & System Access", cls="h5 fw-bold mb-1 text-dark"),
                    P("SJ Interiors is operated exclusively by the two sister owners with equal administrative access.", cls="small text-muted mb-0"),
                ),
                Badge("Strict Policy: Exactly 2 Accounts Permitted", variant="dark", cls="px-3 py-2"),
                cls="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-4 pb-3 border-bottom",
            ),
            Row(*sister_cards, cls="g-3"),
            Div(
                Icon("shield-lock-fill", cls="me-2 text-primary"),
                Span("Security Policy: All admin actions are individually audited to show who did what. Password recovery is dispatched exclusively to the verified personal email address above.", cls="small text-muted"),
                cls="p-3 bg-light rounded-3 border mt-2",
            ),
            cls="p-4 border-0 shadow-sm",
        ),
        id="tab-sisters", cls="tab-pane fade",
    )

    tab_content = Div(
        tab_general,
        tab_hero,
        tab_testimonials,
        tab_transformations,
        tab_notifications,
        tab_sisters,
        cls="tab-content",
    )


    return [
        Div(
            nav_tabs,
            tab_content,
            cls="brand-settings-studio",
            style="width: 100%; max-width: 100%; overflow-x: hidden;",
        ),
    ]


def _field(name: str, label: str, value: str, placeholder: str = "") -> Div:
    return Div(
        Label(label, fr=f"settings-{name}", cls="form-label small fw-bold text-dark"),
        Input(type="text", name=name, id=f"settings-{name}", value=value,
              cls="form-control form-control-sm", placeholder=placeholder),
        cls="mb-3",
    )

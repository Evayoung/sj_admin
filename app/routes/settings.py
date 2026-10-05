"""Settings & Brand Studio routes with audit logging and 2-sister account management."""

from __future__ import annotations

from typing import Any
from starlette.requests import Request
from fasthtml.common import Div

try:
    from ..infrastructure.audit_repository import log_activity
    from ..infrastructure.auth_repository import update_sister_profile
    from ..infrastructure.brand_repository import get_brand_config, update_brand_config
    from ..presentation.page_helpers import oob_alert, toast_fragment
    from ..presentation.shell import page_frame
    from ..presentation.pages.settings import settings_page
except ImportError:
    from app.infrastructure.audit_repository import log_activity
    from app.infrastructure.auth_repository import update_sister_profile
    from app.infrastructure.brand_repository import get_brand_config, update_brand_config
    from app.presentation.page_helpers import oob_alert, toast_fragment
    from app.presentation.shell import page_frame
    from app.presentation.pages.settings import settings_page


def register_settings_routes(app: Any) -> None:

    @app.get("/settings")
    def settings_view():
        config = get_brand_config()
        return page_frame(*settings_page(config), current="/settings", title="Settings & Brand Studio")

    @app.post("/settings/save")
    def settings_save(
        req: Request,
        business_name: str = "",
        business_subtitle: str = "",
        tagline: str = "",
        whatsapp_number: str = "",
        phone_numbers: str = "",
        address: str = "",
        location_short: str = "",
    ):
        """HTMX: save general brand settings."""
        session = req.scope.get("session", {})
        updates = {
            "business_name": business_name,
            "business_subtitle": business_subtitle,
            "tagline": tagline,
            "whatsapp_number": whatsapp_number,
            "phone_numbers": [p.strip() for p in phone_numbers.split(",") if p.strip()],
            "address": address,
            "location_short": location_short,
        }

        success = True
        for key, value in updates.items():
            if not update_brand_config(key, value):
                success = False

        if success:
            log_activity(req, session, "UPDATE_SETTINGS", "settings", "brand_config", f"Updated store contact & identity ({business_name})")
            return oob_alert("Brand settings saved successfully!", variant="success", target="settings-result"), toast_fragment("Brand settings saved successfully!", variant="success")
        return oob_alert("Some settings failed to save.", variant="danger", target="settings-result"), toast_fragment("Some settings failed to save.", variant="danger")

    @app.post("/settings/hero/save")
    async def settings_hero_save(req: Request):
        """HTMX: save hero banner slides array."""
        session = req.scope.get("session", {})
        form = await req.form()
        titles = form.getlist("slide_title[]")
        images = form.getlist("slide_image[]")
        descs = form.getlist("slide_desc[]")

        slides = []
        for i in range(len(images)):
            img = str(images[i]).strip()
            if img:
                title = str(titles[i]).strip() if i < len(titles) else ""
                desc = str(descs[i]).strip() if i < len(descs) else ""
                slides.append({"title": title, "image_url": img, "description": desc})

        if update_brand_config("hero_slides", slides):
            log_activity(req, session, "UPDATE_SETTINGS", "settings", "hero_slides", f"Updated hero slides ({len(slides)} slides)")
            return oob_alert("Hero slides saved successfully!", variant="success", target="hero-result"), toast_fragment("Hero slides saved successfully!", variant="success")
        return oob_alert("Failed to save hero slides.", variant="danger", target="hero-result"), toast_fragment("Failed to save hero slides.", variant="danger")

    @app.post("/settings/testimonials/save")
    async def settings_testimonials_save(req: Request):
        """HTMX: save customer testimonials array."""
        session = req.scope.get("session", {})
        form = await req.form()
        names = form.getlist("test_name[]")
        roles = form.getlist("test_role[]")
        texts = form.getlist("test_text[]")

        testimonials = []
        for i in range(len(names)):
            name = str(names[i]).strip()
            text = str(texts[i]).strip() if i < len(texts) else ""
            if name and text:
                role = str(roles[i]).strip() if i < len(roles) else "Client"
                testimonials.append({
                    "name": name,
                    "role": role,
                    "text": text,
                })

        if update_brand_config("testimonials", testimonials):
            log_activity(req, session, "UPDATE_SETTINGS", "settings", "testimonials", f"Updated customer testimonials ({len(testimonials)} reviews)")
            return oob_alert("Testimonials saved successfully!", variant="success", target="testimonials-result"), toast_fragment("Testimonials saved successfully!", variant="success")
        return oob_alert("Failed to save testimonials.", variant="danger", target="testimonials-result"), toast_fragment("Failed to save testimonials.", variant="danger")

    @app.post("/settings/transformations/save")
    async def settings_transformations_save(req: Request):
        """HTMX: save space transformations array."""
        session = req.scope.get("session", {})
        form = await req.form()
        titles = form.getlist("tr_title[]")
        tags = form.getlist("tr_tag[]")
        images = form.getlist("tr_image[]")
        befores = form.getlist("tr_before[]")
        afters = form.getlist("tr_after[]")

        transformations = []
        for i in range(len(titles)):
            title = str(titles[i]).strip()
            img = str(images[i]).strip() if i < len(images) else ""
            if title and img:
                transformations.append({
                    "title": title,
                    "tag": str(tags[i]).strip() if i < len(tags) else "Transformation",
                    "image_url": img,
                    "before": str(befores[i]).strip() if i < len(befores) else "",
                    "after": str(afters[i]).strip() if i < len(afters) else "",
                })

        if update_brand_config("transformations", transformations):
            log_activity(req, session, "UPDATE_SETTINGS", "settings", "transformations", f"Updated space transformations ({len(transformations)} projects)")
            return oob_alert("Transformations saved successfully!", variant="success", target="transformations-result"), toast_fragment("Space transformations saved successfully!", variant="success")
        return oob_alert("Failed to save transformations.", variant="danger", target="transformations-result"), toast_fragment("Failed to save transformations.", variant="danger")

    @app.post("/settings/save-sister")
    def settings_sister_save(req: Request, user_id: str = "", full_name: str = "", email: str = "", new_password: str = ""):
        """HTMX: update a sister co-owner's personal profile and password."""
        session = req.scope.get("session", {})
        ok, msg = update_sister_profile(user_id, full_name, email, new_password)
        if ok:
            log_activity(req, session, "UPDATE_SISTER_PROFILE", "auth", user_id, f"Updated sister account profile for {full_name} ({email})")
            return oob_alert(msg, variant="success", target=f"sister-{user_id}-result"), toast_fragment(msg, variant="success")
        return oob_alert(msg, variant="danger", target=f"sister-{user_id}-result"), toast_fragment(msg, variant="danger")

    @app.post("/settings/notifications/save")
    def settings_notifications_save(
        req: Request,
        smtp_host: str = "",
        smtp_port: str = "",
        smtp_user: str = "",
        smtp_password: str = "",
        smtp_from_name: str = "",
        smtp_from_email: str = "",
    ):
        """HTMX: save SMTP / email delivery settings to brand_config DB."""
        session = req.scope.get("session", {})
        updates = {
            "smtp_host":       smtp_host.strip() or "smtp.gmail.com",
            "smtp_port":       smtp_port.strip() or "587",
            "smtp_user":       smtp_user.strip(),
            "smtp_from_name":  smtp_from_name.strip() or "SJ Interiors",
            "smtp_from_email": smtp_from_email.strip() or smtp_user.strip(),
        }
        # Only update password if one was supplied (don't blank it out on re-save)
        if smtp_password.strip():
            updates["smtp_password"] = smtp_password.strip()

        success = all(update_brand_config(k, v) for k, v in updates.items())
        if success:
            log_activity(req, session, "UPDATE_SETTINGS", "settings", "smtp_config",
                         f"Email/SMTP settings updated by {session.get('admin_user_name', 'Admin')} — account: {smtp_user}")
            return oob_alert("Email settings saved! Changes are active immediately.", variant="success", target="notifications-result"), \
                   toast_fragment("Email settings saved.", variant="success")
        return oob_alert("Some email settings failed to save. Check Supabase connection.", variant="danger", target="notifications-result"), \
               toast_fragment("Email save failed.", variant="danger")

    @app.post("/settings/notifications/test")
    def settings_notifications_test(req: Request, test_to: str = ""):
        """HTMX: send a test email to verify SMTP configuration."""
        from app.infrastructure.email_service import send_email
        clean_to = (test_to or "").strip()
        if not clean_to or "@" not in clean_to:
            return oob_alert("Please enter a valid email address to send the test to.", variant="danger", target="test-email-result")

        sent, msg = send_email(
            to_email=clean_to,
            subject="SJ Interiors — SMTP Test Email",
            html_body=(
                "<h2 style='color:#6b1d49'>SJ Interiors SMTP Test</h2>"
                "<p>Your email settings are working correctly.</p>"
                "<p>This test was sent from the Admin Settings &gt; Notifications panel.</p>"
                "<hr><p style='color:#9ca3af;font-size:12px'>SJ Interior Deco &amp; Beddings · Ilorin, Kwara State</p>"
            ),
            text_body="SJ Interiors SMTP test — your email settings are working correctly.",
        )
        if sent:
            return oob_alert(f"Test email sent successfully to {clean_to}!", variant="success", target="test-email-result"), \
                   toast_fragment("Test email sent!", variant="success")
        return oob_alert(f"Test failed: {msg}", variant="danger", target="test-email-result"), \
               toast_fragment("Test email failed.", variant="danger")


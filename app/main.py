"""FastHTML app shell for SJ Interiors Admin."""

from __future__ import annotations

import time as _session_time
from pathlib import Path
from urllib.parse import quote

from fasthtml.common import Beforeware, FastHTML, Link, Redirect, Script
from faststrap import add_bootstrap, add_pwa, mount_assets

try:
    from .config import settings
    from .routes import setup_routes
    from .theme import SJ_ADMIN_THEME, setup_theme_defaults
except ImportError:
    from config import settings
    from routes import setup_routes
    from theme import SJ_ADMIN_THEME, setup_theme_defaults

BASE_DIR = Path(__file__).resolve().parent.parent


def _require_admin_login(req, session):
    """Protect all routes except login, logout, and static assets."""
    expires_at = session.get("expires_at", 0)
    if expires_at and _session_time.time() > expires_at:
        session.clear()
    if session.get("admin_authenticated"):
        return None
    next_path = req.url.path
    if req.url.query:
        next_path = f"{next_path}?{req.url.query}"
    return Redirect(f"/login?next_path={quote(next_path, safe='/?=&')}")


JS_VERSION = "20260724"

app = FastHTML(secret_key=settings.secret_key, session_cookie=settings.session_cookie)
app.before.append(
    Beforeware(
        _require_admin_login,
        skip=[
            r"/login",
            r"/logout",
            r"^/forgot-password",
            r"^/reset-password",
            r"/assets/.*",
            r"/favicon.ico",
            r"/manifest\.json",
            r"/sw\.js",
            r"/offline",
            r"^/documents/(preview|pdf|download|print|respond|decision|comment|confirm-payment)/.*",
        ],
    )
)

add_bootstrap(app, theme=SJ_ADMIN_THEME, mode="light", use_cdn=settings.use_cdn)
add_pwa(
    app,
    name="SJ Interiors Admin",
    short_name="SJAdmin",
    description="Manage SJ Interiors products, orders, and documents.",
    theme_color="#f7f3fb",
    background_color="#f7f3fb",
    icon_path="/assets/icon-512.png",
    cache_name="sj-admin-shell",
    cache_version="v1",
    pre_cache_urls=[
        "/assets/css/custom.css",
        f"/assets/js/admin.js?v={JS_VERSION}",
        "/assets/icon-192.png",
        "/assets/icon-512.png",
    ],
)
setup_theme_defaults()

# Always mount local /assets so custom.css, admin.js, and icons are served
# (use_cdn only controls Bootstrap/Faststrap CDN — local assets are always needed)
mount_assets(app, str(BASE_DIR / "assets"), url_path="/assets")

app.hdrs = app.hdrs + [
    Link(rel="preconnect", href="https://fonts.googleapis.com"),
    Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin="anonymous"),
    Link(
        rel="stylesheet",
        href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap",
    ),
    Link(rel="stylesheet", href=f"/assets/css/custom.css?v={JS_VERSION}"),
    Script(src=f"/assets/js/admin.js?v={JS_VERSION}", defer=True),
]

setup_routes(app)

if __name__ == "__main__":
    from fasthtml.common import serve
    serve(port=settings.port)

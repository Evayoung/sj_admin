"""Environment and project configuration for SJ Interiors Admin."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*_args, **_kwargs) -> bool:
        return False


BASE_DIR = Path(__file__).resolve().parent.parent
_vercel_val = os.getenv("VERCEL", "").strip().lower()
if _vercel_val not in ("1", "true"):
    load_dotenv(BASE_DIR / ".env")
    # Re-read after loading .env
    _vercel_val = os.getenv("VERCEL", "").strip().lower()


@dataclass(frozen=True)
class Settings:
    secret_key: str = os.getenv("SJ_ADMIN_SECRET_KEY", "sj-admin-dev-secret-key-change-in-production")
    session_cookie: str = "sj_admin_session"
    use_cdn: bool = _vercel_val in ("1", "true")
    port: int = int(os.getenv("PORT", "5063"))
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    admin_username: str = os.getenv("SJ_ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("SJ_ADMIN_PASSWORD", "admin123")
    public_site_url: str = os.getenv("PUBLIC_SITE_URL", "http://localhost:5057")
    # Store contact defaults (overridable from Admin Settings)
    whatsapp_number: str = os.getenv("WHATSAPP_NUMBER", "2348026022672")
    phone_number: str = os.getenv("PHONE_NUMBER", "+234 (911) 507-6282")
    phone_numbers: str = os.getenv("PHONE_NUMBERS", "08026022672,09115076282")
    address: str = os.getenv("ADDRESS", "Limca Junction Shopping Complex, Along Asa Dam Road, Ilorin, Kwara State")
    location_short: str = os.getenv("LOCATION_SHORT", "Ilorin, Kwara State")
    # SMTP email settings (overridable from Admin Settings > Notifications)
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from_email: str = os.getenv("SMTP_FROM_EMAIL", "")
    smtp_from_name: str = os.getenv("SMTP_FROM_NAME", "SJ Interiors")
    smtp_tls: bool = os.getenv("SMTP_TLS", "True").strip().lower() in ("1", "true")
    smtp_ssl: bool = os.getenv("SMTP_SSL", "False").strip().lower() in ("1", "true")


settings = Settings()

"""Email delivery service for SJ Interiors Admin.

Sends transactional emails (password recovery) via SMTP.
Config priority:
  1. brand_config DB table  (updated from Admin Settings > Notifications)
  2. .env environment variables
  3. Hard-coded defaults (smtp.gmail.com:587)

This means once a sister changes SMTP settings in the admin UI, emails
immediately use the new config without any restart.
"""

from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


def _get_smtp_config() -> dict[str, Any]:
    """Build SMTP config: DB brand_config first, then .env, then defaults."""
    # Try to load from brand_config table (admin-managed)
    try:
        from app.infrastructure.brand_repository import get_brand_config
        cfg = get_brand_config()
    except Exception:
        cfg = {}

    def _pick(db_key: str, env_val: Any) -> Any:
        """Return DB value if present and non-empty, else fall back to env."""
        v = cfg.get(db_key)
        if v is not None and str(v).strip():
            return v
        return env_val

    return {
        "host":       str(_pick("smtp_host",       settings.smtp_host)),
        "port":       int(_pick("smtp_port",       settings.smtp_port)),
        "user":       str(_pick("smtp_user",       settings.smtp_user)),
        "password":   str(_pick("smtp_password",   settings.smtp_password)),
        "from_email": str(_pick("smtp_from_email", settings.smtp_from_email or settings.smtp_user)),
        "from_name":  str(_pick("smtp_from_name",  settings.smtp_from_name)),
        "tls":        str(_pick("smtp_tls",        settings.smtp_tls)).lower() in ("1", "true"),
        "ssl":        str(_pick("smtp_ssl",        settings.smtp_ssl)).lower() in ("1", "true"),
    }


def send_email(to_email: str, subject: str, html_body: str, text_body: str = "") -> tuple[bool, str]:
    """Send an email via SMTP.

    Returns (success: bool, message: str).
    Falls back gracefully — never raises; all errors are logged and returned.
    """
    cfg = _get_smtp_config()

    if not cfg["user"] or not cfg["password"]:
        msg = "SMTP is not configured. Update SMTP settings in Admin > Settings > Notifications."
        logger.warning(msg)
        return False, msg

    if not to_email or "@" not in to_email:
        return False, "Invalid recipient email address."

    from_addr = f"{cfg['from_name']} <{cfg['from_email']}>" if cfg["from_name"] else cfg["from_email"]

    mime_msg = MIMEMultipart("alternative")
    mime_msg["Subject"] = subject
    mime_msg["From"]    = from_addr
    mime_msg["To"]      = to_email

    if text_body:
        mime_msg.attach(MIMEText(text_body, "plain", "utf-8"))
    mime_msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        if cfg["ssl"]:
            with smtplib.SMTP_SSL(cfg["host"], cfg["port"], timeout=15) as server:
                server.login(cfg["user"], cfg["password"])
                server.sendmail(cfg["from_email"], [to_email], mime_msg.as_string())
        else:
            with smtplib.SMTP(cfg["host"], cfg["port"], timeout=15) as server:
                server.ehlo()
                if cfg["tls"]:
                    server.starttls()
                    server.ehlo()
                server.login(cfg["user"], cfg["password"])
                server.sendmail(cfg["from_email"], [to_email], mime_msg.as_string())

        logger.info("Email sent to %s: %s", to_email, subject)
        return True, f"Email sent successfully to {to_email}."

    except smtplib.SMTPAuthenticationError:
        msg = "SMTP authentication failed. Check your email and app password in Notifications settings."
        logger.error(msg)
        return False, msg
    except smtplib.SMTPConnectError as e:
        msg = f"Cannot connect to SMTP server ({cfg['host']}:{cfg['port']}). {e}"
        logger.error(msg)
        return False, msg
    except Exception as e:
        msg = f"Email delivery failed: {e}"
        logger.error(msg)
        return False, msg


def send_password_reset_email(to_email: str, sister_name: str, reset_url: str) -> tuple[bool, str]:
    """Send the password recovery email to a sister co-owner."""
    subject = "SJ Interiors Admin — Password Reset Request"

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:Arial,Helvetica,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f5;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#6b1d49,#9d2466);padding:32px 40px;text-align:center;">
              <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:700;letter-spacing:-0.5px;">SJ Interiors</h1>
              <p style="margin:6px 0 0;color:rgba(255,255,255,0.8);font-size:13px;">Deco &amp; Beddings — Admin Portal</p>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:36px 40px;">
              <p style="margin:0 0 16px;font-size:15px;color:#374151;">Hello <strong>{sister_name}</strong>,</p>
              <p style="margin:0 0 24px;font-size:15px;color:#374151;line-height:1.6;">
                We received a request to reset the password for your SJ Interiors Admin account.
                Click the button below to set a new password. This link is valid for <strong>60 minutes</strong>.
              </p>
              <table cellpadding="0" cellspacing="0" style="margin:0 auto 28px;">
                <tr>
                  <td style="background:#6b1d49;border-radius:8px;text-align:center;">
                    <a href="{reset_url}" style="display:inline-block;padding:14px 32px;color:#ffffff;font-weight:700;font-size:15px;text-decoration:none;letter-spacing:0.3px;">
                      Reset My Password
                    </a>
                  </td>
                </tr>
              </table>
              <p style="margin:0 0 8px;font-size:13px;color:#6b7280;">Or copy this link into your browser:</p>
              <p style="margin:0 0 28px;font-size:12px;color:#9ca3af;word-break:break-all;">{reset_url}</p>
              <hr style="border:none;border-top:1px solid #e5e7eb;margin:0 0 20px;">
              <p style="margin:0;font-size:13px;color:#9ca3af;line-height:1.6;">
                If you did not request this, you can safely ignore this email.
                Your password will not change unless you click the link above.<br><br>
                — The SJ Interiors System
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background:#f9fafb;padding:20px 40px;text-align:center;border-top:1px solid #e5e7eb;">
              <p style="margin:0;font-size:12px;color:#9ca3af;">
                SJ Interior Deco &amp; Beddings · Limca Junction, Asa Dam Road, Ilorin, Kwara State
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    text_body = (
        f"Hello {sister_name},\n\n"
        f"Click the link below to reset your SJ Interiors Admin password (valid 60 minutes):\n\n"
        f"{reset_url}\n\n"
        f"If you did not request this, ignore this email.\n\n"
        f"— SJ Interiors System"
    )

    return send_email(to_email, subject, html_body, text_body)

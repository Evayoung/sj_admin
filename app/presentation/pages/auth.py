"""Authentication presentation pages — Login, Forgot Password, and Reset Password."""

from __future__ import annotations

from fasthtml.common import A, Button, Div, Form, H1, Input, Label, P, Small, Span, Title
from faststrap import Icon

from app.presentation.page_helpers import status_alert


def login_page(next_path: str = "/", error: str = "", success: str = "") -> tuple:
    """Render the 2-sister login page."""
    error_div = status_alert(error) if error else ""
    success_div = Div(
        Div(Icon("check-circle-fill", cls="me-2 text-success"), Span(success), cls="d-flex align-items-center"),
        cls="alert alert-success py-2 small mb-3",
    ) if success else ""

    return (
        Title("Sign In | SJ Interiors Admin"),
        Div(
            Div(
                Div(
                    Div(
                        Div("SJ", cls="admin-login-logo-letter"),
                        Div("Interiors", cls="admin-login-logo-letter admin-login-logo-letter-alt"),
                        cls="admin-login-logo",
                    ),
                    H1("Admin Dashboard", cls="admin-login-title"),
                    P("Sister Co-Owners & Store Management Portal", cls="admin-login-subtitle"),
                    error_div,
                    success_div,
                    Form(
                        Div(
                            Label("Email or Username", fr="login-username", cls="form-label small fw-semibold"),
                            Input(
                                type="text",
                                name="username",
                                id="login-username",
                                required=True,
                                autofocus=True,
                                cls="form-control",
                                placeholder="e.g. fatima@sjinteriors.com or fatima",
                            ),
                            cls="mb-3",
                        ),
                        Div(
                            Div(
                                Label("Password", fr="login-password", cls="form-label small fw-semibold mb-0"),
                                A("Forgot password?", href="/forgot-password", cls="small text-primary text-decoration-none"),
                                cls="d-flex justify-content-between align-items-center mb-1",
                            ),
                            Input(
                                type="password",
                                name="password",
                                id="login-password",
                                required=True,
                                cls="form-control",
                                placeholder="Enter your password",
                            ),
                            cls="mb-4",
                        ),
                        Input(type="hidden", name="next_path", value=next_path),
                        Button(
                            "Sign In",
                            type="submit",
                            cls="btn btn-primary w-100 py-2 fw-semibold",
                        ),
                        action="/login",
                        method="post",
                        cls="admin-login-form",
                    ),
                    cls="admin-login-card",
                ),
                cls="admin-login-wrap",
            ),
            cls="admin-login-page",
        ),
    )


def forgot_password_page(error: str = "", success: str = "", reset_link: str = "") -> tuple:
    """Render password recovery request page."""
    error_div = status_alert(error) if error else ""
    success_div = Div(
        Div(Icon("check-circle-fill", cls="me-2 text-success"), Span(success), cls="d-flex align-items-center"),
        cls="alert alert-success py-2 small mb-3",
    ) if success else ""

    direct_link_box = Div(
        P(Icon("key-fill", cls="me-2 text-primary"), "Direct Recovery Access (Development Mode):", cls="fw-bold small mb-1"),
        P("Click below to proceed to your password reset screen:", cls="small text-muted mb-2"),
        A(
            "Set New Password Now →",
            href=reset_link,
            cls="btn btn-outline-primary btn-sm fw-semibold w-100",
        ),
        cls="p-3 bg-light rounded-3 border mb-3",
    ) if reset_link else ""

    return (
        Title("Recover Password | SJ Interiors Admin"),
        Div(
            Div(
                Div(
                    Div(
                        Div("SJ", cls="admin-login-logo-letter"),
                        Div("Interiors", cls="admin-login-logo-letter admin-login-logo-letter-alt"),
                        cls="admin-login-logo",
                    ),
                    H1("Password Recovery", cls="admin-login-title"),
                    P("Enter your registered personal email address", cls="admin-login-subtitle"),
                    error_div,
                    success_div,
                    direct_link_box,
                    Form(
                        Div(
                            Label("Personal Administrator Email", fr="reset-email", cls="form-label small fw-semibold"),
                            Input(
                                type="email",
                                name="email",
                                id="reset-email",
                                required=True,
                                autofocus=True,
                                cls="form-control",
                                placeholder="e.g. fatima@sjinteriors.com",
                            ),
                            cls="mb-3",
                        ),
                        Button(
                            Icon("envelope", cls="me-2"), "Send Reset Link",
                            type="submit",
                            cls="btn btn-primary w-100 py-2 fw-semibold mb-3",
                        ),
                        Div(
                            A("← Back to Sign In", href="/login", cls="small text-secondary text-decoration-none fw-medium"),
                            cls="text-center",
                        ),
                        action="/forgot-password",
                        method="post",
                    ) if not reset_link else Div(
                        Div(
                            A("← Back to Sign In", href="/login", cls="small text-secondary text-decoration-none fw-medium"),
                            cls="text-center",
                        ),
                    ),
                    cls="admin-login-card",
                ),
                cls="admin-login-wrap",
            ),
            cls="admin-login-page",
        ),
    )


def reset_password_page(token: str, error: str = "", user_name: str = "") -> tuple:
    """Render password creation page with token."""
    error_div = status_alert(error) if error else ""

    return (
        Title("Set New Password | SJ Interiors Admin"),
        Div(
            Div(
                Div(
                    Div(
                        Div("SJ", cls="admin-login-logo-letter"),
                        Div("Interiors", cls="admin-login-logo-letter admin-login-logo-letter-alt"),
                        cls="admin-login-logo",
                    ),
                    H1("Set New Password", cls="admin-login-title"),
                    P(f"Reset credentials for {user_name or 'Account'}", cls="admin-login-subtitle"),
                    error_div,
                    Form(
                        Input(type="hidden", name="token", value=token),
                        Div(
                            Label("New Password (min 8 characters)", fr="new-password", cls="form-label small fw-semibold"),
                            Input(
                                type="password",
                                name="new_password",
                                id="new-password",
                                required=True,
                                minlength="8",
                                autofocus=True,
                                cls="form-control",
                                placeholder="Enter at least 8 characters",
                            ),
                            cls="mb-3",
                        ),
                        Div(
                            Label("Confirm New Password", fr="confirm-password", cls="form-label small fw-semibold"),
                            Input(
                                type="password",
                                name="confirm_password",
                                id="confirm-password",
                                required=True,
                                minlength="8",
                                cls="form-control",
                                placeholder="Re-enter your new password",
                            ),
                            cls="mb-4",
                        ),
                        Button(
                            Icon("shield-check", cls="me-2"), "Update Password & Sign In",
                            type="submit",
                            cls="btn btn-primary w-100 py-2 fw-semibold mb-3",
                        ),
                        Div(
                            A("← Cancel and Return to Sign In", href="/login", cls="small text-secondary text-decoration-none"),
                            cls="text-center",
                        ),
                        action="/reset-password",
                        method="post",
                    ),
                    cls="admin-login-card",
                ),
                cls="admin-login-wrap",
            ),
            cls="admin-login-page",
        ),
    )

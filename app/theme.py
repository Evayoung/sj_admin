"""Brand theme and component defaults for SJ Interiors Admin."""

from faststrap import create_theme, set_component_defaults

BRAND_COLORS = {
    "primary": "#6E45C9",
    "secondary": "#D8BC73",
    "accent": "#ECE7F5",
    "white": "#FFFFFF",
    "text": "#E8E0F5",
    "muted": "#B9AED4",
    "deep": "#1a1128",
}

SJ_ADMIN_THEME = create_theme(
    primary=BRAND_COLORS["primary"],
    secondary=BRAND_COLORS["secondary"],
    success="#6CD8A4",
    info="#7F9BFF",
    warning=BRAND_COLORS["secondary"],
    danger="#FF727E",
    light="#F4F8FB",
    dark=BRAND_COLORS["deep"],
)


def setup_theme_defaults() -> None:
    """Apply shared Faststrap defaults for the admin."""
    set_component_defaults("Button", variant="primary", size="md")
    set_component_defaults("Card", cls="border-0 shadow-sm")
    set_component_defaults("Badge", pill=True)
    set_component_defaults("Input", size="md")
    set_component_defaults("Alert", dismissible=True)

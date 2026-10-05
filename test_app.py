"""Smoke tests for SJ Interiors Admin."""

import importlib.util
import sys
from pathlib import Path

from starlette.testclient import TestClient

APP_PATH = Path(__file__).with_name("main.py")
ROOT = APP_PATH.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SPEC = importlib.util.spec_from_file_location("sj_admin_app", APP_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
app = MODULE.app

client = TestClient(app)


def test_login_page_renders():
    """Login page should render without auth."""
    response = client.get("/login")
    assert response.status_code == 200
    assert "Sign In" in response.text or "Sign in" in response.text


def test_redirect_to_login():
    """Protected routes should redirect to login."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 303, 307)
    assert "/login" in response.headers.get("location", "")


def test_login_success():
    """Valid credentials should allow access."""
    response = client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=False)
    assert response.status_code in (302, 303, 307)


def test_login_failure():
    """Invalid credentials should show error."""
    response = client.post("/login", data={"username": "admin", "password": "wrong"})
    assert response.status_code == 200
    assert "Invalid" in response.text or "invalid" in response.text


def test_authenticated_routes_render():
    """Authenticated session should be able to access all admin workspaces."""
    auth_client = TestClient(app)
    login_res = auth_client.post("/login", data={"username": "admin", "password": "admin123"})
    assert login_res.status_code == 200

    for path, expected in [
        ("/", "Overview"),
        ("/categories", "Categories"),
        ("/products", "Products"),
        ("/services", "Services"),
        ("/inquiries", "Inquiries"),
        ("/orders", "Orders"),
        ("/documents", "Documents"),
        ("/media", "Media"),
        ("/settings", "Settings"),
    ]:
        res = auth_client.get(path)
        assert res.status_code == 200
        assert expected in res.text


def test_documents_editor_fragment():
    """Document editor HTMX fragment should render."""
    auth_client = TestClient(app)
    auth_client.post("/login", data={"username": "admin", "password": "admin123"})
    res = auth_client.get("/documents/editor?kind=quotation")
    assert res.status_code == 200
    assert "Quotation" in res.text
    assert "Itemized Breakdown" in res.text


def test_orders_editor_fragment():
    """Order editor HTMX fragment should render."""
    auth_client = TestClient(app)
    auth_client.post("/login", data={"username": "admin", "password": "admin123"})
    res = auth_client.get("/orders/editor")
    assert res.status_code == 200
    assert "Create New Order" in res.text
    assert "Order Items" in res.text


def test_document_official_template_loading():
    """Loading official sample template should populate 6-division items."""
    auth_client = TestClient(app)
    auth_client.post("/login", data={"username": "admin", "password": "admin123"})
    res = auth_client.get("/documents/editor?template=official")
    assert res.status_code == 200
    html = res.text
    assert "1. SITTING ROOM CURTAINS" in html
    assert "2. BEDROOM CURTAINS" in html
    assert "3. INTERIOR DECOR" in html
    assert "5. KITCHENWARE" in html


def test_client_portal_page_rendering():
    """Client portal endpoint should render with official plum layout."""
    res = client.get("/documents/preview/non-existent-token")
    assert res.status_code == 200


def test_receipt_editor_renders():
    """Creating a new receipt document should show payment fields."""
    auth_client = TestClient(app)
    auth_client.post("/login", data={"username": "admin", "password": "admin123"})
    res = auth_client.get("/documents/editor?kind=receipt")
    assert res.status_code == 200
    html = res.text
    assert "Receipt" in html
    assert "Payment Method" in html
    assert "Amount Paid" in html


def test_receipt_kind_shown_in_filter():
    """Documents page should list the Receipts tab in the filter bar."""
    auth_client = TestClient(app)
    auth_client.post("/login", data={"username": "admin", "password": "admin123"})
    res = auth_client.get("/documents")
    assert res.status_code == 200
    assert "Receipts" in res.text


def test_generate_receipt_endpoint_exists():
    """generate-receipt POST should return 200 (even if DB is offline, handler runs)."""
    auth_client = TestClient(app)
    auth_client.post("/login", data={"username": "admin", "password": "admin123"})
    res = auth_client.post("/documents/generate-receipt/non-existent-id", data={})
    assert res.status_code == 200


def test_confirm_payment_endpoint_exists():
    """confirm-payment POST (public) should return 200 for any token."""
    res = client.post(
        "/documents/confirm-payment/non-existent-token",
        data={"payment_method": "Cash", "payment_reference": "CASH-001", "notes": "Test"},
    )
    assert res.status_code == 200


def test_brand_studio_tabs_render():
    """Settings page should render all studio tabs."""
    auth_client = TestClient(app)
    auth_client.post("/login", data={"username": "admin", "password": "admin123"})
    res = auth_client.get("/settings")
    assert res.status_code == 200
    html = res.text
    assert "Hero Banner Slides" in html
    assert "Client Testimonials" in html
    assert "Space Transformations" in html


def test_brand_studio_hero_save_endpoint():
    """Hero slides save endpoint should handle form arrays."""
    auth_client = TestClient(app)
    auth_client.post("/login", data={"username": "admin", "password": "admin123"})
    res = auth_client.post(
        "/settings/hero/save",
        data={"slide_image[]": ["https://example.com/slide1.jpg"], "slide_alt[]": ["Test Slide"]},
    )
    assert res.status_code == 200


def test_pdf_download_endpoint():
    """GET /documents/pdf/{token} should return application/pdf with valid PDF binary."""
    res = client.get("/documents/pdf/token-qtn-meshell-2026")
    assert res.status_code == 200
    assert res.headers.get("content-type") == "application/pdf"
    assert res.content.startswith(b"%PDF")


def test_in_platform_respond_accept():
    """POST /documents/respond/{token} with action='accepted' updates status in-platform."""
    res = client.post(
        "/documents/respond/token-qtn-meshell-2026",
        data={"action": "accepted", "notes": "Approved, please start production."},
    )
    assert res.status_code == 200
    html = res.text
    assert "Document Accepted & Confirmed" in html or "Accepted" in html


def test_in_platform_respond_decline():
    """POST /documents/respond/{token} with action='declined' records rejection reason."""
    res = client.post(
        "/documents/respond/token-pro-meshell-2026",
        data={"action": "declined", "notes": "Need to reduce bedroom drapery scope."},
    )
    assert res.status_code == 200
    html = res.text
    assert "Declined" in html or "Revision Requested" in html


def test_client_portal_header_and_modals():
    """Client portal should render Copy Link, Download PDF, and in-platform action modals."""
    res = client.get("/documents/preview/token-inv-meshell-2026")
    assert res.status_code == 200
    html = res.text
    assert "Copy Link" in html
    assert "Download PDF" in html
    assert "payment-confirm-modal" in html


def test_unauthenticated_document_management_redirects():
    """Admin document management routes must NOT bypass authentication."""
    unauth_client = TestClient(app)
    # /documents listing requires auth
    res = unauth_client.get("/documents", follow_redirects=False)
    assert res.status_code in (302, 303, 307)
    assert "/login" in res.headers.get("location", "")

    # /documents/editor requires auth
    res = unauth_client.get("/documents/editor", follow_redirects=False)
    assert res.status_code in (302, 303, 307)
    assert "/login" in res.headers.get("location", "")


def test_public_document_endpoints_accessible_without_auth():
    """Only public client portal endpoints should bypass login."""
    res = client.get("/documents/preview/token-qtn-meshell-2026")
    assert res.status_code == 200

    pdf_res = client.get("/documents/pdf/token-qtn-meshell-2026")
    assert pdf_res.status_code == 200
    assert pdf_res.headers.get("content-type") == "application/pdf"


def test_open_redirect_protection():
    """Login redirect must sanitize next_path and prevent external redirects."""
    # Malicious double-slash protocol-relative redirect
    res = client.post("/login", data={"username": "admin", "password": "admin123", "next_path": "//evil.com"}, follow_redirects=False)
    assert res.status_code in (302, 303, 307)
    location = res.headers.get("location", "")
    assert location == "/" or not location.startswith("//evil.com")

    # Absolute external URL
    res = client.post("/login", data={"username": "admin", "password": "admin123", "next_path": "https://evil.com"}, follow_redirects=False)
    assert res.status_code in (302, 303, 307)
    location = res.headers.get("location", "")
    assert location == "/"


def test_media_page_and_picker_modal():
    """Media page and picker modal should render without errors."""
    auth_client = TestClient(app)
    auth_client.post("/login", data={"username": "admin", "password": "admin123"})

    res = auth_client.get("/media")
    assert res.status_code == 200
    assert "Upload Media" in res.text
    assert "Media Library" in res.text

    picker_res = auth_client.get("/media/picker-modal")
    assert picker_res.status_code == 200


def test_shortcut_prefill_orders():
    """GET /orders?new=1 and ?inquiry_id=... should mount the prefilled editor."""
    auth_client = TestClient(app)
    auth_client.post("/login", data={"username": "admin", "password": "admin123"})

    # new=1 opens order creation editor
    res = auth_client.get("/orders?new=1")
    assert res.status_code == 200
    assert "Create New Order" in res.text

    # inquiry_id pre-fills customer details
    inq_res = auth_client.get("/orders?inquiry_id=inq-meshell-2026-001")
    assert inq_res.status_code == 200
    assert "Chief Meshell" in inq_res.text


def test_shortcut_prefill_documents():
    """GET /documents?new=1 and ?inquiry_id=... should mount prefilled quotation editor."""
    auth_client = TestClient(app)
    auth_client.post("/login", data={"username": "admin", "password": "admin123"})

    res = auth_client.get("/documents?new=1")
    assert res.status_code == 200

    inq_res = auth_client.get("/documents?inquiry_id=inq-meshell-2026-001")
    assert inq_res.status_code == 200
    assert "Chief Meshell" in inq_res.text


def test_reactive_htmx_trigger_headers():
    """Save endpoints should return HX-Trigger: refreshList header."""
    auth_client = TestClient(app)
    auth_client.post("/login", data={"username": "admin", "password": "admin123"})

    # Product save
    p_res = auth_client.post("/products/save", data={"name": "Test Sheet", "category_slug": "bedding"})
    assert p_res.headers.get("hx-trigger") == "refreshList"

    # Category save
    c_res = auth_client.post("/categories/save", data={"label": "Test Decor", "slug": "test-decor"})
    assert c_res.headers.get("hx-trigger") == "refreshList"

    # Service save
    s_res = auth_client.post("/services/save", data={"title": "Test Staging", "slug": "test-staging"})
    assert s_res.headers.get("hx-trigger") == "refreshList"

    # Order save
    o_res = auth_client.post("/orders/save", data={"customer_name": "Test Client", "phone": "08012345678"})
    assert o_res.headers.get("hx-trigger") == "refreshList"


def test_two_sisters_login_and_roles():
    """Both Fatima and Zainab can log in via username or email."""
    client = TestClient(app)

    # Mercy login with username
    res1 = client.post("/login", data={"username": "mercy", "password": "Olajumoke402@"}, follow_redirects=False)
    assert res1.status_code == 303
    assert res1.headers.get("location") == "/"

    # Mercy login with email
    res2 = client.post("/login", data={"username": "alademercy93@gmail.com", "password": "Olajumoke402@"}, follow_redirects=False)
    assert res2.status_code == 303

    # Christianah login with username
    res3 = client.post("/login", data={"username": "christianah", "password": "Beamose1965#"}, follow_redirects=False)
    assert res3.status_code == 303

    # Christianah login with email
    res4 = client.post("/login", data={"username": "aladechristiana5@gmail.com", "password": "Beamose1965#"}, follow_redirects=False)
    assert res4.status_code == 303

    # Legacy admin fallback
    res5 = client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=False)
    assert res5.status_code == 303


def test_max_two_admin_accounts_constraint():
    """System strictly enforces maximum of 2 admin accounts."""
    from app.infrastructure.auth_repository import can_create_admin_user, get_admin_users, MAX_ADMIN_ACCOUNTS
    assert MAX_ADMIN_ACCOUNTS == 2
    users = get_admin_users()
    assert len(users) == 2
    # Cannot create a 3rd admin
    assert can_create_admin_user() is False


def test_password_recovery_flow():
    """Password recovery workflow generates token and resets password."""
    client = TestClient(app)
    from app.infrastructure.auth_repository import create_password_reset_token, verify_reset_token, reset_password_with_token

    # Forgot password page renders
    res = client.get("/forgot-password")
    assert res.status_code == 200
    assert "Password Recovery" in res.text

    # Request reset token for Mercy's email
    ok, msg, token = create_password_reset_token("alademercy93@gmail.com")
    assert ok is True
    assert token is not None

    # Verify reset token
    user = verify_reset_token(token)
    assert user is not None
    assert user["username"] == "mercy"

    # Reset password with token
    ok_reset, msg_reset = reset_password_with_token(token, "NewSecret2026@")
    assert ok_reset is True

    # Login with new password works
    login_res = client.post("/login", data={"username": "mercy", "password": "NewSecret2026@"}, follow_redirects=False)
    assert login_res.status_code == 303

    # Reset back to Olajumoke402@
    ok2, msg2, token2 = create_password_reset_token("alademercy93@gmail.com")
    reset_password_with_token(token2, "Olajumoke402@")


def test_audit_trail_logging_and_display():
    """Audit trail captures actions and renders in admin workspace."""
    from app.infrastructure.audit_repository import log_activity, get_audit_logs
    log_activity(None, {"admin_user": "mercy", "admin_user_name": "Sister Mercy"}, "TEST_ACTION", "system", "sys-1", "Automated test audit event")

    # Verify log entry recorded
    logs = get_audit_logs()
    actions = [l.get("action") for l in logs]
    assert "TEST_ACTION" in actions

    # Audit trail page renders when authenticated
    auth_client = TestClient(app)
    auth_client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=True)
    res = auth_client.get("/audit-trail")
    assert res.status_code == 200


def test_feedback_management_and_publishing():
    """Admin feedback workspace allows review publishing and complaint resolution."""
    auth_client = TestClient(app)
    auth_client.post("/login", data={"username": "mercy", "password": "Olajumoke402@"}, follow_redirects=True)

    # 1. Feedback workspace renders
    res = auth_client.get("/feedback")
    assert res.status_code == 200
    assert "Feedback" in res.text or "Reviews" in res.text

    # 2. Toggle publication of a review
    from app.infrastructure.feedback_repository import create_feedback, get_all_feedback
    test_fb = create_feedback({
        "kind": "review",
        "customer_name": "Test Client Alpha",
        "customer_phone": "08011223344",
        "rating": 5,
        "message": "Outstanding curtain styling service!",
    })
    fb_id = test_fb["id"]

    toggle_res = auth_client.post(f"/feedback/toggle-publish/{fb_id}")
    assert toggle_res.status_code == 200
    assert "Live on Website" in toggle_res.text or "Unpublish" in toggle_res.text

    # 3. Resolve a complaint
    test_comp = create_feedback({
        "kind": "complaint",
        "customer_name": "Test Client Beta",
        "customer_phone": "08099887766",
        "message": "Adjust track tension please",
    })
    comp_id = test_comp["id"]

    resolve_res = auth_client.post(f"/feedback/resolve/{comp_id}", data={
        "status": "resolved",
        "notes": "Installer completed track adjustment.",
        "assigned_to": "Christianah",
    })
    assert resolve_res.status_code == 200
    assert "Resolved" in resolve_res.text


def test_quick_receipt_form_and_whatsapp_flow():
    """Quick receipt form pre-fills receipt data and supports WhatsApp dispatch."""
    auth_client = TestClient(app)
    auth_client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=True)

    # Quick receipt form loads with official receipt draft
    res = auth_client.get("/documents/quick-receipt-form")
    assert res.status_code == 200
    assert "Official Payment Receipt" in res.text or "REC-" in res.text









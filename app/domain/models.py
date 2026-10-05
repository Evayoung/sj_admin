"""Domain models for SJ Interiors Admin."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AdminUser:
    id: str
    username: str
    full_name: str
    is_active: bool


@dataclass(frozen=True)
class Category:
    id: str
    slug: str
    label: str
    description: str
    icon: str
    image_url: str
    sort_order: int
    is_active: bool


@dataclass(frozen=True)
class Product:
    id: str
    name: str
    slug: str
    category_slug: str
    description: str
    price: str
    highlight: str
    image_url: str
    images: list
    stock_status: str
    is_featured: bool
    is_active: bool


@dataclass(frozen=True)
class Service:
    id: str
    title: str
    slug: str
    summary: str
    description: str
    icon: str
    image_url: str
    is_active: bool
    sort_order: int


@dataclass(frozen=True)
class Inquiry:
    id: str
    customer_name: str
    phone: str
    email: str
    message: str
    source: str
    status: str
    service_inquiry: bool
    selected_services: list | None


@dataclass(frozen=True)
class Order:
    id: str
    order_number: str
    customer_name: str
    phone: str
    items: list
    status: str
    notes: str


@dataclass(frozen=True)
class Document:
    id: str
    kind: str
    document_number: str
    customer_name: str
    customer_phone: str
    customer_email: str
    title: str
    subtitle: str
    notes: str
    terms: str
    status: str
    total_amount: float
    currency: str
    access_token: str
    view_count: int = 0
    viewed_at: str | None = None
    client_decision: str | None = None  # 'accepted', 'rejected', 'revision_requested'
    client_decision_at: str | None = None
    client_notes: str | None = None
    comments: list | None = None
    amount_paid: float = 0.0
    balance_due: float = 0.0
    payment_method: str = "Bank Transfer"
    payment_reference: str = ""
    payment_date: str | None = None
    related_invoice_id: str | None = None
    payment_claimed: bool = False


@dataclass(frozen=True)
class DocumentItem:
    id: str
    document_id: str
    description: str
    quantity: float
    unit_price: float
    total: float
    sort_order: int
    category_group: str = ""
    specification: str = ""
    unit_label: str = ""


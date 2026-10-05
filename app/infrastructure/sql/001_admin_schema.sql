-- ============================================================================
-- SJ INTERIORS & SJ ADMIN — MASTER SUPABASE DATABASE SCHEMA
-- ============================================================================

create extension if not exists "pgcrypto";

-- ────────────────────────────────────────────────────────────────────────────
-- 1. ENUMS & TYPES
-- ────────────────────────────────────────────────────────────────────────────

do $$ begin
    create type order_status as enum ('processing', 'shipped', 'delivered', 'cancelled');
exception when duplicate_object then null;
end $$;

do $$ begin
    create type inquiry_status as enum ('new', 'contacted', 'ordered', 'closed');
exception when duplicate_object then null;
end $$;

do $$ begin
    create type stock_status as enum ('in_stock', 'made_to_order', 'discontinued');
exception when duplicate_object then null;
end $$;

do $$ begin
    create type inquiry_source as enum ('whatsapp', 'contact_form', 'phone', 'services_page');
exception when duplicate_object then null;
end $$;

do $$ begin
    create type document_kind as enum ('proposal', 'quotation', 'invoice', 'receipt');
exception when duplicate_object then null;
end $$;

do $$ begin
    create type document_status as enum (
        'draft', 'sent', 'viewed', 'accepted', 'declined', 
        'payment_pending', 'partially_paid', 'paid', 'expired'
    );
exception when duplicate_object then null;
end $$;

-- ────────────────────────────────────────────────────────────────────────────
-- 2. CORE TABLES
-- ────────────────────────────────────────────────────────────────────────────

-- Brand Configuration (Global dynamic site settings, hero slides, testimonials, etc.)
create table if not exists brand_config (
    id uuid primary key default gen_random_uuid(),
    key text unique not null,
    value jsonb not null,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Categories
create table if not exists categories (
    id uuid primary key default gen_random_uuid(),
    slug text unique not null,
    label text not null,
    description text,
    icon text,
    image_url text,
    sort_order int default 0,
    is_active boolean default true,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Products Catalog
create table if not exists products (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    slug text unique not null,
    category_slug text references categories(slug) on update cascade on delete set null,
    description text,
    price text,
    highlight text,
    image_url text,
    images jsonb default '[]'::jsonb,
    stock_status stock_status default 'in_stock',
    is_featured boolean default false,
    is_active boolean default true,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Services (6 Core Divisions)
create table if not exists services (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    slug text unique not null,
    summary text,
    description text,
    icon text,
    image_url text,
    sort_order int default 0,
    is_active boolean default true,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Inquiries & Service Leads
create table if not exists inquiries (
    id uuid primary key default gen_random_uuid(),
    product_id uuid,
    service_inquiry boolean default false,
    customer_name text,
    phone text,
    email text,
    message text,
    source inquiry_source default 'contact_form',
    selected_services jsonb default '[]'::jsonb,
    status inquiry_status default 'new',
    notes text,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Orders (Customer Order Lookup & Fulfillment)
create table if not exists orders (
    id uuid primary key default gen_random_uuid(),
    inquiry_id uuid references inquiries(id) on delete set null,
    order_number text unique not null,
    customer_name text not null,
    phone text,
    items jsonb default '[]'::jsonb,
    total_amount numeric(12,2) default 0,
    status order_status default 'processing',
    notes text,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Documents (Proposals, Quotations, Invoices, Receipts)
create table if not exists documents (
    id uuid primary key default gen_random_uuid(),
    kind document_kind not null,
    document_number text unique not null,
    inquiry_id uuid references inquiries(id) on delete set null,
    customer_name text not null,
    customer_phone text,
    customer_email text,
    title text not null,
    subtitle text,
    notes text,
    terms text,
    status document_status default 'draft',
    valid_until date,
    total_amount numeric(12,2) default 0,
    amount_paid numeric(12,2) default 0,
    balance_due numeric(12,2) default 0,
    currency text default 'NGN',
    payment_method text,
    payment_reference text,
    payment_date text,
    related_invoice_id uuid references documents(id) on delete set null,
    payment_claimed boolean default false,
    access_token text unique default gen_random_uuid()::text,
    view_count int default 0,
    viewed_at timestamptz,
    client_decision text,
    client_decision_at timestamptz,
    client_notes text,
    comments jsonb default '[]'::jsonb,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Document Line Items (Categorized with Specifications)
create table if not exists document_items (
    id uuid primary key default gen_random_uuid(),
    document_id uuid references documents(id) on delete cascade not null,
    category_group text default '1. GENERAL FURNISHING & SERVICES',
    description text not null,
    specification text,
    quantity numeric(10,2) default 1,
    unit_price numeric(12,2) not null,
    unit_label text,
    sort_order int default 0,
    created_at timestamptz default now()
);

-- Admin Users (For Backend Authentication)
create table if not exists admin_users (
    id uuid primary key default gen_random_uuid(),
    username text unique not null,
    password_hash text not null,
    full_name text,
    is_active boolean default true,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ────────────────────────────────────────────────────────────────────────────
-- 3. INDEXES FOR PERFORMANCE
-- ────────────────────────────────────────────────────────────────────────────

create index if not exists idx_brand_config_key on brand_config(key);
create index if not exists idx_categories_slug on categories(slug);
create index if not exists idx_categories_active on categories(is_active);
create index if not exists idx_products_category on products(category_slug);
create index if not exists idx_products_slug on products(slug);
create index if not exists idx_products_featured on products(is_featured) where is_active = true;
create index if not exists idx_products_active on products(is_active);
create index if not exists idx_services_active on services(is_active) where is_active = true;
create index if not exists idx_inquiries_status on inquiries(status);
create index if not exists idx_orders_number on orders(order_number);
create index if not exists idx_orders_status on orders(status);
create index if not exists idx_documents_number on documents(document_number);
create index if not exists idx_documents_token on documents(access_token);
create index if not exists idx_documents_status on documents(status);
create index if not exists idx_documents_kind on documents(kind);
create index if not exists idx_document_items_doc on document_items(document_id);

-- ────────────────────────────────────────────────────────────────────────────
-- 4. ROW-LEVEL SECURITY (RLS) POLICIES
-- ────────────────────────────────────────────────────────────────────────────

alter table brand_config enable row level security;
alter table categories enable row level security;
alter table products enable row level security;
alter table services enable row level security;
alter table inquiries enable row level security;
alter table orders enable row level security;
alter table documents enable row level security;
alter table document_items enable row level security;
alter table admin_users enable row level security;

-- Public Read Policies (Anonymous website visitors - read-only)
create policy "Public read brand_config" on brand_config for select using (true);
create policy "Public read categories" on categories for select using (is_active = true);
create policy "Public read products" on products for select using (is_active = true);
create policy "Public read services" on services for select using (is_active = true);
create policy "Public read orders" on orders for select using (true);
create policy "Public read documents" on documents for select using (true);
create policy "Public read document_items" on document_items for select using (true);

-- Anonymous Contact Form & Lead Submissions
create policy "Public insert inquiries" on inquiries for insert with check (true);

-- Service Role Full Access (Admin backend operations)
create policy "Service full brand_config" on brand_config for all using (auth.role() = 'service_role');
create policy "Service full categories" on categories for all using (auth.role() = 'service_role');
create policy "Service full products" on products for all using (auth.role() = 'service_role');
create policy "Service full services" on services for all using (auth.role() = 'service_role');
create policy "Service full inquiries" on inquiries for all using (auth.role() = 'service_role');
create policy "Service full orders" on orders for all using (auth.role() = 'service_role');
create policy "Service full documents" on documents for all using (auth.role() = 'service_role');
create policy "Service full document_items" on document_items for all using (auth.role() = 'service_role');
create policy "Service full admin_users" on admin_users for all using (auth.role() = 'service_role');


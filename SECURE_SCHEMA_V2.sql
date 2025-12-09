-- =============================================
-- SECURE CONTACT INTELLIGENCE SCHEMA v2.0
-- Author: Super Brain Architect
-- Features: RLS, Encryption-ready, Vector Search
-- =============================================

-- 1. EXTENSIONS
-- Enable Vector search for RAG
create extension if not exists vector;
-- Enable Crypto for hashing/encryption utilities (if needed DB-side)
create extension if not exists pgcrypto;

-- 2. ENUMS & TYPES
create type sentiment_type as enum ('positive', 'negative', 'neutral', 'mixed', 'unknown');
create type urgency_type as enum ('low', 'medium', 'high', 'critical');
create type channel_type as enum ('telegram', 'whatsapp', 'email', 'voice', 'meeting');

-- 3. TABLES

-- CONTACTS (Enhanced Profile)
create table public.contacts (
    id uuid primary key default gen_random_uuid(),
    created_at timestamptz default now(),
    updated_at timestamptz default now(),
    
    -- Identity (Hashed for search if needed, or plain if risk is low)
    name text not null,
    telegram_id bigint unique,
    telegram_username text,
    
    -- Relationship Management
    trust_level int default 1 check (trust_level between 1 and 5),
    relationship_context text, -- "Met at conference X..."
    
    -- Style Mimicry Data
    communication_style jsonb default '{}'::jsonb, 
    -- e.g. {"avg_len": 15, "emoji_freq": 0.4, "tone": "casual"}
    
    -- Settings
    is_active boolean default true,
    auto_respond_enabled boolean default false
);

-- INTERACTIONS (The Secure Vault)
create table public.interactions (
    id uuid primary key default gen_random_uuid(),
    contact_id uuid references public.contacts(id) on delete cascade not null,
    timestamp timestamptz default now(),
    
    -- Metadata
    channel channel_type not null,
    direction text check (direction in ('incoming', 'outgoing')) not null,
    
    -- CONTENT (ENCRYPTED AT REST)
    -- This field contains the AES-256 encrypted base64 string
    -- Decryption happens ONLY in the FastAPI service, never in DB or n8n
    message_encrypted text not null,
    
    -- AI Memory (Embeddings)
    -- Generated from SANITIZED (PII-stripped) text
    embedding vector(1536),
    
    -- Analytics (Metadata is usually safe to keep unencrypted)
    sentiment sentiment_type,
    urgency urgency_type,
    token_count int,
    
    -- Search Optimization
    topics text[]
);

-- 4. INDEXES

-- Vector Search Index (IVFFlat for speed)
create index on interactions using ivfflat (embedding vector_cosine_ops)
with (lists = 100);

-- Standard Indexes
create index idx_interactions_contact on interactions(contact_id);
create index idx_interactions_ts on interactions(timestamp desc);

-- 5. ROW LEVEL SECURITY (RLS)
-- Mandatory: No public access ever.
alter table public.contacts enable row level security;
alter table public.interactions enable row level security;

-- Policy: Service Role (API) has full access
create policy "Service Role Full Access"
on public.contacts
for all
using ( auth.role() = 'service_role' );

create policy "Service Role Full Access Interactions"
on public.interactions
for all
using ( auth.role() = 'service_role' );

-- Policy: Authenticated Users (You) can read
create policy "User Read Access"
on public.contacts
for select
using ( auth.role() = 'authenticated' );

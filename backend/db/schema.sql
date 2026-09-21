-- Tech Advisor — Postgres schema
-- Requires: PostgreSQL 15+, pgvector, pgcrypto extensions

-- ---------------------------------------------------------------------------
-- Enums
-- ---------------------------------------------------------------------------

CREATE TYPE company_size AS ENUM (
    'solo',
    'small',       -- 1-10
    'medium',      -- 11-50
    'large',       -- 51-200
    'enterprise'   -- 200+
);

CREATE TYPE budget_range AS ENUM (
    'free',
    'under_100',
    '100_to_500',
    '500_to_2000',
    'enterprise'
);

CREATE TYPE technical_maturity AS ENUM (
    'non_technical',
    'low_code',
    'developer'
);

CREATE TYPE tool_category AS ENUM (
    'sales_marketing_ai',
    'customer_support_ai',
    'operations_workflow_ai',
    'analytics_forecasting_ai',
    'developer_ai',
    'general_automation'
);

CREATE TYPE session_status AS ENUM (
    'collecting',
    'clarifying',
    'recommending',
    'refining',
    'completed'
);

CREATE TYPE feedback_rating AS ENUM (
    'positive',
    'negative',
    'neutral'
);

-- ---------------------------------------------------------------------------
-- Catalog
-- ---------------------------------------------------------------------------

CREATE TABLE tools (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    vendor          TEXT NOT NULL,
    url             TEXT NOT NULL,
    description     TEXT NOT NULL,
    pricing_model   TEXT,                -- e.g. per_seat, usage_based, flat
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tool_pricing_tiers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_id         UUID NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
    tier_name       TEXT NOT NULL,
    price_monthly   NUMERIC(10, 2),      -- NULL if custom/enterprise
    price_currency  TEXT NOT NULL DEFAULT 'USD',
    per_seat        BOOLEAN NOT NULL DEFAULT FALSE,
    min_seats       INTEGER,
    max_seats       INTEGER,
    limits_summary  TEXT,
    company_size_fit company_size[],
    sort_order      INTEGER NOT NULL DEFAULT 0,
    UNIQUE (tool_id, tier_name)
);

CREATE TABLE tool_tags (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_id         UUID NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
    category        tool_category NOT NULL,
    industries      TEXT[] NOT NULL DEFAULT '{}',
    goals           TEXT[] NOT NULL DEFAULT '{}',
    integrations    TEXT[] NOT NULL DEFAULT '{}',
    company_sizes   company_size[] NOT NULL DEFAULT '{}',
    budget_fits     budget_range[] NOT NULL DEFAULT '{}',
    technical_maturity_fits technical_maturity[] NOT NULL DEFAULT '{}'
);

CREATE TABLE tool_pros_cons (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_id         UUID NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
    pros            TEXT[] NOT NULL DEFAULT '{}',
    cons            TEXT[] NOT NULL DEFAULT '{}'
);

CREATE TABLE tool_playbooks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_id         UUID NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
    implementation_steps JSONB NOT NULL DEFAULT '[]',
    -- Array of { "step": number, "title": string, "description": string }
    migration_notes JSONB NOT NULL DEFAULT '{}'
    -- Keyed by stack, e.g. { "salesforce": ["...", "..."] }
);

CREATE TABLE tool_embeddings (
    tool_id         UUID PRIMARY KEY REFERENCES tools(id) ON DELETE CASCADE,
    embedding       vector(384) NOT NULL,  -- match chosen model dimension
    model_name      TEXT NOT NULL,
    embedded_text   TEXT NOT NULL,           -- text that was embedded
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE catalog_sources (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_id         UUID NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
    field_name      TEXT NOT NULL,           -- e.g. pricing_tiers, pros
    source_url      TEXT NOT NULL,
    last_verified   DATE,
    notes           TEXT
);

CREATE INDEX idx_tools_active ON tools(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_tool_tags_category ON tool_tags(category);
-- Create after loading embeddings (ivfflat needs rows):
-- CREATE INDEX idx_tool_embeddings_vector ON tool_embeddings
--     USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ---------------------------------------------------------------------------
-- Sessions and recommendations
-- ---------------------------------------------------------------------------

CREATE TABLE sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status          session_status NOT NULL DEFAULT 'collecting',
    user_id         UUID,                  -- NULL until accounts (Phase 6)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE scenario_profiles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    industry        TEXT,
    company_size    company_size,
    budget_range    budget_range,
    technical_maturity technical_maturity,
    primary_goals   TEXT[] NOT NULL DEFAULT '{}',
    existing_stack  TEXT[] NOT NULL DEFAULT '{}',
    constraints     TEXT[] NOT NULL DEFAULT '{}',
    free_text_summary TEXT,
    embedding       vector(384),
    normalized_hash TEXT,                  -- for exact cache key
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE recommendations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    scenario_id     UUID NOT NULL REFERENCES scenario_profiles(id) ON DELETE CASCADE,
    ranked_tools    JSONB NOT NULL,
    -- Array of { "tool_id", "slug", "name", "score", "fit_reason" }
    report          JSONB NOT NULL,        -- AdvisoryReport JSON
    model_version   TEXT,
    cache_hit       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE recommendation_feedback (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recommendation_id   UUID NOT NULL REFERENCES recommendations(id) ON DELETE CASCADE,
    rating              feedback_rating,
    selected_tool_id    UUID REFERENCES tools(id) ON DELETE SET NULL,
    comment             TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_scenario_profiles_session ON scenario_profiles(session_id);
CREATE INDEX idx_recommendations_session ON recommendations(session_id);
CREATE INDEX idx_scenario_profiles_hash ON scenario_profiles(normalized_hash);

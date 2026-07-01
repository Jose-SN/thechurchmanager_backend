-- =====================================================
-- SERVICE ROTA TABLES - PostgreSQL Schema
-- =====================================================
-- Volunteer scheduling: services, availability, assignments,
-- attendance, clock sessions, and audit logs.
--
-- Run in Supabase SQL editor or psql after teams/organizations exist:
--   psql $DATABASE_URL -f app/scripts/create_service_rota_tables.sql
-- =====================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enums (idempotent)
DO $$ BEGIN
    CREATE TYPE service_status AS ENUM ('draft', 'published', 'completed', 'cancelled');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE availability_status AS ENUM (
        'available', 'available_all_day', 'unavailable', 'not_sure'
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE assignment_status AS ENUM ('assigned', 'confirmed', 'declined');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE attendance_status AS ENUM (
        'present', 'absent', 'late', 'replacement', 'pending'
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE clock_session_status AS ENUM ('clocked_in', 'completed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- 1. Services
CREATE TABLE IF NOT EXISTS rota_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    time VARCHAR(10) NOT NULL DEFAULT '10:00',
    location VARCHAR(255) NOT NULL DEFAULT '',
    description TEXT DEFAULT '',
    languages JSONB NOT NULL DEFAULT '["English"]'::jsonb,
    availability_options JSONB NOT NULL DEFAULT
        '["available","available_all_day","unavailable","not_sure"]'::jsonb,
    max_volunteers INTEGER,
    notes TEXT DEFAULT '',
    status service_status NOT NULL DEFAULT 'draft',
    team_id UUID,
    volunteer_count INTEGER NOT NULL DEFAULT 0,
    attendance_summary JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rota_services_org_date
    ON rota_services (organization_id, date);
CREATE INDEX IF NOT EXISTS idx_rota_services_org_status
    ON rota_services (organization_id, status);

-- 2. Availability
CREATE TABLE IF NOT EXISTS rota_availability (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    service_id UUID NOT NULL REFERENCES rota_services(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    team_id UUID,
    team_name VARCHAR(255),
    role VARCHAR(255),
    availability availability_status NOT NULL DEFAULT 'not_sure',
    comment TEXT DEFAULT '',
    comments JSONB NOT NULL DEFAULT '[]'::jsonb,
    updated_by_id UUID,
    updated_by_name VARCHAR(255),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (organization_id, service_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_rota_availability_org_service
    ON rota_availability (organization_id, service_id);
CREATE INDEX IF NOT EXISTS idx_rota_availability_user
    ON rota_availability (organization_id, user_id);

-- 3. Assignments
CREATE TABLE IF NOT EXISTS rota_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    service_id UUID NOT NULL REFERENCES rota_services(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    user_email VARCHAR(255),
    user_phone VARCHAR(50),
    team_id UUID NOT NULL,
    team_name VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    arrival_time VARCHAR(10),
    notes TEXT DEFAULT '',
    status assignment_status NOT NULL DEFAULT 'assigned',
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (organization_id, service_id, user_id, team_id)
);

CREATE INDEX IF NOT EXISTS idx_rota_assignments_service
    ON rota_assignments (organization_id, service_id);

-- 4. Attendance
CREATE TABLE IF NOT EXISTS rota_attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    service_id UUID NOT NULL REFERENCES rota_services(id) ON DELETE CASCADE,
    assignment_id UUID REFERENCES rota_assignments(id) ON DELETE SET NULL,
    user_id UUID NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    team_id UUID NOT NULL,
    team_name VARCHAR(255) NOT NULL,
    role VARCHAR(255),
    status attendance_status NOT NULL DEFAULT 'pending',
    check_in_time TIMESTAMPTZ,
    check_out_time TIMESTAMPTZ,
    notes TEXT DEFAULT '',
    replacement_user_id UUID,
    replacement_user_name VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (organization_id, service_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_rota_attendance_service
    ON rota_attendance (organization_id, service_id);

-- 5. Clock sessions (volunteer clock-in/out)
CREATE TABLE IF NOT EXISTS rota_clock_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    user_id UUID NOT NULL,
    service_id UUID NOT NULL REFERENCES rota_services(id) ON DELETE CASCADE,
    assignment_id UUID REFERENCES rota_assignments(id) ON DELETE SET NULL,
    shift_date DATE NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    service_location VARCHAR(255) NOT NULL DEFAULT '',
    role VARCHAR(255) NOT NULL,
    status clock_session_status NOT NULL DEFAULT 'clocked_in',
    clock_in_time TIMESTAMPTZ NOT NULL,
    clock_in_lat DOUBLE PRECISION,
    clock_in_lng DOUBLE PRECISION,
    clock_in_accuracy DOUBLE PRECISION,
    clock_in_label TEXT,
    clock_out_time TIMESTAMPTZ,
    clock_out_lat DOUBLE PRECISION,
    clock_out_lng DOUBLE PRECISION,
    clock_out_accuracy DOUBLE PRECISION,
    clock_out_label TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rota_clock_user_date
    ON rota_clock_sessions (organization_id, user_id, shift_date);
CREATE UNIQUE INDEX IF NOT EXISTS idx_rota_clock_active
    ON rota_clock_sessions (organization_id, user_id, service_id, shift_date)
    WHERE status = 'clocked_in';

-- 6. Audit logs
CREATE TABLE IF NOT EXISTS rota_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    service_id UUID REFERENCES rota_services(id) ON DELETE SET NULL,
    user_id UUID,
    user_name VARCHAR(255) NOT NULL,
    action VARCHAR(255) NOT NULL,
    field_name VARCHAR(255),
    old_value TEXT,
    new_value TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rota_audit_org_created
    ON rota_audit_logs (organization_id, created_at DESC);

-- updated_at triggers (same pattern as checklist/rotas scripts)
CREATE OR REPLACE FUNCTION update_rota_services_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
    CREATE TRIGGER trigger_update_rota_services_updated_at
        BEFORE UPDATE ON rota_services
        FOR EACH ROW
        EXECUTE FUNCTION update_rota_services_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE OR REPLACE FUNCTION update_rota_assignments_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
    CREATE TRIGGER trigger_update_rota_assignments_updated_at
        BEFORE UPDATE ON rota_assignments
        FOR EACH ROW
        EXECUTE FUNCTION update_rota_assignments_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE OR REPLACE FUNCTION update_rota_attendance_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
    CREATE TRIGGER trigger_update_rota_attendance_updated_at
        BEFORE UPDATE ON rota_attendance
        FOR EACH ROW
        EXECUTE FUNCTION update_rota_attendance_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE OR REPLACE FUNCTION update_rota_clock_sessions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
    CREATE TRIGGER trigger_update_rota_clock_sessions_updated_at
        BEFORE UPDATE ON rota_clock_sessions
        FOR EACH ROW
        EXECUTE FUNCTION update_rota_clock_sessions_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

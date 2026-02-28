-- =====================================================
-- CHECKLIST TABLES - PostgreSQL Schema
-- =====================================================

-- Checklist templates (one per team)
CREATE TABLE IF NOT EXISTS checklist_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  team_id UUID NOT NULL REFERENCES teams(id),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  created_by VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_checklist_templates_team_id ON checklist_templates(team_id);

-- Checklist items (lines within a template)
CREATE TABLE IF NOT EXISTS checklist_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  template_id UUID NOT NULL REFERENCES checklist_templates(id) ON DELETE CASCADE,
  title VARCHAR(500) NOT NULL,
  description TEXT,
  "order" INT NOT NULL DEFAULT 0,
  is_required BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_checklist_items_template_id ON checklist_items(template_id);

-- Checklist records (one completed checklist per date/template/team)
CREATE TABLE IF NOT EXISTS checklist_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  template_id UUID NOT NULL REFERENCES checklist_templates(id),
  team_id UUID NOT NULL,
  date DATE NOT NULL,
  completed_by VARCHAR(255) NOT NULL,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(template_id, team_id, date)
);

CREATE INDEX IF NOT EXISTS idx_checklist_records_date ON checklist_records(date);
CREATE INDEX IF NOT EXISTS idx_checklist_records_team ON checklist_records(team_id);
CREATE INDEX IF NOT EXISTS idx_checklist_records_template ON checklist_records(template_id);
CREATE INDEX IF NOT EXISTS idx_checklist_records_completed_by ON checklist_records(completed_by);

-- Item statuses (per item, per record)
CREATE TABLE IF NOT EXISTS checklist_item_statuses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  checklist_record_id UUID NOT NULL REFERENCES checklist_records(id) ON DELETE CASCADE,
  checklist_item_id UUID NOT NULL REFERENCES checklist_items(id) ON DELETE CASCADE,
  is_checked BOOLEAN DEFAULT false,
  issue_reported TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(checklist_record_id, checklist_item_id)
);

CREATE INDEX IF NOT EXISTS idx_checklist_item_statuses_record ON checklist_item_statuses(checklist_record_id);
CREATE INDEX IF NOT EXISTS idx_checklist_item_statuses_item ON checklist_item_statuses(checklist_item_id);

-- Triggers to update updated_at
CREATE OR REPLACE FUNCTION update_checklist_templates_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_checklist_templates_updated_at
    BEFORE UPDATE ON checklist_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_checklist_templates_updated_at();

CREATE OR REPLACE FUNCTION update_checklist_items_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_checklist_items_updated_at
    BEFORE UPDATE ON checklist_items
    FOR EACH ROW
    EXECUTE FUNCTION update_checklist_items_updated_at();

CREATE OR REPLACE FUNCTION update_checklist_records_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_checklist_records_updated_at
    BEFORE UPDATE ON checklist_records
    FOR EACH ROW
    EXECUTE FUNCTION update_checklist_records_updated_at();

CREATE OR REPLACE FUNCTION update_checklist_item_statuses_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_checklist_item_statuses_updated_at
    BEFORE UPDATE ON checklist_item_statuses
    FOR EACH ROW
    EXECUTE FUNCTION update_checklist_item_statuses_updated_at();

-- =====================================================
-- SONGS TABLE - PostgreSQL Schema
-- =====================================================
-- This table stores worship songs with lyrics, chords, and metadata
-- =====================================================

CREATE TABLE IF NOT EXISTS songs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255),
    scale VARCHAR(50),
    tempo VARCHAR(50),
    chords TEXT,
    rhythm VARCHAR(50),
    lyrics TEXT,
    organization_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure title is not empty
    CONSTRAINT chk_songs_title_not_empty 
        CHECK (LENGTH(TRIM(title)) > 0)
);

-- Indexes for songs table
CREATE INDEX IF NOT EXISTS idx_songs_organization_id ON songs(organization_id);
CREATE INDEX IF NOT EXISTS idx_songs_title ON songs(title);
CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs(artist);
CREATE INDEX IF NOT EXISTS idx_songs_created_at ON songs(created_at);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_songs_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_songs_updated_at
    BEFORE UPDATE ON songs
    FOR EACH ROW
    EXECUTE FUNCTION update_songs_updated_at();

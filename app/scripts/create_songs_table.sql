-- =====================================================
-- SONGS TABLE - PostgreSQL Schema
-- =====================================================
-- This table stores worship songs with lyrics, chords, and metadata
-- =====================================================

-- Create songs table
CREATE TABLE IF NOT EXISTS songs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255),
    scale VARCHAR(50), -- e.g., "C Major", "A Minor"
    tempo VARCHAR(50), -- e.g., "120 BPM"
    chords TEXT, -- Chord progression or chord sheet
    rhythm VARCHAR(50), -- e.g., "4/4", "3/4", "Ballad", "Other", or custom value
    lyrics TEXT, -- Song lyrics
    organization_id UUID NOT NULL,
    created_by UUID, -- Optional: User who created the song
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   
    -- Ensure title is not empty
    CONSTRAINT chk_title_not_empty 
        CHECK (LENGTH(TRIM(title)) > 0)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_songs_organization_id ON songs(organization_id);
CREATE INDEX IF NOT EXISTS idx_songs_created_by ON songs(created_by);
CREATE INDEX IF NOT EXISTS idx_songs_title ON songs(title);
CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs(artist);
CREATE INDEX IF NOT EXISTS idx_songs_scale ON songs(scale);
CREATE INDEX IF NOT EXISTS idx_songs_rhythm ON songs(rhythm);
CREATE INDEX IF NOT EXISTS idx_songs_created_at ON songs(created_at DESC);

-- Full-text search index for searching across multiple fields
CREATE INDEX IF NOT EXISTS idx_songs_search ON songs USING GIN (
    to_tsvector('english', 
        COALESCE(title, '') || ' ' || 
        COALESCE(artist, '') || ' ' || 
        COALESCE(scale, '') || ' ' || 
        COALESCE(tempo, '') || ' ' || 
        COALESCE(chords, '') || ' ' || 
        COALESCE(rhythm, '') || ' ' || 
        COALESCE(lyrics, '')
    )
);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_songs_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
CREATE TRIGGER trigger_update_songs_updated_at
    BEFORE UPDATE ON songs
    FOR EACH ROW
    EXECUTE FUNCTION update_songs_updated_at();

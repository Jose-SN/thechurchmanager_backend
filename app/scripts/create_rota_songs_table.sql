-- =====================================================
-- ROTA_SONGS TABLE - PostgreSQL Schema
-- =====================================================
-- Junction table linking rotas to songs (many-to-many)
-- =====================================================

CREATE TABLE IF NOT EXISTS rota_songs (
    id SERIAL PRIMARY KEY,
    rota_id INTEGER NOT NULL,
    song_id INTEGER NOT NULL,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_rota_songs_rota 
        FOREIGN KEY (rota_id) 
        REFERENCES rotas(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_rota_songs_song 
        FOREIGN KEY (song_id) 
        REFERENCES songs(id) 
        ON DELETE CASCADE
);

-- Indexes for rota_songs table
CREATE INDEX IF NOT EXISTS idx_rota_songs_rota_id ON rota_songs(rota_id);
CREATE INDEX IF NOT EXISTS idx_rota_songs_song_id ON rota_songs(song_id);
CREATE INDEX IF NOT EXISTS idx_rota_songs_display_order ON rota_songs(rota_id, display_order);

COMMENT ON TABLE rota_songs IS 'Junction table linking rotas to songs (many-to-many)';
COMMENT ON COLUMN rota_songs.display_order IS 'Order in which songs should be displayed/performed';

GET_SONGS_QUERY = """
SELECT * FROM songs
ORDER BY created_at DESC
"""

GET_SONG_BY_ID_QUERY = """
SELECT * FROM songs WHERE id = $1
"""

GET_SONGS_BY_ORGANIZATION_QUERY = """
SELECT * FROM songs 
WHERE organization_id = $1
ORDER BY created_at DESC
"""

GET_SONGS_BY_CREATED_BY_QUERY = """
SELECT * FROM songs 
WHERE created_by = $1
ORDER BY created_at DESC
"""

SEARCH_SONGS_QUERY = """
SELECT * FROM songs
WHERE organization_id = $1
    AND ($2::VARCHAR IS NULL OR LOWER(title) LIKE LOWER('%' || $2 || '%'))
    AND ($3::VARCHAR IS NULL OR LOWER(artist) LIKE LOWER('%' || $3 || '%'))
    AND ($4::VARCHAR IS NULL OR LOWER(scale) LIKE LOWER('%' || $4 || '%'))
    AND ($5::VARCHAR IS NULL OR LOWER(tempo) LIKE LOWER('%' || $5 || '%'))
    AND ($6::VARCHAR IS NULL OR LOWER(chords) LIKE LOWER('%' || $6 || '%'))
    AND ($7::VARCHAR IS NULL OR LOWER(rhythm) LIKE LOWER('%' || $7 || '%'))
    AND ($8::VARCHAR IS NULL OR LOWER(lyrics) LIKE LOWER('%' || $8 || '%'))
ORDER BY created_at DESC
"""

INSERT_SONG_QUERY = """
INSERT INTO songs (
    title,
    artist,
    scale,
    tempo,
    chords,
    rhythm,
    lyrics,
    organization_id,
    created_by,
    created_at,
    updated_at
) VALUES (
    $1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW()
)
RETURNING *
"""

UPDATE_SONG_QUERY = """
UPDATE songs
SET 
    title = $1,
    artist = $2,
    scale = $3,
    tempo = $4,
    chords = $5,
    rhythm = $6,
    lyrics = $7,
    updated_at = NOW()
WHERE id = $8 AND organization_id = $9
RETURNING *
"""

DELETE_SONG_QUERY = """
DELETE FROM songs 
WHERE id = $1 AND organization_id = $2
"""

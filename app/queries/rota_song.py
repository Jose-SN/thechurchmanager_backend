GET_ROTA_SONGS_QUERY = """
SELECT * FROM rota_songs
ORDER BY rota_id, display_order, id
"""

GET_ROTA_SONG_BY_ID_QUERY = """
SELECT * FROM rota_songs WHERE id = $1
"""

GET_ROTA_SONGS_BY_ROTA_QUERY = """
SELECT rs.*, s.title, s.artist, s.scale, s.tempo, s.chords, s.rhythm, s.lyrics
FROM rota_songs rs
LEFT JOIN songs s ON rs.song_id = s.id
WHERE rs.rota_id = $1
ORDER BY rs.display_order, rs.id
"""

GET_ROTA_SONGS_BY_SONG_QUERY = """
SELECT * FROM rota_songs 
WHERE song_id = $1
ORDER BY display_order, id
"""

INSERT_ROTA_SONG_QUERY = """
INSERT INTO rota_songs (
    rota_id,
    song_id,
    display_order,
    created_at
) VALUES (
    $1, $2, $3, NOW()
)
RETURNING *
"""

UPDATE_ROTA_SONG_QUERY = """
UPDATE rota_songs
SET 
    rota_id = $1,
    song_id = $2,
    display_order = $3
WHERE id = $4
RETURNING *
"""

DELETE_ROTA_SONG_QUERY = """
DELETE FROM rota_songs 
WHERE id = $1
"""

DELETE_ROTA_SONGS_BY_ROTA_QUERY = """
DELETE FROM rota_songs 
WHERE rota_id = $1
"""

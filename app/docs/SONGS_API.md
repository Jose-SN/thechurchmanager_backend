# Songs Service API Documentation

This service manages worship songs with lyrics, chords, and metadata.

## Database Setup

Run the SQL migration script to create the songs table:

```bash
psql -U your_user -d your_database -f app/scripts/create_songs_table.sql
```

## API Endpoints

Base URL: `/song`

### 1. Get Songs (with filters)

**Endpoint:** `GET /song/get`

**Query Parameters:**
- `id` (optional): Song ID
- `organization_id` (optional): Filter by organization
- `created_by` (optional): Filter by creator user ID
- `title` (optional): Search by title
- `artist` (optional): Search by artist
- `scale` (optional): Search by scale
- `tempo` (optional): Search by tempo
- `chords` (optional): Search by chords
- `content` (optional): Search by content
- `rhythm` (optional): Search by rhythm
- `notes` (optional): Search by notes/lyrics

**Example:**
```
GET /song/get?organization_id=05938861-d294-4e9c-a88d-9c1413861e22
GET /song/get?organization_id=05938861-d294-4e9c-a88d-9c1413861e22&title=amazing&artist=hillsong
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "organization_id": "uuid",
      "created_by": "uuid",
      "title": "Amazing Grace",
      "artist": "Traditional",
      "scale": "G Major",
      "tempo": "80 BPM",
      "chords": "G C D Em",
      "content": "Additional notes",
      "rhythm": "4/4",
      "notes": "Amazing grace how sweet the sound...",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "count": 1
}
```

### 2. Get Song by ID

**Endpoint:** `GET /song/{song_id}`

**Example:**
```
GET /song/9fc7380b-58e8-45a3-aebe-b4b3c6b0a0cc
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "9fc7380b-58e8-45a3-aebe-b4b3c6b0a0cc",
    "organization_id": "uuid",
    "created_by": "uuid",
    "title": "Amazing Grace",
    "artist": "Traditional",
    "scale": "G Major",
    "tempo": "80 BPM",
    "chords": "G C D Em",
    "content": "Additional notes",
    "rhythm": "4/4",
    "notes": "Amazing grace how sweet the sound...",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 3. Create Song

**Endpoint:** `POST /song/save`

**Request Body:**
```json
{
  "organization_id": "05938861-d294-4e9c-a88d-9c1413861e22",
  "created_by": "user-uuid-here",
  "title": "Amazing Grace",
  "artist": "Traditional",
  "scale": "G Major",
  "tempo": "80 BPM",
  "chords": "G C D Em",
  "content": "Additional information about the song",
  "rhythm": "4/4",
  "notes": "Amazing grace how sweet the sound\nThat saved a wretch like me..."
}
```

**Required Fields:**
- `organization_id`: UUID of the organization
- `title`: Song title (cannot be empty)
- `notes`: Lyrics and chords (cannot be empty)

**Optional Fields:**
- `created_by`: UUID of the user who created the song
- `artist`: Artist or composer name
- `scale`: Musical scale (e.g., "C Major", "A Minor")
- `tempo`: Tempo in BPM (e.g., "120 BPM")
- `chords`: Chord progression or chord sheet
- `content`: Additional content or notes
- `rhythm`: Time signature (e.g., "4/4", "3/4", "Ballad")

**Response:**
```json
{
  "success": true,
  "message": "Song saved successfully",
  "data": {
    "id": "newly-created-uuid",
    "organization_id": "05938861-d294-4e9c-a88d-9c1413861e22",
    "created_by": "user-uuid-here",
    "title": "Amazing Grace",
    "artist": "Traditional",
    "scale": "G Major",
    "tempo": "80 BPM",
    "chords": "G C D Em",
    "content": "Additional information about the song",
    "rhythm": "4/4",
    "notes": "Amazing grace how sweet the sound\nThat saved a wretch like me...",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 4. Update Song

**Endpoint:** `PUT /song/update/{song_id}`

**Request Body:**
```json
{
  "organization_id": "05938861-d294-4e9c-a88d-9c1413861e22",
  "title": "Amazing Grace (Updated)",
  "artist": "Traditional - Arranged by John Newton",
  "scale": "C Major",
  "tempo": "85 BPM",
  "chords": "C F G Am",
  "content": "Updated content",
  "rhythm": "4/4",
  "notes": "Updated lyrics and chords..."
}
```

**Note:** `organization_id` is required in the request body for authorization. Only songs belonging to the specified organization can be updated.

**Response:**
```json
{
  "success": true,
  "message": "Song updated successfully",
  "data": {
    "id": "song-uuid",
    "organization_id": "05938861-d294-4e9c-a88d-9c1413861e22",
    "created_by": "user-uuid-here",
    "title": "Amazing Grace (Updated)",
    "artist": "Traditional - Arranged by John Newton",
    "scale": "C Major",
    "tempo": "85 BPM",
    "chords": "C F G Am",
    "content": "Updated content",
    "rhythm": "4/4",
    "notes": "Updated lyrics and chords...",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T12:00:00"
  }
}
```

### 5. Delete Song

**Endpoint:** `DELETE /song/delete/{song_id}`

**Query Parameters:**
- `organization_id` (required): Organization ID for authorization

**Example:**
```
DELETE /song/delete/9fc7380b-58e8-45a3-aebe-b4b3c6b0a0cc?organization_id=05938861-d294-4e9c-a88d-9c1413861e22
```

**Response:**
```json
{
  "success": true,
  "message": "Song deleted successfully"
}
```

## Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Auto-generated | Unique identifier |
| `organization_id` | UUID | Required | Organization this song belongs to |
| `created_by` | UUID | Optional | User who created the song |
| `title` | String (255) | Required | Song title |
| `artist` | String (255) | Optional | Artist or composer name |
| `scale` | String (50) | Optional | Musical scale (e.g., "C Major") |
| `tempo` | String (50) | Optional | Tempo (e.g., "120 BPM") |
| `chords` | Text | Optional | Chord progression or chord sheet |
| `content` | Text | Optional | Additional content/lyrics |
| `rhythm` | String (50) | Optional | Time signature (e.g., "4/4") |
| `notes` | Text | Required | Lyrics and chords |
| `created_at` | Timestamp | Auto-generated | Creation timestamp |
| `updated_at` | Timestamp | Auto-updated | Last update timestamp |

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": {
    "message": "title is required and cannot be empty"
  }
}
```

### 403 Forbidden
```json
{
  "success": false,
  "error": {
    "message": "Not authorized to update this song"
  }
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": {
    "message": "Song not found"
  }
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": {
    "message": "Database query error: [error details]"
  }
}
```

## Security & Authorization

- All update and delete operations require `organization_id` for authorization
- Songs can only be modified or deleted by users from the same organization
- Full-text search is available across all text fields using PostgreSQL's GIN index

## Search Features

The service supports partial matching on multiple fields:
- Title
- Artist
- Scale
- Tempo
- Chords
- Content
- Rhythm
- Notes/Lyrics

Example search query:
```
GET /song/get?organization_id=uuid&title=amazing&artist=traditional&scale=major
```

This will find songs where:
- Title contains "amazing"
- Artist contains "traditional"
- Scale contains "major"
- All within the specified organization

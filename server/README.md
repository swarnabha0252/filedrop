# FileDrop Backend

FastAPI backend for the FileDrop temporary file sharing application.

## Features

- Secure file upload with expiration
- Cryptographically secure share tokens
- Password protection (Argon2)
- Download limits
- Manual deletion with private credentials
- Automatic cleanup of expired files
- Local storage backend (S3-compatible interface ready)

## API Endpoints

```
POST   /api/v1/files              # Upload file
GET    /api/v1/files/{token}      # Get file metadata
GET    /api/v1/files/{token}/download  # Download file
POST   /api/v1/files/{token}/verify    # Verify password
DELETE /api/v1/files/{token}      # Delete file (requires delete_token)
GET    /health                    # Health check
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` from `.env.example`:
```bash
cp .env.example .env
```

3. Configure PostgreSQL database in `.env`

4. Run migrations:
```bash
alembic upgrade head
```

5. Start server:
```bash
uvicorn app.main:app --reload
```

## Example Usage

### Upload File
```bash
curl -X POST http://localhost:8000/api/v1/files \
  -F "file=@research.pdf" \
  -F "expiry=3600" \
  -F "download_limit=10"
```

Response:
```json
{
  "token": "X7k92LmQ8xP4...",
  "download_url": "http://localhost:8000/api/v1/files/X7k92LmQ8xP4.../download",
  "delete_token": "a1b2c3d4e5f6...",
  "expires_at": "2026-09-06T14:00:00Z",
  "filename": "research.pdf",
  "size": 24800000,
  "download_limit": 10
}
```

### Get Metadata
```bash
curl http://localhost:8000/api/v1/files/X7k92LmQ8xP4...
```

Response:
```json
{
  "filename": "research.pdf",
  "size": 24800000,
  "mime_type": "application/pdf",
  "expires_at": "2026-09-06T14:00:00Z",
  "download_count": 0,
  "download_limit": 10,
  "password_required": false
}
```

### Download File
```bash
curl -O -J http://localhost:8000/api/v1/files/X7k92LmQ8xP4.../download
```

### Password Protected Download
```bash
# First verify password
curl -X POST http://localhost:8000/api/v1/files/X7k92LmQ8xP4.../verify \
  -H "Content-Type: application/json" \
  -d '{"password": "secret123"}'

# Then download with verified token
curl -O -J "http://localhost:8000/api/v1/files/X7k92LmQ8xP4.../download?verified=true"
```

### Delete File
```bash
curl -X DELETE http://localhost:8000/api/v1/files/X7k92LmQ8xP4... \
  -H "Content-Type: application/json" \
  -d '{"delete_token": "a1b2c3d4e5f6..."}'
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | development | Application environment |
| `DATABASE_URL` | postgresql+asyncpg://postgres:postgres@localhost:5432/filedrop | PostgreSQL connection string |
| `MAX_FILE_SIZE_MB` | 100 | Maximum file size in MB |
| `FRONTEND_URL` | http://localhost:5173 | Frontend URL for CORS |
| `STORAGE_BACKEND` | local | Storage backend (local/s3) |
| `LOCAL_STORAGE_PATH` | ./storage | Local storage directory |
| `ALLOWED_ORIGINS` | http://localhost:5173 | CORS allowed origins |
| `TOKEN_LENGTH` | 24 | Length of public share tokens |
| `CLEANUP_INTERVAL_SECONDS` | 3600 | Cleanup job interval |
| `RATE_LIMIT_REQUESTS` | 30 | Requests per window |
| `RATE_LIMIT_WINDOW_SECONDS` | 60 | Rate limit window |

## Testing

```bash
pytest tests/ -v
```

## Project Structure

```
server/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── api/
│   │   ├── router.py           # API router
│   │   └── routes/
│   │       ├── health.py       # Health check endpoint
│   │       └── files.py        # File endpoints
│   ├── core/
│   │   ├── config.py           # Configuration
│   │   └── security.py         # Token generation, password hashing
│   ├── db/
│   │   ├── session.py          # Database session
│   │   └── base.py             # SQLAlchemy base
│   ├── models/
│   │   └── file.py             # File model
│   ├── schemas/
│   │   └── file.py             # Pydantic schemas
│   ├── services/
│   │   ├── file_service.py     # File business logic
│   │   ├── storage_service.py  # Storage abstraction
│   │   ├── token_service.py    # Token generation
│   │   └── cleanup_service.py  # Cleanup job
│   └── utils/
│       ├── filename.py         # Filename utilities
│       └── file_validation.py  # File validation
├── tests/                      # Test suite
├── migrations/                 # Alembic migrations
├── requirements.txt
├── alembic.ini
└── .env.example
```

## Security Notes

- Tokens use cryptographically secure random generation (24 chars = ~142 bits entropy)
- Passwords hashed with Argon2id
- Delete tokens hashed with Argon2id
- File type validation via magic bytes
- Path traversal prevention
- Rate limiting on sensitive endpoints
- CORS configured for specific origins
- No sensitive data in logs

## Production Deployment

1. Set `APP_ENV=production`
2. Use strong `DATABASE_URL`
3. Configure `ALLOWED_ORIGINS` to your frontend domain
4. Set up S3-compatible storage backend
5. Run cleanup job via cron/scheduler
6. Use reverse proxy (nginx) with TLS
# FileDrop

A lightweight, minimalistic file sharing web application with drag-and-drop functionality and configurable expiration times.

## Features

- **Drag & Drop** - Upload files by dragging them onto the drop zone or clicking to browse
- **Expiration Settings** - Set file expiration: 30 mins, 1 hr, 2 hrs, 6 hrs, 12 hrs, 24 hrs, or custom time
- **Custom Time Picker** - Phone-style scrollable hours/minutes dropdown for precise expiration
- **Confirmation Dialog** - Confirm custom expiration before applying
- **File Preview** - See selected files with names and sizes
- **Minimalistic UI** - Clean, light theme with subtle animations
- **Secure Backend** - FastAPI with PostgreSQL, Argon2 password hashing, cryptographically secure tokens
- **File Security** - Magic byte validation, path traversal prevention, rate limiting

## Tech Stack

### Frontend
- **React 19** with Vite
- **Tailwind CSS v4** for styling
- **PostCSS** for CSS processing

### Backend
- **FastAPI** with Python 3.11+
- **PostgreSQL** with SQLAlchemy 2.0 (async)
- **Alembic** for migrations
- **Argon2** for password hashing
- **Uvicorn** ASGI server

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 14+

### Frontend Setup

```bash
# Install dependencies
npm install

# Development server (opens at http://localhost:5173)
npm run dev

# Production build (output in dist/)
npm run build

# Preview production build
npm run preview
```

### Backend Setup

```bash
cd server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database URL and settings

# Run migrations
alembic upgrade head

# Start server (http://localhost:8000)
uvicorn app.main:app --reload
```

## Project Structure

```
filedrop/
├── src/                    # Frontend source
│   ├── App.jsx            # Main component with all features
│   ├── main.jsx           # React entry point
│   └── index.css          # Tailwind imports + custom animations
├── server/                # Backend source
│   ├── app/
│   │   ├── main.py        # FastAPI app entry point
│   │   ├── api/           # API routes
│   │   ├── core/          # Config & security
│   │   ├── db/            # Database session & models
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utilities
│   ├── tests/             # Test suite
│   ├── migrations/        # Alembic migrations
│   ├── requirements.txt
│   ├── alembic.ini
│   └── .env.example
├── index.html             # HTML entry point
├── tailwind.config.js
├── postcss.config.js
├── vite.config.js
└── package.json
```

## Usage

1. Open the app in browser (`http://localhost:5173`)
2. Drag files onto the drop zone or click to select
3. Choose expiration time from dropdown (or select "Custom" for precise time)
4. Click **Drop** to initiate sharing (button enables after file selection)

## API Endpoints

```
POST   /api/v1/files              # Upload file
GET    /api/v1/files/{token}      # Get file metadata
GET    /api/v1/files/{token}/download  # Download file
POST   /api/v1/files/{token}/verify    # Verify password
DELETE /api/v1/files/{token}      # Delete file (requires delete_token)
GET    /health                    # Health check
```

## Environment Variables

### Frontend
No environment variables required.

### Backend (server/.env)

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
# Frontend linting
npm run lint

# Backend tests
cd server
pytest tests/ -v
```

## Custom Animations

Defined in `src/index.css`:
- `animate-slide-down` - For custom time picker panel
- `animate-fade-in` - For confirmation modal backdrop
- `animate-scale-in` - For confirmation modal content

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
7. Build frontend: `npm run build` and serve `dist/` via nginx
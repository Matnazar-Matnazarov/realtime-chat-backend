# Realtime Chat Application Backend

A professional, production-ready real-time chat application backend built with FastAPI, featuring WebSocket support, cookie-based authentication, OAuth integration, group messaging, and admin panel.

## 🚀 Features

- **Real-time Messaging**: WebSocket-based instant messaging for private and group chats
- **Cookie-based Authentication**: HttpOnly cookies for secure token storage (access + refresh tokens)
- **Dual Authentication Support**: Both cookie-based and Bearer token authentication
- **User Authentication**: JWT-based authentication with Google OAuth2 support via `fastapi-users`
- **Group Chats**: Create and manage group conversations with multiple members
- **Contact Management**: Add and manage contacts
- **Optimized User Search**: Case-insensitive search with Btree indexes for high performance
- **Media Support**: Upload and share images and videos
- **Online Status**: Real-time online/offline status tracking via WebSocket
- **Admin Panel**: FastAdmin-based admin interface for database management
- **Redis Integration**: Pub/sub support for scalable group messaging
- **Database Migrations**: Alembic for database schema management with proper UUID handling
- **Async Architecture**: Fully async/await implementation for high performance
- **Security Headers**: Comprehensive security headers middleware
- **Performance Monitoring**: Request timing middleware with microsecond precision
- **Response Compression**: GZip middleware for optimized response sizes
- **Connection Pooling**: Optimized database connection pooling

## 📋 Tech Stack

- **FastAPI** – High-performance async API framework
- **WebSockets** – Real-time communication
- **SQLAlchemy 2.0** – Async ORM
- **Alembic** – Database migrations
- **PostgreSQL** – Primary database with optimized indexes
- **Redis** – Pub/sub for groups and online status
- **fastapi-users** – JWT + Google OAuth2 authentication
- **Uvicorn** – ASGI server with uvloop
- **FastAdmin** – Admin panel interface
- **pwdlib** – Modern password hashing (Argon2)
- **ORJSON** – Fast JSON serialization

## 🏗️ Project Structure

```
realtime-chat-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API routes
│   │   ├── dependencies.py     # API dependencies (auth, db)
│   │   └── v1/
│   │       ├── auth.py         # Custom JSON login with cookies
│   │       ├── oauth.py        # Google OAuth endpoints
│   │       ├── users.py        # User endpoints with optimized search
│   │       ├── messages.py     # Message endpoints
│   │       ├── groups.py       # Group endpoints
│   │       ├── contacts.py     # Contact endpoints
│   │       ├── websocket.py    # WebSocket endpoints
│   │       ├── upload.py       # File upload endpoints
│   │       └── router.py       # API router
│   ├── auth/                   # Authentication
│   │   ├── database.py         # User database adapter
│   │   ├── users.py            # User management
│   │   └── oauth.py            # OAuth2 configuration
│   ├── core/                   # Core functionality
│   │   ├── config.py            # Application settings
│   │   ├── security.py         # JWT token utilities
│   │   ├── utils.py            # Authentication utilities
│   │   ├── websocket.py        # WebSocket connection manager
│   │   ├── middleware.py       # Custom middleware (timing, security)
│   │   └── redis.py            # Redis connection
│   ├── db/                     # Database
│   │   └── base.py             # Database base and session
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py             # User model with search indexes
│   │   ├── message.py          # Message model
│   │   ├── group.py            # Group and GroupMember models
│   │   └── contact.py         # Contact model
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── message.py
│   │   ├── group.py
│   │   └── contact.py
│   └── admin/                  # Admin panel
│       ├── admin.py            # FastAdmin configuration
│       └── views/              # Admin views
│           ├── user.py
│           ├── message.py
│           ├── group.py
│           └── contact.py
├── alembic/                    # Database migrations
│   ├── env.py                  # Alembic environment with UUID handling
│   └── versions/               # Migration files
├── scripts/
│   ├── reset_database.py      # Database reset script
│   └── seed_users.py          # User seeding script
├── tests/                      # Test suite
│   ├── conftest.py            # Pytest configuration
│   └── test_*.py              # Test files
├── .env.example               # Environment variables template
├── alembic.ini                # Alembic configuration
├── pyproject.toml             # Project configuration
├── Makefile                   # Development commands
└── README.md                  # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.13+
- PostgreSQL 12+
- Redis 6+ (optional, but recommended)
- `uv` package manager (recommended) or `pip`

### Quick Start with Make

```bash
make install      # Install dependencies
make migrate      # Run database migrations
make seed-users   # Create admin and test users
make run          # Start server
```

### Manual Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Matnazar-Matnazarov/realtime-chat-backend.git
   cd realtime-chat-backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   # Using uv (recommended)
   uv pip install -r requirements.txt
   
   # Or using pip
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up PostgreSQL database**:
   ```bash
   createdb chatdb
   # Or use your preferred method
   ```

6. **Run database migrations**:
   ```bash
   make migrate
   # Or manually:
   alembic upgrade head
   ```

7. **Seed initial users**:
   ```bash
   make seed-users
   # Or manually:
   PYTHONPATH=$(pwd) uv run python scripts/seed_users.py
   ```

8. **Start Redis** (if not running):
   ```bash
   redis-server
   # Or check if Redis is already running:
   redis-cli ping
   ```

9. **Run the application**:
   ```bash
   make run
   # Or manually:
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Admin Panel**: http://localhost:8000/admin
- **Health Check**: http://localhost:8000/health

## ⚙️ Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql+asyncpg://user:pass@localhost:5432/chatdb`)
- `REDIS_URL`: Redis connection string (e.g., `redis://localhost:6379/0`)
- `SECRET_KEY`: Secret key for JWT access tokens (generate with `openssl rand -hex 32`)
- `REFRESH_SECRET_KEY`: Secret key for JWT refresh tokens (generate with `openssl rand -hex 32`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiration time (default: 15 minutes)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration time (default: 7 days)
- `CORS_ORIGINS_STR`: Comma-separated list of allowed origins (e.g., `http://localhost:3000,http://localhost:5173`) - automatically parsed to list
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`: Google OAuth credentials (optional)
- `ALLOWED_EXTENSIONS_STR`: Comma-separated list of allowed file MIME types for uploads - automatically parsed to set
- `DEBUG`: Enable debug mode (default: `False`)

**Note**: For `CORS_ORIGINS_STR` and `ALLOWED_EXTENSIONS_STR`, use comma-separated values without spaces or brackets. The application will automatically parse them into lists/sets via computed fields.

### Database URL Format

For async PostgreSQL, use `asyncpg` driver:
```
postgresql+asyncpg://username:password@localhost:5432/database_name
```

## 📚 API Documentation

### Authentication

#### Custom JSON Login (Cookie-based)
- `POST /api/v1/auth/login` - Login with JSON credentials (sets HttpOnly cookies)
  - Request: `{"username": "user", "password": "pass"}`
  - Response: Returns tokens in body and sets cookies
- `POST /api/v1/auth/refresh` - Refresh access token (uses cookie or body)
- `POST /api/v1/auth/logout` - Logout (clears cookies)

#### FastAPI Users Endpoints
- `POST /auth/register` - Register a new user
- `POST /auth/jwt/login` - Login with form data (returns JWT token)
- `POST /auth/jwt/logout` - Logout
- `GET /auth/verify` - Verify email
- `POST /auth/forgot-password` - Request password reset
- `GET /users/me` - Get current user info
- `PATCH /users/me` - Update current user

#### OAuth2
- `GET /api/v1/oauth/google/authorize` - Initiate Google OAuth flow
- `GET /api/v1/oauth/google/callback` - Handle Google OAuth callback
- `GET /api/v1/oauth/google/status` - Check Google OAuth configuration

### Users

- `GET /api/v1/users/me` - Get current user info
- `GET /api/v1/users/search?query=...&limit=20` - Search users (case-insensitive, optimized with Btree indexes)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PATCH /api/v1/users/me/online?is_online=true` - Update online status

### Messages

- `POST /api/v1/messages` - Send a message
  - Body: `{"content": "...", "receiver_id": "..."}` or `{"content": "...", "group_id": "..."}`
- `GET /api/v1/messages?receiver_id=...&group_id=...&limit=50&offset=0` - Get messages
- `PATCH /api/v1/messages/{message_id}/read` - Mark message as read

### Groups

- `POST /api/v1/groups` - Create a group
- `GET /api/v1/groups?limit=50&offset=0` - Get user's groups
- `GET /api/v1/groups/{group_id}` - Get group details
- `PATCH /api/v1/groups/{group_id}` - Update group
- `POST /api/v1/groups/{group_id}/members?user_id=...` - Add member
- `DELETE /api/v1/groups/{group_id}/members/{user_id}` - Remove member

### Contacts

- `POST /api/v1/contacts` - Add a contact
- `GET /api/v1/contacts` - Get all contacts
- `DELETE /api/v1/contacts/{contact_id}` - Remove a contact

### WebSocket

- `WS /api/v1/ws/{user_id}?token=...` - WebSocket connection for real-time messaging
  - Token: JWT access token in query parameter
  - Auto-reconnects on disconnect
  - Broadcasts online status changes

### File Upload

- `POST /api/v1/upload` - Upload a file (image/video)
  - Content-Type: `multipart/form-data`
  - File size limit: 10MB (configurable)
- `GET /api/v1/upload/{filename}` - Get uploaded file

## 🔌 WebSocket Protocol

### Connection

Connect to `/api/v1/ws/{user_id}` with a JWT access token in query params:
```
ws://localhost:8000/api/v1/ws/{user_id}?token={access_token}
```

### Message Types

**Client → Server:**
- `{"type": "join_group", "group_id": "..."}` - Join a group room
- `{"type": "leave_group", "group_id": "..."}` - Leave a group room
- `{"type": "ping"}` - Heartbeat

**Server → Client:**
- `{"type": "message", "id": "...", "content": "...", "sender_id": "...", "receiver_id": "...", "created_at": "...", "sender": {...}}` - New message received
- `{"type": "online_status", "user_id": "...", "is_online": true}` - User status update
- `{"type": "pong"}` - Heartbeat response
- `{"type": "error", "message": "..."}` - Error message

## 🗄️ Database Models

### User
- Authentication fields (email, hashed_password)
- Profile fields (username, first_name, last_name, avatar_url)
- Status fields (is_online, last_seen)
- **Indexes**: 
  - Functional Btree index on `LOWER(username)` for case-insensitive search
  - Functional Btree index on `LOWER(email)` for case-insensitive search
  - Partial Btree index on `is_active = true` for active user queries

### Message
- Content and metadata
- Relationships: sender, receiver (optional), group (optional)
- Media support (media_url, media_type)
- Read status (is_read)
- Timestamps (created_at)

### Group
- Group information (name, description, avatar_url)
- Creator relationship
- Privacy setting (is_private)

### GroupMember
- Many-to-many relationship between User and Group
- Role (member, admin)

### Contact
- Many-to-many relationship between Users
- Optional nickname

## 🔐 Security Features

- **HttpOnly Cookies**: Access and refresh tokens stored in HttpOnly cookies (XSS protection)
- **Secure Cookies**: Cookies use `Secure` flag in production
- **SameSite Protection**: Cookies use `SameSite=Lax` for CSRF protection
- **Password Hashing**: Argon2 password hashing via `pwdlib`
- **JWT Tokens**: Separate secrets for access and refresh tokens
- **Security Headers**: 
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Strict-Transport-Security` (production only)
- **CORS**: Configurable CORS with credentials support
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **File Upload Validation**: Size and MIME type validation
- **Token Expiration**: Configurable token expiration times

## 🎯 Performance Optimizations

- **Connection Pooling**: Optimized PostgreSQL connection pool (size: 20, max_overflow: 10)
- **Connection Health Checks**: `pool_pre_ping=True` for connection validation
- **Connection Recycling**: Connections recycled after 1 hour
- **Database Indexes**: Btree indexes for optimized user search
- **Response Compression**: GZip middleware for responses > 1KB
- **Fast JSON**: ORJSON for faster JSON serialization
- **uvloop**: High-performance event loop (disabled in tests)
- **Request Timing**: Microsecond-precision timing headers

## 🧪 Testing

### Running Tests

Run all tests:
```bash
make test
# Or manually:
uv run pytest -v
```

Run with coverage:
```bash
make test-cov
# Or manually:
uv run pytest --cov=app --cov-report=html
```

Run specific test file:
```bash
uv run pytest tests/test_auth.py -v
```

### Test Structure

Tests are located in the `tests/` directory:
- `conftest.py` - Pytest fixtures and configuration
- `test_auth.py` - Authentication tests
- `test_users.py` - User endpoint tests
- `test_messages.py` - Message endpoint tests
- `test_groups.py` - Group endpoint tests
- `test_contacts.py` - Contact endpoint tests
- `test_upload.py` - File upload tests
- `test_health.py` - Health check tests

### Test Database

Tests use a separate test database (`test_chatdb`). Make sure it exists:
```bash
createdb test_chatdb
```

Or tests will create it automatically if permissions allow.

## 🛠️ Development Scripts

### Database Management

**Reset Database** (drops all tables, recreates migrations):
```bash
make reset-db
# Or manually:
PYTHONPATH=$(pwd) uv run python scripts/reset_database.py
```

**Seed Users** (creates admin and test users):
```bash
make seed-users
# Or manually:
PYTHONPATH=$(pwd) uv run python scripts/seed_users.py
```

### Code Quality

**Format code**:
```bash
make format
# Or manually:
uv run ruff format app/ tests/ scripts/
```

**Lint code**:
```bash
make lint
# Or manually:
uv run ruff check app/ tests/ scripts/
```

**Fix linting issues**:
```bash
make lint-fix
# Or manually:
uv run ruff check app/ tests/ scripts/ --fix
```

### Migrations

**Create new migration**:
```bash
make migrate-create msg="description"
# Or manually:
uv run alembic revision --autogenerate -m "description"
```

**Apply migrations**:
```bash
make migrate
# Or manually:
uv run alembic upgrade head
```

## 📦 Deployment

### Using Uvicorn

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Gunicorn with Uvicorn Workers

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables for Production

- Set `DEBUG=False`
- Use strong `SECRET_KEY` and `REFRESH_SECRET_KEY` (generate with `openssl rand -hex 32`)
- Configure proper `CORS_ORIGINS_STR`
- Use production database and Redis URLs
- Set up proper file storage (S3, etc.) for uploads
- Configure SSL/TLS certificates
- Set up proper logging and monitoring

## 🐛 Troubleshooting

### Configuration Parsing Errors

If you encounter errors like `error parsing value for field "CORS_ORIGINS"`:

- **Problem**: Environment variables with lists/sets are not formatted correctly
- **Solution**: Use `CORS_ORIGINS_STR` and `ALLOWED_EXTENSIONS_STR` with comma-separated values (no brackets or quotes):
  ```
  # ✅ Correct
  CORS_ORIGINS_STR=http://localhost:3000,http://localhost:5173
  ALLOWED_EXTENSIONS_STR=image/jpeg,image/png,video/mp4
  
  # ❌ Wrong
  CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
  CORS_ORIGINS_STR=http://localhost:3000, http://localhost:5173  # spaces after comma
  ```

### Database Connection Issues

- Ensure PostgreSQL is running: `sudo systemctl status postgresql` (Linux) or check service status
- Check `DATABASE_URL` format (must use `asyncpg` driver): `postgresql+asyncpg://user:pass@host:port/dbname`
- Verify database exists: `psql -U postgres -l` to list databases
- Check database user permissions
- Verify connection pool settings in `app/db/base.py`

### Redis Connection Issues

- Ensure Redis is running: `redis-cli ping` (should return `PONG`)
- Check `REDIS_URL` format: `redis://localhost:6379/0`
- Redis is optional but recommended for production (app will work without it, but group messaging may be limited)
- Start Redis: `redis-server` or `sudo systemctl start redis`

### Migration Issues

- Run `alembic upgrade head` to apply migrations
- Check `alembic.ini` configuration matches your `DATABASE_URL`
- Ensure database user has proper permissions (CREATE, ALTER, etc.)
- If migrations fail, check database connection first
- To create initial migration: `alembic revision --autogenerate -m "Initial migration"`
- **Note**: Migration files are autogenerated with proper UUID handling via `render_item` in `alembic/env.py`

### Import Errors

- Ensure all dependencies are installed: `uv pip install -r requirements.txt`
- Check Python version: `python --version` (requires 3.13+)
- Verify virtual environment is activated
- If using `uv`, run: `uv pip install -r requirements.txt`

### WebSocket Connection Issues

- Verify WebSocket endpoint URL: `ws://localhost:8000/api/v1/ws/{user_id}?token=...`
- Check CORS settings if connecting from frontend
- Ensure JWT token is valid and not expired
- Check server logs for connection errors
- Verify token is passed in query parameter, not headers

### Admin Panel Access Issues

- Admin panel is available at `/admin`
- Uses FastAdmin framework
- Configured via `app/admin/admin.py`
- Access requires superuser privileges

### Cookie Authentication Issues

- Ensure `withCredentials: true` is set in frontend requests
- Check CORS `allow_credentials=True` is configured
- Verify cookie domain and path settings
- In development, cookies work on `localhost` and `127.0.0.1`
- In production, ensure proper domain configuration

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests
5. Run tests and linting (`make test && make lint`)
6. Commit your changes (`git commit -m 'feat: add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📧 Contact

For questions or issues, please open an issue on the repository.

---

Built with ❤️ using FastAPI

# Realtime Chat Application Backend

A professional, production-ready real-time chat application backend built with FastAPI, featuring WebSocket support, OAuth authentication, group messaging, and admin panel.

## 🚀 Features

- **Real-time Messaging**: WebSocket-based instant messaging for private and group chats
- **User Authentication**: JWT-based authentication with Google/GitHub OAuth2 support via `fastapi-users`
- **Group Chats**: Create and manage group conversations with multiple members
- **Contact Management**: Add and manage contacts
- **User Search**: Search users by username or email
- **Media Support**: Upload and share images and videos
- **Online Status**: Real-time online/offline status tracking
- **Admin Panel**: SQLAdmin-based admin interface for database management
- **Redis Integration**: Pub/sub support for scalable group messaging
- **Database Migrations**: Alembic for database schema management
- **Async Architecture**: Fully async/await implementation for high performance

## 📋 Tech Stack

- **FastAPI** – High-performance async API framework
- **WebSockets** – Real-time communication
- **SQLAlchemy 2.0** – Async ORM
- **Alembic** – Database migrations
- **PostgreSQL** – Primary database
- **Redis** – Pub/sub for groups and online status
- **fastapi-users** – JWT + Google/GitHub OAuth2 authentication
- **Uvicorn** – ASGI server with uvloop
- **SQLAdmin** – Admin panel interface

## 🏗️ Project Structure

```
realtime-chat-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API routes
│   │   ├── v1/
│   │   │   ├── users.py        # User endpoints
│   │   │   ├── messages.py    # Message endpoints
│   │   │   ├── groups.py      # Group endpoints
│   │   │   ├── contacts.py    # Contact endpoints
│   │   │   ├── websocket.py   # WebSocket endpoints
│   │   │   ├── upload.py      # File upload endpoints
│   │   │   └── router.py      # API router
│   │   └── dependencies.py     # API dependencies
│   ├── auth/                   # Authentication
│   │   ├── database.py         # User database adapter
│   │   ├── users.py            # User management
│   │   └── oauth.py            # OAuth2 configuration
│   ├── core/                   # Core functionality
│   │   ├── config.py            # Application settings
│   │   ├── security.py         # Security utilities
│   │   ├── websocket.py        # WebSocket manager
│   │   └── redis.py            # Redis connection
│   ├── db/                     # Database
│   │   └── base.py             # Database base and session
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py             # User model
│   │   ├── message.py          # Message model
│   │   ├── group.py            # Group and GroupMember models
│   │   └── contact.py          # Contact model
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── message.py
│   │   ├── group.py
│   │   └── contact.py
│   └── admin/                  # Admin panel
│       └── admin.py            # SQLAdmin configuration
├── alembic/                    # Database migrations
│   ├── env.py
│   └── versions/
├── scripts/
│   └── create_superuser.py    # Superuser creation script
├── .env.example                # Environment variables template
├── alembic.ini                  # Alembic configuration
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.13+
- PostgreSQL 12+
- Redis 6+ (optional, but recommended)
- pip or uv

### Quick Start with Make

```bash
make install    # Install dependencies
make migrate    # Run database migrations
make superuser  # Create admin user
make run        # Start server
```

### Manual Setup

### Setup

1. **Clone the repository** (if applicable):
   ```bash
   cd realtime-chat-backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # Or with uv:
   uv pip install -r requirements.txt
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

6. **Initialize Alembic** (if not already done):
   ```bash
   alembic init alembic
   ```
   Note: The `alembic/` directory should already exist. If you get an error, the directory might need to be created.

7. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```
   
   If this is the first time, create the initial migration:
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

8. **Create a superuser**:
   ```bash
   python scripts/create_superuser.py
   ```
   
   Or using `uv`:
   ```bash
   uv run python scripts/create_superuser.py
   ```

9. **Start Redis** (if not running):
   ```bash
   redis-server
   ```
   
   Or check if Redis is already running:
   ```bash
   redis-cli ping
   ```

10. **Run the application**:
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    
    Or using the run script:
    ```bash
    python main.py
    ```
    
    Or with `uv`:
    ```bash
    uv run uvicorn app.main:app --reload
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
- `SECRET_KEY`: Secret key for JWT tokens (generate with `openssl rand -hex 32`)
- `CORS_ORIGINS_STR`: Comma-separated list of allowed origins (e.g., `http://localhost:3000,http://localhost:5173`) - automatically parsed to list
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`: Google OAuth credentials (optional)
- `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET`: GitHub OAuth credentials (optional)
- `ALLOWED_EXTENSIONS_STR`: Comma-separated list of allowed file MIME types for uploads - automatically parsed to set

**Note**: For `CORS_ORIGINS_STR` and `ALLOWED_EXTENSIONS_STR`, use comma-separated values without spaces or brackets. The application will automatically parse them into lists/sets via computed fields.

### Database URL Format

For async PostgreSQL, use `asyncpg` driver:
```
postgresql+asyncpg://username:password@localhost:5432/database_name
```

## 📚 API Documentation

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/jwt/login` - Login with email/password (returns JWT token)
- `POST /auth/jwt/logout` - Logout
- `GET /auth/verify` - Verify email
- `POST /auth/forgot-password` - Request password reset

### Users

- `GET /api/v1/users/me` - Get current user info
- `GET /api/v1/users/search?query=...` - Search users
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PATCH /api/v1/users/me/online?is_online=true` - Update online status

### Messages

- `POST /api/v1/messages` - Send a message
- `GET /api/v1/messages?receiver_id=...&group_id=...` - Get messages
- `PATCH /api/v1/messages/{message_id}/read` - Mark message as read

### Groups

- `POST /api/v1/groups` - Create a group
- `GET /api/v1/groups` - Get user's groups
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

### File Upload

- `POST /api/v1/upload` - Upload a file (image/video)
- `GET /api/v1/upload/{filename}` - Get uploaded file

## 🔌 WebSocket Protocol

### Connection

Connect to `/api/v1/ws/{user_id}` with a JWT token in query params.

### Message Types

**Client → Server:**
- `{"type": "join_group", "group_id": "..."}` - Join a group room
- `{"type": "leave_group", "group_id": "..."}` - Leave a group room
- `{"type": "ping"}` - Heartbeat

**Server → Client:**
- `{"type": "message", ...}` - New message received
- `{"type": "user_status", "user_id": "...", "is_online": true}` - User status update
- `{"type": "pong"}` - Heartbeat response

## 🗄️ Database Models

### User
- Authentication fields (email, hashed_password)
- Profile fields (username, first_name, last_name, avatar_url, bio)
- Status fields (is_online, last_seen)

### Message
- Content and metadata
- Relationships: sender, receiver (optional), group (optional)
- Media support (media_url, media_type)
- Read status

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

## 🔐 Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- CORS configured for allowed origins
- SQL injection protection via SQLAlchemy
- File upload size and type validation

## 🧪 Testing

### Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_auth.py
```

Run with verbose output:
```bash
pytest -v
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
- Use strong `SECRET_KEY`
- Configure proper `CORS_ORIGINS_STR`
- Use production database and Redis URLs
- Set up proper file storage (S3, etc.) for uploads

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

### Import Errors

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (requires 3.13+)
- Verify virtual environment is activated
- If using `uv`, run: `uv pip install -r requirements.txt`

### WebSocket Connection Issues

- Verify WebSocket endpoint URL: `ws://localhost:8000/api/v1/ws/{user_id}?token=...`
- Check CORS settings if connecting from frontend
- Ensure JWT token is valid and not expired
- Check server logs for connection errors

### Admin Panel Access Issues

- Ensure superuser exists: `python scripts/create_superuser.py`
- Use superuser email and password to login
- Check `ADMIN_EMAIL` and `ADMIN_PASSWORD` in `.env`
- Verify user has `is_superuser=True` in database

## 📝 License

See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📧 Contact

For questions or issues, please open an issue on the repository.

---

Built with ❤️ using FastAPI

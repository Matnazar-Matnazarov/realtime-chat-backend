# 💬 Realtime Chat Application Backend

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.17+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![WebSocket](https://img.shields.io/badge/WebSocket-010101?style=for-the-badge&logo=socket.io&logoColor=white)

**Production-ready real-time chat backend with WebSocket support, cookie-based authentication, and OAuth integration**

[Features](#-features) • [Quick Start](#-quick-start) • [API Documentation](#-api-documentation) • [Deployment](#-deployment)

</div>

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [WebSocket Protocol](#-websocket-protocol)
- [Database Schema](#-database-schema)
- [Security](#-security)
- [Performance](#-performance)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

### 🔐 Authentication & Security
- ✅ **HttpOnly Cookie Authentication** - Secure token storage with XSS protection
- ✅ **Dual Auth Support** - Both cookie-based and Bearer token authentication
- ✅ **JWT Tokens** - Separate access and refresh tokens with configurable expiration
- ✅ **Google OAuth2** - Social authentication integration
- ✅ **Argon2 Password Hashing** - Modern password security via `pwdlib`
- ✅ **Security Headers** - Comprehensive security headers middleware
- ✅ **CORS Protection** - Configurable CORS with credentials support

### 💬 Real-time Communication
- ✅ **WebSocket Support** - Real-time bidirectional communication
- ✅ **Online Status** - Live online/offline status tracking
- ✅ **Group Messaging** - Multi-user group conversations
- ✅ **Private Messaging** - One-on-one chat support
- ✅ **Message Broadcasting** - Efficient message delivery via Redis pub/sub

### 🚀 Performance & Optimization
- ✅ **Connection Pooling** - Optimized PostgreSQL connection pool (20 connections)
- ✅ **Database Indexes** - Btree indexes for fast case-insensitive search
- ✅ **Response Compression** - GZip middleware for reduced bandwidth
- ✅ **Fast JSON** - ORJSON for high-performance serialization
- ✅ **uvloop** - Ultra-fast event loop (production only)
- ✅ **Request Timing** - Microsecond-precision performance monitoring

### 🛠️ Developer Experience
- ✅ **Admin Panel** - FastAdmin interface for database management
- ✅ **Auto Migrations** - Alembic with proper UUID handling
- ✅ **Development Scripts** - Database reset and user seeding
- ✅ **Comprehensive Tests** - Full test coverage with pytest
- ✅ **Type Safety** - Full type hints and Pydantic validation
- ✅ **Code Quality** - Ruff linting and formatting

---

## 🛠️ Tech Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Framework** | ![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi&logoColor=white) | High-performance async API framework |
| **WebSocket** | ![WebSocket](https://img.shields.io/badge/WebSocket-010101?logo=socket.io&logoColor=white) | Real-time bidirectional communication |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white) | Primary database with optimized indexes |
| **Cache/PubSub** | ![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white) | Pub/sub for scalable messaging |
| **ORM** | ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-29BEB0?logo=sqlalchemy&logoColor=white) | Async ORM for database operations |
| **Migrations** | ![Alembic](https://img.shields.io/badge/Alembic-9B59B6?logo=alembic&logoColor=white) | Database schema versioning |
| **Auth** | ![fastapi-users](https://img.shields.io/badge/fastapi--users-FF6B6B?logo=fastapi&logoColor=white) | JWT + OAuth2 authentication |
| **Server** | ![Uvicorn](https://img.shields.io/badge/Uvicorn-059669?logo=uvicorn&logoColor=white) | ASGI server with uvloop |
| **Admin** | ![FastAdmin](https://img.shields.io/badge/FastAdmin-8B5CF6?logo=admin&logoColor=white) | Admin panel interface |
| **Password** | ![pwdlib](https://img.shields.io/badge/pwdlib-Argon2-FF6B9D?logo=key&logoColor=white) | Modern password hashing |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Applications                      │
│              (Web, Mobile, Desktop Clients)                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTP/WebSocket
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    FastAPI Application                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Middleware  │  │   Routers    │  │  WebSocket   │       │
│  │  - CORS      │  │  - Auth      │  │  Manager     │       │
│  │  - Security  │  │  - Users      │  │  - Real-time │       │
│  │  - Timing    │  │  - Messages   │  │  - Status    │       │
│  │  - GZip      │  │  - Groups     │  │              │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└───────────┬──────────────────┬──────────────────┬───────────┘
            │                  │                  │
    ┌───────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐
    │  PostgreSQL  │  │    Redis     │  │   FastAdmin  │
    │  - Users     │  │  - Pub/Sub   │  │   - Admin    │
    │  - Messages  │  │  - Cache     │  │   - Views    │
    │  - Groups    │  │              │  │              │
    └──────────────┘  └──────────────┘  └──────────────┘
```

### Project Structure

```
realtime-chat-backend/
├── 📁 app/
│   ├── 📄 main.py              # FastAPI application entry point
│   ├── 📁 api/                  # API routes
│   │   ├── dependencies.py        # Auth & DB dependencies
│   │   └── v1/
│   │       ├── auth.py          # 🔐 JSON login with cookies
│   │       ├── oauth.py         # 🔗 Google OAuth endpoints
│   │       ├── users.py         # 👤 User management
│   │       ├── messages.py      # 💬 Message endpoints
│   │       ├── groups.py        # 👥 Group management
│   │       ├── contacts.py      # 📇 Contact management
│   │       ├── websocket.py     # 🔌 WebSocket endpoints
│   │       ├── upload.py        # 📤 File upload
│   │       └── router.py        # 🛣️ API router
│   ├── 📁 auth/                 # Authentication
│   │   ├── database.py          # User database adapter
│   │   ├── users.py             # User manager
│   │   └── oauth.py             # OAuth2 config
│   ├── 📁 core/                 # Core functionality
│   │   ├── config.py            # ⚙️ Settings
│   │   ├── security.py          # 🔒 JWT utilities
│   │   ├── utils.py             # 🛠️ Auth utilities
│   │   ├── websocket.py         # 🔌 WebSocket manager
│   │   ├── middleware.py        # 🛡️ Custom middleware
│   │   └── redis.py             # 📦 Redis connection
│   ├── 📁 db/                   # Database
│   │   └── base.py              # DB session & engine
│   ├── 📁 models/               # SQLAlchemy models
│   │   ├── user.py              # 👤 User model
│   │   ├── message.py           # 💬 Message model
│   │   ├── group.py             # 👥 Group models
│   │   └── contact.py           # 📇 Contact model
│   ├── 📁 schemas/              # Pydantic schemas
│   └── 📁 admin/                # Admin panel
│       ├── admin.py             # FastAdmin config
│       └── views/               # Admin views
├── 📁 alembic/                  # Database migrations
├── 📁 scripts/                  # Utility scripts
│   ├── reset_database.py        # 🔄 DB reset
│   └── seed_users.py           # 🌱 User seeding
└── 📁 tests/                    # Test suite
```

---

## 🚀 Quick Start

### Prerequisites

- 🐍 **Python 3.13+**
- 🐘 **PostgreSQL 17+**
- 🔴 **Redis 7+** (optional, recommended)
- 📦 **uv** package manager (recommended)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/Matnazar-Matnazarov/realtime-chat-backend.git
cd realtime-chat-backend

# 2. Install dependencies
make install

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Setup database
createdb chatdb
make migrate

# 5. Seed users
make seed-users

# 6. Start Redis (optional)
redis-server

# 7. Run application
make run
```

### 🎯 Quick Commands

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make migrate` | Run database migrations |
| `make seed-users` | Create admin and test users |
| `make run` | Start development server |
| `make test` | Run test suite |
| `make lint` | Check code quality |
| `make format` | Format code |
| `make reset-db` | Reset database |

### 🌐 Access Points

After starting the server, access:

- 🌐 **API**: http://localhost:8000
- 📚 **Swagger UI**: http://localhost:8000/docs
- 📖 **ReDoc**: http://localhost:8000/redoc
- ⚙️ **Admin Panel**: http://localhost:8000/admin
- ❤️ **Health Check**: http://localhost:8000/health

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file from `.env.example`:

```bash
# Application
DEBUG=False
APP_NAME=Realtime Chat API
APP_VERSION=1.0.0

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/chatdb

# Redis
REDIS_URL=redis://localhost:6379/0

# Security - Generate with: openssl rand -hex 32
SECRET_KEY=your-secret-key-here
REFRESH_SECRET_KEY=your-refresh-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (comma-separated, no spaces)
CORS_ORIGINS_STR=http://localhost:3000,http://localhost:5173

# OAuth2 (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# File Upload
ALLOWED_EXTENSIONS_STR=image/jpeg,image/png,image/gif,video/mp4
MAX_UPLOAD_SIZE=10485760
```

### 🔑 Generating Secrets

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate REFRESH_SECRET_KEY
openssl rand -hex 32
```

---

## 📚 API Documentation

### 🔐 Authentication Endpoints

#### Custom JSON Login (Cookie-based)
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user",
  "password": "pass"
}
```

**Response:**
- Sets `access_token` and `refresh_token` in HttpOnly cookies
- Returns tokens in response body for Bearer token usage

#### Token Refresh
```http
POST /api/v1/auth/refresh
```
- Uses refresh token from cookie or request body
- Returns new token pair

#### Logout
```http
POST /api/v1/auth/logout
```
- Clears all authentication cookies

#### OAuth2
```http
GET  /api/v1/oauth/google/authorize?redirect_url=...
GET  /api/v1/oauth/google/callback?code=...
GET  /api/v1/oauth/google/status
```

### 👤 User Endpoints

```http
GET    /api/v1/users/me
GET    /api/v1/users/search?query=admin&limit=20
GET    /api/v1/users/{user_id}
PATCH  /api/v1/users/me/online?is_online=true
```

### 💬 Message Endpoints

```http
POST   /api/v1/messages
GET    /api/v1/messages?receiver_id=...&limit=50
PATCH  /api/v1/messages/{message_id}/read
```

**Create Message:**
```json
{
  "content": "Hello!",
  "receiver_id": "user-uuid"  // For private message
}
// OR
{
  "content": "Hello!",
  "group_id": "group-uuid"     // For group message
}
```

### 👥 Group Endpoints

```http
POST   /api/v1/groups
GET    /api/v1/groups?limit=50
GET    /api/v1/groups/{group_id}
PATCH  /api/v1/groups/{group_id}
POST   /api/v1/groups/{group_id}/members?user_id=...
DELETE /api/v1/groups/{group_id}/members/{user_id}
```

### 📇 Contact Endpoints

```http
POST   /api/v1/contacts
GET    /api/v1/contacts
DELETE /api/v1/contacts/{contact_id}
```

### 📤 File Upload

```http
POST /api/v1/upload
Content-Type: multipart/form-data

file: [binary data]
```

---

## 🔌 WebSocket Protocol

### Connection

```javascript
const ws = new WebSocket(
  `ws://localhost:8000/api/v1/ws/${userId}?token=${accessToken}`
);
```

### Message Types

#### Client → Server

```json
// Join group
{"type": "join_group", "group_id": "uuid"}

// Leave group
{"type": "leave_group", "group_id": "uuid"}

// Heartbeat
{"type": "ping"}
```

#### Server → Client

```json
// New message
{
  "type": "message",
  "id": "uuid",
  "content": "Hello!",
  "sender_id": "uuid",
  "receiver_id": "uuid",
  "created_at": "2024-01-01T00:00:00",
  "sender": {...}
}

// Online status update
{
  "type": "online_status",
  "user_id": "uuid",
  "is_online": true
}

// Heartbeat response
{"type": "pong"}

// Error
{"type": "error", "message": "Error description"}
```

## 🔐 Security Features

### Authentication

- ✅ **HttpOnly Cookies** - Tokens stored in HttpOnly cookies (XSS protection)
- ✅ **Secure Flag** - Cookies use `Secure` flag in production
- ✅ **SameSite Protection** - `SameSite=Lax` for CSRF protection
- ✅ **Separate Secrets** - Different keys for access and refresh tokens
- ✅ **Token Expiration** - Configurable expiration times

### Password Security

- ✅ **Argon2 Hashing** - Modern password hashing algorithm
- ✅ **No Plaintext Storage** - Passwords never stored in plaintext

### HTTP Security Headers

- ✅ `X-Content-Type-Options: nosniff`
- ✅ `X-Frame-Options: DENY`
- ✅ `X-XSS-Protection: 1; mode=block`
- ✅ `Referrer-Policy: strict-origin-when-cross-origin`
- ✅ `Strict-Transport-Security` (production only)

### Additional Security

- ✅ **CORS Protection** - Configurable allowed origins
- ✅ **SQL Injection Protection** - SQLAlchemy ORM
- ✅ **File Upload Validation** - Size and MIME type checks
- ✅ **Input Validation** - Pydantic schemas

---

## ⚡ Performance Optimizations

### Database

- ✅ **Connection Pooling** - 20 connections, 10 overflow
- ✅ **Connection Health Checks** - `pool_pre_ping=True`
- ✅ **Connection Recycling** - 1 hour recycle time
- ✅ **Optimized Indexes** - Btree indexes for fast search
- ✅ **Partial Indexes** - Index only active users

### Response Optimization

- ✅ **GZip Compression** - Responses > 1KB compressed
- ✅ **ORJSON** - Fast JSON serialization
- ✅ **Response Caching** - Redis for frequently accessed data

### Event Loop

- ✅ **uvloop** - Ultra-fast event loop (production)
- ✅ **Async/Await** - Fully async implementation

### Monitoring

- ✅ **Request Timing** - `X-Process-Time` header (microsecond precision)
- ✅ **Performance Metrics** - Built-in timing middleware

---

## 🧪 Testing

### Run Tests

```bash
# All tests
make test

# With coverage
make test-cov

# Specific test file
uv run pytest tests/test_auth.py -v
```

### Test Structure

```
tests/
├── conftest.py        # Pytest fixtures
├── test_auth.py       # Authentication tests
├── test_users.py      # User endpoint tests
├── test_messages.py   # Message tests
├── test_groups.py     # Group tests
├── test_contacts.py   # Contact tests
├── test_upload.py     # File upload tests
└── test_health.py     # Health check tests
```

---

## 📦 Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY` and `REFRESH_SECRET_KEY`
- [ ] Configure production `DATABASE_URL`
- [ ] Configure production `REDIS_URL`
- [ ] Set proper `CORS_ORIGINS_STR`
- [ ] Configure SSL/TLS certificates
- [ ] Set up file storage (S3, etc.)
- [ ] Configure logging and monitoring
- [ ] Set up backup strategy

### Using Uvicorn

```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4
```

### Using Gunicorn

```bash
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## 🐛 Troubleshooting

### Common Issues

<details>
<summary><b>Configuration Parsing Errors</b></summary>

**Problem**: `error parsing value for field "CORS_ORIGINS"`

**Solution**: Use comma-separated values without spaces:
```bash
# ✅ Correct
CORS_ORIGINS_STR=http://localhost:3000,http://localhost:5173

# ❌ Wrong
CORS_ORIGINS_STR=http://localhost:3000, http://localhost:5173
```

</details>

<details>
<summary><b>Database Connection Issues</b></summary>

- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Check `DATABASE_URL` format: `postgresql+asyncpg://user:pass@host:port/dbname`
- Verify database exists: `psql -U postgres -l`
- Check user permissions

</details>

<details>
<summary><b>WebSocket Connection Issues</b></summary>

- Verify URL: `ws://localhost:8000/api/v1/ws/{user_id}?token=...`
- Check CORS settings
- Ensure token is valid and not expired
- Check server logs for errors

</details>

<details>
<summary><b>Cookie Authentication Issues</b></summary>

- Ensure `withCredentials: true` in frontend
- Check CORS `allow_credentials=True`
- Verify cookie domain/path settings
- In development, use `localhost` or `127.0.0.1`

</details>

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. 💻 Make your changes
4. ✅ Add tests
5. 🧹 Run tests and linting (`make test && make lint`)
6. 📝 Commit your changes (`git commit -m 'feat: add amazing feature'`)
7. 🚀 Push to the branch (`git push origin feature/amazing-feature`)
8. 🔄 Open a Pull Request

---

## 📧 Support

For questions, issues, or feature requests:

- 📮 Open an [Issue](https://github.com/Matnazar-Matnazarov/realtime-chat-backend/issues)
- 💬 Start a [Discussion](https://github.com/Matnazar-Matnazarov/realtime-chat-backend/discussions)

---

<div align="center">

**Built with ❤️ using FastAPI**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)

⭐ Star this repo if you find it helpful!

</div>

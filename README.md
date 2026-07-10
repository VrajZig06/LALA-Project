# LALA Backend API

A clean, modular, and high-performance FastAPI boilerplate built using SQLAlchemy 2.x (ORM), Alembic (migrations), PostgreSQL, Pydantic Settings, Celery (background tasks), Redis (caching/message broker), and Firebase Cloud Messaging (FCM).

---

## 🚀 Key Features

- **FastAPI**: Modern, fast (high-performance) web framework for building APIs.
- **SQLAlchemy 2.0 & Alembic**: Database migrations and ORM supporting modular versioning.
- **WebRTC Video Calling**: Real-time video/audio signaling via WebSockets with a robust connection manager ([app/services/video_service.py](file:///Users/ztlab141/Desktop/LALA%20Project/app/services/video_service.py)).
- **Firebase Cloud Messaging (FCM)**: Push notification service integrated using the Firebase Admin SDK.
- **Celery Tasks & Redis**: Asynchronous task scheduling and background workers (with scheduled beats) configured in [app/celery/celery_worker.py](file:///Users/ztlab141/Desktop/LALA%20Project/app/celery/celery_worker.py).
- **Google SSO Authentication**: Google Sign-In and Social Signup flow.
- **Brevo Email Service**: Sending registration verification OTPs and password reset links.
- **LlamaParse**: Integrated for advanced document parsing and processing.
- **Structured Architecture**: Clean-architecture inspired separation of concerns.

---

## 📂 Project Structure

```text
├── alembic/                # Alembic migration configuration and environment
│   ├── env.py              # Environment configuration script
│   └── script.py.mako      # Template for migrations
├── alembic.ini             # Alembic INI configuration file
├── docker-compose.yml      # Local services (Redis, RedisInsight) config
├── firebase-credentials.json # Firebase Admin SDK credential key (git-ignored)
├── app/
│   ├── api/                # API Routers & Controllers (e.g. video_routes.py, user_routes.py)
│   ├── celery/             # Celery background tasks & workers
│   │   └── celery_worker.py
│   ├── common/             # Utilities and shared helpers
│   ├── core/               # Configuration settings, custom logging, exception handlers
│   ├── db/                 # Database base class, session, models, and migrations
│   │   ├── base.py         # SQLAlchemy Base declaration
│   │   ├── session.py      # Database session engines
│   │   ├── models/         # SQLAlchemy DB Models (e.g. user.py, role.py, call_room.py)
│   │   ├── seeds/          # Database seeding scripts (e.g. role_seeds.py)
│   │   └── versions/       # Migration version files (stored here instead of alembic/versions)
│   ├── repository/         # Data Access Layer (Repository pattern implementation)
│   ├── schema/             # Pydantic schemas (Request / Response validation)
│   ├── services/           # Business logic layer (e.g. user_service.py, video_service.py)
│   └── main.py             # FastAPI entrypoint
├── .env                    # Active environment selector
├── .env.dev                # Development environment secrets/config
├── .env.prod               # Production environment secrets/config
├── requirements.txt        # Python dependency list
└── README.md               # This README file
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- PostgreSQL server (running locally or remotely)
- Docker Desktop (for running Redis locally)

### 2. Clone and Initialize Virtual Environment
Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows
```

### 3. Install Dependencies
Install all required libraries using:
```bash
pip install -r requirements.txt
```

### 4. Configuration

#### Environment Selection
The [.env](file:///Users/ztlab141/Desktop/LALA%20Project/.env) file determines which environment config is active:
```env
ENV = "dev"
```

#### Secrets & Credentials
Configure database connections, JWT details, external APIs, and Redis server credentials in the environment files ([.env.dev](file:///Users/ztlab141/Desktop/LALA%20Project/.env.dev) / `.env.prod`):
```env
DATABASE_URL = "postgresql://postgres:<password>@localhost:5432/lala_db"
JWT_SECRET_KEY = "your-secret-key"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRY = 10
JWT_REFRESH_TOKEN_EXPIRY = 1140

# BREVO Email Service
BREVO_API_KEY = "your-brevo-api-key"
BREVO_SENDER_EMAIL = "your-sender-email"
BREVO_SENDER_NAME = "your-sender-name"

# Google Auth
GOOGLE_CLIENT_ID = "your-google-client-id"

# LlamaParse API Key
LLAMAPARSE_API_KEY = "your-llamaparse-api-key"

# Redis Server URL
REDIS_SERVER_URL = "redis://localhost:6379/0"
```

#### Firebase SDK Setup
To enable push notifications, place your Firebase credentials file in the project root as [firebase-credentials.json](file:///Users/ztlab141/Desktop/LALA%20Project/firebase-credentials.json).

---

## 🐋 Local Infrastructure (Redis & RedisInsight)

A [docker-compose.yml](file:///Users/ztlab141/Desktop/LALA%20Project/docker-compose.yml) file is provided to quickly run a local Redis server and RedisInsight container:

```bash
docker compose up -d
```
- **Redis Server**: Port `6379`
- **RedisInsight (GUI)**: Access at `http://localhost:8001`

---

## 🗄️ Database Migrations (Alembic)

Migrations are stored in [app/db/versions/](file:///Users/ztlab141/Desktop/LALA%20Project/app/db/versions/).

- **Create a New Migration:** (Make sure any new SQLAlchemy models are imported in [app/db/models/\_\_init\_\_.py](file:///Users/ztlab141/Desktop/LALA%20Project/app/db/models/__init__.py))
  ```bash
  alembic revision --autogenerate -m "Add your migration description"
  ```
- **Apply Migrations to DB:**
  ```bash
  alembic upgrade head
  ```
- **Revert Last Migration:**
  ```bash
  alembic downgrade -1
  ```

---

## 🌱 Database Seeding

To populate the database with default roles (`admin`, `manager`, `employee`, and `employe`):

```bash
python -m app.db.seeds.role_seeds
```

---

## 🏃 Running the Application

### 1. Start the FastAPI Development Server
```bash
fastapi dev app/main.py
```
*Alternatively, run using Uvicorn directly:*
```bash
uvicorn app.main:app --reload
```
The server will be available at `http://127.0.0.1:8000`.

### 2. Start Celery Worker & Scheduler
For asynchronous tasks, start the Celery worker and beat scheduler in separate terminal sessions (or in the background):

- **Celery Worker:**
  ```bash
  celery -A app.celery.celery_worker.celery worker --loglevel=info
  ```
- **Celery Beat (Scheduler):**
  ```bash
  celery -A app.celery.celery_worker.celery beat --loglevel=info
  ```

---

## 📖 API Documentation & Routes

- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc UI:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Key Endpoints:
- **Google OAuth Login / Sign-up:** Serves `static/google_signup.html` at `http://127.0.0.1:8000/` (Root path).
- **Authentication Routes (`/api/v1/users`):**
  - `/signup` (Register)
  - `/verify-otp` (OTP verification via Email)
  - `/user-login` (Email/password login)
  - `/google-auth` (Google Sign-In)
  - `/forgot-password` / `/validate-password` (Password recovery)
  - `/refresh-token` (Acquire new access token)
- **Video Calling Room Signaling (`/api/v1/video`):**
  - `/rooms` [POST] - Create call room
  - `/rooms` [GET] - List active call rooms
  - `/rooms/{room_code}` [GET] - Get room details
  - `/ws/{room_code}` [WS] - WebSocket signaling endpoint (Requires `token` query param)
- **Push Notifications:** `/send-notification` [POST] - Send FCM push notification.

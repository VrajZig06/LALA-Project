# LALA Backend API

A clean, modular FastAPI boilerplate built using SQLAlchemy 2.x (ORM), Alembic (migrations), PostgreSQL, and Pydantic Settings.

## 🚀 Key Features
- **FastAPI**: Modern, fast (high-performance), web framework for building APIs.
- **SQLAlchemy 2.0**: Next-generation database toolkit and Object Relational Mapper for Python.
- **Alembic**: Database migration tool configured to store migrations within the modular directory structure.
- **Pydantic v2**: High-speed data validation and settings management.
- **Structured Architecture**: Clean-architecture inspired separation of concerns.

---

## 📂 Project Structure

```text
├── alembic/                # Alembic migration configuration and environment
│   ├── env.py              # Environment configuration script
│   └── script.py.mako      # Template for migrations
├── alembic.ini             # Alembic INI configuration file
├── app/
│   ├── api/                # API Routers & Controllers
│   ├── common/             # Utilities and shared helpers
│   ├── core/               # Configuration settings, custom logging, exception handlers
│   ├── db/                 # Database base class, session, and migrations
│   │   ├── base.py         # SQLAlchemy Base declaration
│   │   ├── session.py      # Database session engines
│   │   ├── models/         # SQLAlchemy DB Models (e.g. user.py)
│   │   └── versions/       # Migration version files (stored here instead of alembic/versions)
│   ├── repository/         # Data Access Layer (Repository pattern implementation)
│   ├── schema/             # Pydantic schemas (Request / Response validation)
│   ├── services/           # Business logic layer
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
1. The `.env` file determines which environment config is active:
   ```env
   ENV = "dev"
   ```
2. Configure database connections and JWT details in the environment files ([.env.dev](file:///Users/ztlab141/Desktop/LALA%20Project/.env.dev) / `.env.prod`):
   ```env
   DATABASE_URL = "postgresql://postgres:<password>@localhost:5432/lala_db"
   JWT_SECRET_KEY = "your-secret-key"
   JWT_ALGORITHM = "HS256"
   JWT_ACCESS_TOKEN_EXPIRY = 10
   JWT_REFRESH_TOKEN_EXPIRY = 1140
   ```

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

## 🏃 Running the Application

To start the FastAPI development server:

```bash
fastapi dev app/main.py
```
*Alternatively, you can run using Uvicorn directly:*
```bash
uvicorn app.main:app --reload
```

The server will be available at `http://127.0.0.1:8000`.

### 📖 API Documentation
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc UI:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

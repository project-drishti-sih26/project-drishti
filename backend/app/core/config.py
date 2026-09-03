"""
FILE: backend/app/core/config.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This is the central configuration file for the entire backend application.
    It defines a `Settings` class using Pydantic's BaseSettings that reads
    configuration values from environment variables and the `.env` file.
    All other files import from this single source of truth.

📌 WHY IS THIS FILE NEEDED?
    Hardcoding database URLs, secret keys, or ports in code is a terrible
    practice. If we push to GitHub with a real secret, it's a security breach.
    By centralizing config here, we can switch from local dev DB to production
    DB just by changing the `.env` file — no code changes needed.
    This is the standard 12-Factor App principle.

📌 WHAT TO IMPLEMENT HERE:
    Create a `Settings(BaseSettings)` class with these fields:

    APPLICATION SETTINGS:
    - PROJECT_NAME: str = "Project Drishti API"
    - VERSION: str = "1.0.0"
    - API_V1_STR: str = "/api/v1"
      (This prefix is prepended to all our API routes, e.g., /api/v1/transactions)

    DATABASE SETTINGS:
    - DATABASE_URL: str
      Default: "postgresql://drishti_user:drishti_secret@localhost:5432/drishti_db"
      This is the SQLAlchemy-format connection string for PostgreSQL.
      For local dev without Docker: can also use "sqlite:///./drishti_local.db"

    ML TRIGGER SETTINGS:
    - MULE_TRIGGER_AMOUNT: float = 50000.0
      This is the ₹ threshold above which an incoming mule transaction
      triggers the ML prediction pipeline. Centralizing it here means
      we can change the threshold without touching business logic code.

    SECURITY SETTINGS:
    - SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_PLEASE"
      Used for JWT token signing. MUST be overridden in .env for production.
    - ALGORITHM: str = "HS256"
    - ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    CORS SETTINGS:
    - CORS_ORIGINS: List[str] = [
        "http://localhost:5173",   # Vite dev server (Role 3 & 4 Frontend)
        "http://localhost:3000",   # Alternate React port
        "http://127.0.0.1:5173",
      ]
      These are the frontend URLs allowed to make cross-origin requests.

    Inside the class, add:
    class Config:
        env_file = ".env"        # Reads from .env file automatically
        case_sensitive = True

    After the class definition, create a singleton instance:
    `settings = Settings()`
    This is what all other files will import:
    `from app.core.config import settings`

📌 HOW IT CONNECTS TO OTHER FILES:
    - main.py imports `settings` for CORS origins and API prefix.
    - db/session.py imports `settings.DATABASE_URL` for DB connection.
    - services/trigger_service.py imports `settings.MULE_TRIGGER_AMOUNT`.
    - core/security.py imports SECRET_KEY and ALGORITHM for JWT tokens.

📌 LIBRARIES TO USE:
    - pydantic_settings (BaseSettings)
    - typing (List)
"""

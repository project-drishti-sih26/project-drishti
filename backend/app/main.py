"""
FILE: backend/app/main.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This is the main entrypoint of the entire FastAPI backend application.
    When you run `uvicorn app.main:app`, Python starts HERE.
    This file creates the FastAPI app instance, attaches all middleware
    (CORS, logging), registers all API routers, and connects the database.

📌 WHY IS THIS FILE NEEDED?
    Without this file, the server cannot start. Every HTTP request and
    WebSocket connection flows through this app instance. It also
    handles application startup/shutdown lifecycle events — for example,
    running DB migrations or creating initial tables on server startup.

📌 WHAT TO IMPLEMENT HERE:
    1.  Import FastAPI and create the `app = FastAPI(...)` instance.
        Set metadata like title="Project Drishti API", version="1.0.0",
        and description for the Swagger docs at /docs.

    2.  Add CORSMiddleware — this is CRITICAL for the React frontend
        (running on http://localhost:5173) to call this backend without
        getting "CORS blocked" errors in the browser.
        Allow origins from `settings.CORS_ORIGINS` (defined in config.py).
        Allow all methods (GET, POST, PUT, DELETE) and all headers.

    3.  Include the API router from `app.api.router` with a prefix of
        `settings.API_V1_STR` which will be "/api/v1".
        This means all endpoints will be at /api/v1/...

    4.  Add startup event handler using @app.on_event("startup"):
        - Import Base and engine from the db module.
        - Call `Base.metadata.create_all(bind=engine)` to auto-create
          all database tables if they don't exist yet.
        - This is the dev-friendly approach. In production, use Alembic migrations.

    5.  Add a simple root health-check endpoint:
        GET / → returns {"status": "Drishti API is live 🚀", "version": "1.0.0"}
        This lets Role 6 (DevOps) verify the server is up during integration.

📌 HOW IT CONNECTS TO OTHER FILES:
    - Imports `settings` from app.core.config for CORS origins and API prefix.
    - Imports `api_router` from app.api.router (which assembles all sub-routers).
    - Imports `Base` and `engine` from app.db.session for table creation.

📌 LIBRARIES TO USE:
    - fastapi (FastAPI, Depends)
    - fastapi.middleware.cors (CORSMiddleware)
    - uvicorn (for running, not imported here but used in CLI)
"""

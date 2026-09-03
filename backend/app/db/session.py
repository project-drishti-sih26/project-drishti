"""
FILE: backend/app/db/session.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This file sets up the SQLAlchemy database engine and session factory.
    It also provides the FastAPI dependency function `get_db()` that gives
    every API endpoint its own clean database session per request.

📌 WHY IS THIS FILE NEEDED?
    Database connections are expensive. We should NOT open a new connection
    for every single DB query, and we should NOT share one global connection
    across all requests (that causes race conditions and data corruption).
    SQLAlchemy's connection pool and session factory solve this problem:
    - The `engine` manages a pool of actual DB connections.
    - Each HTTP request gets its own `SessionLocal()` session from the pool.
    - When the request finishes (success or error), the session is returned
      to the pool via the `finally` block in `get_db()`.

📌 WHAT TO IMPLEMENT HERE:

    1. CREATE THE ENGINE:
       from sqlalchemy import create_engine
       from app.core.config import settings

       engine = create_engine(
           settings.DATABASE_URL,
           pool_pre_ping=True,   # Tests connection health before using it
           echo=False            # Set to True during debugging to log all SQL
       )

       Note: For SQLite (local dev without Docker), add:
       connect_args={"check_same_thread": False}
       This is only needed for SQLite, not for PostgreSQL.

    2. CREATE THE SESSION FACTORY:
       from sqlalchemy.orm import sessionmaker

       SessionLocal = sessionmaker(
           autocommit=False,   # We manually commit transactions for data safety
           autoflush=False,    # We manually flush so we control when SQL is sent
           bind=engine
       )

    3. CREATE THE `get_db()` DEPENDENCY:
       This is a Python generator function used as a FastAPI dependency.

       def get_db():
           db = SessionLocal()
           try:
               yield db          # FastAPI injects this `db` into the endpoint
           finally:
               db.close()        # Always close, even if the request raised an error

       Usage in any endpoint:
       @router.post("/transactions")
       def create_transaction(db: Session = Depends(get_db)):
           # `db` is a fresh SQLAlchemy session for this request
           pass

📌 HOW IT CONNECTS TO OTHER FILES:
    - config.py provides DATABASE_URL.
    - main.py imports `engine` and `Base` to create tables on startup.
    - ALL endpoint files import `get_db` as a Depends() dependency.
    - Service files receive `db` as a parameter from the endpoint functions.

📌 LIBRARIES TO USE:
    - sqlalchemy (create_engine)
    - sqlalchemy.orm (sessionmaker, Session)
    - app.core.config (settings)
"""

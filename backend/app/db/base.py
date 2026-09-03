"""
FILE: backend/app/db/base.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This file creates the single shared SQLAlchemy `Base` declarative class.
    All database model classes (Account, Transaction, Case, PhysicalLocation)
    inherit from this Base to register themselves with SQLAlchemy's ORM system.

📌 WHY IS THIS FILE NEEDED?
    SQLAlchemy needs ONE central `Base` object that knows about all models.
    When we call `Base.metadata.create_all(engine)` in main.py, SQLAlchemy
    looks at ALL classes that inherited from this Base and creates their
    corresponding tables in the database. If models defined their own separate
    Base, `create_all` would miss them and tables would not be created.

📌 WHAT TO IMPLEMENT HERE:
    This file is intentionally very simple — just 3 lines:

    from sqlalchemy.orm import declarative_base
    Base = declarative_base()

    That's it. The complexity lives in the model files that import Base.

📌 HOW IT CONNECTS TO OTHER FILES:
    - ALL model files (account.py, transaction.py, location.py, case.py)
      import `Base` from here: `from app.db.base import Base`
    - db/session.py imports `Base` for the create_all call.
    - main.py startup event imports `Base` to call `Base.metadata.create_all()`.

📌 LIBRARIES TO USE:
    - sqlalchemy.orm (declarative_base)

📌 IMPORTANT: Do NOT import any model files here. That would create
    circular import errors. The model files import FROM base.py, not the
    other way around.
"""

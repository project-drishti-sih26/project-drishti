"""
FILE: backend/app/core/security.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This file handles all authentication and authorization logic for the API.
    In a police/law enforcement intelligence system, not everyone should be
    able to access predictions or post transactions. This file provides
    JWT (JSON Web Token) creation and verification utilities.

📌 WHY IS THIS FILE NEEDED?
    Project Drishti handles sensitive law enforcement data. The API should
    not be open to the public internet. JWT tokens let us authenticate
    police officers/operators: they log in once, get a token, and include
    that token in every subsequent API request header.
    The RBAC (Role-Based Access Control) concept from the blueprint lives here.

📌 WHAT TO IMPLEMENT HERE:

    1. PASSWORD HASHING UTILITIES:
       - Use `passlib` with bcrypt scheme.
       - `hash_password(plain_password: str) -> str`
         Takes a plain text password, returns a bcrypt hash.
         Never store plain passwords in the database.
       - `verify_password(plain_password: str, hashed_password: str) -> bool`
         Verifies a plain password against its stored hash during login.

    2. JWT TOKEN CREATION:
       - `create_access_token(data: dict, expires_delta: timedelta = None) -> str`
         Creates a signed JWT token.
         - Add an expiry claim (`exp`) to the payload.
         - Sign with `settings.SECRET_KEY` using `settings.ALGORITHM` (HS256).
         - Returns the encoded token string.
         - Example usage: called when a user successfully logs in.

    3. JWT TOKEN VERIFICATION:
       - `verify_token(token: str) -> dict`
         Decodes and validates a JWT token.
         - Raises `HTTPException(401)` if token is invalid or expired.
         - Returns the decoded payload dict on success.

    4. FASTAPI DEPENDENCY (for protected routes):
       - `get_current_user(token: str = Depends(oauth2_scheme)) -> dict`
         This is a FastAPI dependency function that can be injected into
         any protected endpoint using `Depends(get_current_user)`.
         It extracts the token from the Authorization header and calls
         `verify_token()` to validate it.

📌 HOW IT CONNECTS TO OTHER FILES:
    - config.py provides SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES.
    - The `get_current_user` dependency will be imported by any endpoint
      that needs to be protected (e.g., POST /transactions).

📌 LIBRARIES TO USE:
    - passlib[bcrypt] (CryptContext)
    - python-jose[cryptography] (jwt)
    - fastapi (Depends, HTTPException, status)
    - fastapi.security (OAuth2PasswordBearer)
    - datetime (datetime, timedelta)

📌 NOTE FOR HACKATHON:
    During the hackathon demo, you can skip enforcing auth on all routes
    to save time. But keep this file ready — add `Depends(get_current_user)`
    to sensitive routes before the final presentation if time permits.
    The judges will be impressed that auth is architecturally in place.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import create_access_token, Token, MOCK_USERS_DB
from app.api.router import api_router
from app.db.base import Base
from app.db.session import engine
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # Ensure all ORM models are registered with Base before creating tables
    from app.models.account import Account
    from app.models.transaction import Transaction
    from app.models.case import Case
    from app.models.location import PhysicalLocation
    Base.metadata.create_all(bind=engine)

@app.post("/api/v1/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = MOCK_USERS_DB.get(form_data.username)
    if not user or user["hashed_password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

from app.api.endpoints import websockets

app.include_router(api_router, prefix="/api/v1")
app.include_router(websockets.router, prefix="/ws", tags=["websockets"])

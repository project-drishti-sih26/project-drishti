import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# OAuth2 scheme setup for FastAPI Swagger UI and token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

# Hardcoded MVP mock database of Nodal Officers
# Passwords should normally be hashed using passlib!
MOCK_USERS_DB = {
    "officer1": {
        "username": "officer1",
        "full_name": "Rajesh Kumar",
        "hashed_password": "fakehashedpassword123", # Let's assume this is the hash for "password"
        "role": "nodal_officer"
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    username: str
    full_name: str
    role: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = MOCK_USERS_DB.get(username)
    if user is None:
        raise credentials_exception
        
    return user

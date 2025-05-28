from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
import secrets
import bcrypt
from typing import Optional
from core.config import JWT_SECRET

# Use your secret key and algorithm
SECRET_KEY = JWT_SECRET
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # endpoint to get token

class User(BaseModel):
    username: str
    email: str | None = None
    # Add other user fields as needed

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
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
        # Optionally, retrieve user from DB here if needed
        user = User(username=username)
    except JWTError:
        raise credentials_exception
    return user

def generate_otp(otp: str = '') -> str:
    if len(otp) == 5:
        return otp
    random_i = str(secrets.randbelow(10))
    if random_i not in otp and not (not otp and random_i == '0'):
        otp += random_i
    return generate_otp(otp)

async def get_hashed_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=10)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')
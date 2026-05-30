import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY", "74ccbcda0428c7e9f3e619e94e23b0a102dc63bbb7694ec0b38e4e696343dded")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 14

def create_access_token(*, user_id: str, expires_delta: Optional[timedelta] = None) -> str: #function to create the short lives access token
    to_encode = {"sub" : str(user_id), "type": "access"}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp" : expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)

def create_refresh_token(*, user_id: str, expires_delta: Optional[timedelta] = None) ->str:
    to_encode = {"sub":str(user_id), "type": "refresh"}
    expire = datetime.utcnow() +(expires_delta or timedelta(days = REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)


def decode_token(token : str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])



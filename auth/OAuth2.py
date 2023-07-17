from typing import Optional
from datetime import datetime, timedelta
from jose import jwt

# Load env
from dotenv import load_dotenv
import os

load_dotenv()


# Get the Secret Key from the .env file
SECRET_KEY = os.environ.get("OAUTH2_SECRET_KEY")
ALGORITHM = "HS256"


# A function to create a token used for authentication, contain loggedin user details
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

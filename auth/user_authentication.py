from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import HTTPException, Depends, status, APIRouter
from sqlalchemy.orm import Session
from db.db import get_db
from jose import jwt, JWTError
from db.models import Users
from auth.hashing import Hash
from auth.OAuth2 import create_access_token
import os

candidate_oauth2_schema = OAuth2PasswordBearer(
    tokenUrl="/user/login", scheme_name="User Authentication"
)

SECRET_KEY = os.environ.get("OAUTH2_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_loggedin_user(
    token: str = Depends(candidate_oauth2_schema), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # Fetching the user details from the databse.
    user = db.query(Users).filter(Users.username == username).first()
    if user is None:
        raise credentials_exception
    return user


# Route defined for user login
router = APIRouter(tags=["Authentication"])


@router.post("/user/login", description="User login")
def login(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(Users).filter(Users.username == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials"
        )
    if not Hash.verify(user.password, request.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect Password"
        )
    access_token = create_access_token(data={"username": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.userid,
        "username": user.username,
    }

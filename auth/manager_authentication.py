from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status, APIRouter
from auth.OAuth2 import create_access_token
from jose import jwt, JWTError
import os


manager_oauth2_schema = OAuth2PasswordBearer(
    tokenUrl="/manager/login", scheme_name="Manager Authentication"
)
SECRET_KEY = os.environ.get("OAUTH2_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Used as a middlware for authorizing the Manager level routes
def manager_login(token: str = Depends(manager_oauth2_schema)):
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
    return username


# Route for manger login
router = APIRouter(tags=["Authentication"])


@router.post("/manager/login", description="Manager login")
def login(request: OAuth2PasswordRequestForm = Depends()):
    username = request.username
    password = request.password

    if username != os.environ.get("MANAGER_USERNAME") or password != os.environ.get(
        "MANAGER_PASSOWRD"
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username and Password not matched",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"username": username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": username,
    }

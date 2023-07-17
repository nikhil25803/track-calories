from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session
from db.db import get_db
from db.schema import UserBase, UserUpdate, UserDisplay
from controllers import user_controller
from auth.user_authentication import get_loggedin_user


# User routes initialization
router = APIRouter(prefix="/user", tags=["User Level Permissions"])


@router.post("", description="Create a new user", response_model=UserDisplay)
async def create_user(request: UserBase, db: Session = Depends(get_db)):
    response = user_controller.create_user(db, request)
    return response


@router.get(
    "/{username}", description="Get current user details", response_model=UserDisplay
)
async def get_user(
    username: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_loggedin_user),
):
    response = user_controller.user_detail(db, username, current_user)
    return response


@router.put(
    "/{username}", description="Update current user details", response_model=UserDisplay
)
async def update_user(
    request: UserUpdate,
    username: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_loggedin_user),
):
    response = user_controller.update_user(username, db, request, current_user)
    return response


@router.delete("/{username}", description="Delete the user")
async def delete_user(
    username: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_loggedin_user),
):
    response = user_controller.delete_user(username, db, current_user)
    return response

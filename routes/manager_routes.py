from fastapi import APIRouter, Depends, HTTPException, status
import os
from controllers import admin_controllers
from auth.manager_authentication import manager_login
from db.db import get_db
from sqlalchemy.orm.session import Session
from db.schema import UserUpdate, UserBase, UserDisplay
from controllers import user_controller
from fastapi_pagination import Page, paginate


router = APIRouter(prefix="/manager", tags=["Manager Level Permission"])


# Fetching the manager's username from the .env file
admin_username = os.environ.get("MANAGER_USERNAME")


# A function to validate manager and loggedin user
def validation(current_user):
    if admin_username != current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/user/all", description="Get all the users", response_model=Page[UserDisplay]
)
async def get_all_users(
    current_user=Depends(manager_login), db: Session = Depends(get_db), name: str = None
):
    validation(current_user)
    response = admin_controllers.get_all_users(db, name)
    return paginate(response)


@router.post("/user/create", description="Create an user", response_model=UserDisplay)
async def create_user(
    request: UserBase,
    db: Session = Depends(get_db),
    current_user=Depends(manager_login),
):
    validation(current_user)
    response = user_controller.create_user(db, request)
    return response


@router.get(
    "/user/{userid}", description="Get an user bu userid", response_model=UserDisplay
)
async def get_an_user(
    userid: int, current_user=Depends(manager_login), db: Session = Depends(get_db)
):
    validation(current_user)
    response = admin_controllers.get_an_user(userid, db)
    return response


@router.put("/user/{userid}", description="Update an user with userid provided")
async def update_an_user(
    userid: int,
    request: UserUpdate,
    current_user=Depends(manager_login),
    db: Session = Depends(get_db),
):
    validation(current_user)
    response = admin_controllers.update_an_user(userid, db, request)
    return response


@router.delete("/user/{userid}", description="Delete an user with userid provided")
async def delete_an_user(
    userid: int,
    db: Session = Depends(get_db),
    current_user=Depends(manager_login),
):
    validation(current_user)
    response = admin_controllers.delete_an_user(userid, db)
    return response

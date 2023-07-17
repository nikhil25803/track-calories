from fastapi import APIRouter, Depends, HTTPException, status
from auth.admin_authentication import admin_login
from db.schema import (
    UserBase,
    UserUpdate,
    EntryBaseAdminUpdate,
    UserDisplay,
    EntryDispay,
)
from sqlalchemy.orm.session import Session
from controllers import admin_controllers, user_controller
from db.db import get_db
from db.schema import EntryBaseAdmin
import os
from fastapi_pagination import Page, paginate

# Defining router for the admins
router = APIRouter(prefix="/admin", tags=["Admin Level Permissions"])

# Fetchning the Admin username from the .env file for authentication purpose
admin_username = os.environ.get("ADMIN_USERNAME")


# A function to validate the current user - does the loggedin user's username match with the admin username or not
def validation(current_user):
    if admin_username != current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials |",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Admin CRUD on Users
@router.get(
    "/user/all", description="Get all the users", response_model=Page[UserDisplay]
)
async def get_all_users(
    current_user=Depends(admin_login), db: Session = Depends(get_db), name: str = None
):
    validation(current_user)
    response = admin_controllers.get_all_users(db, name)
    return paginate(response)


@router.post("/user/create", description="Create an user")
async def create_user(
    request: UserBase, db: Session = Depends(get_db), current_user=Depends(admin_login)
):
    validation(current_user)
    response = user_controller.create_user(db, request)
    return response


@router.get("/user/{userid}", description="Get an user bu userid")
async def get_an_user(
    userid: int, current_user=Depends(admin_login), db: Session = Depends(get_db)
):
    validation(current_user)
    response = admin_controllers.get_an_user(userid, db)
    return response


@router.put("/user/{userid}", description="Update an user with userid provided")
async def update_an_user(
    userid: int,
    request: UserUpdate,
    current_user=Depends(admin_login),
    db: Session = Depends(get_db),
):
    validation(current_user)
    response = admin_controllers.update_an_user(userid, db, request)
    return response


@router.delete("/user/{userid}", description="Delete an user with userid provided")
async def delete_an_user(
    userid: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_login),
):
    validation(current_user)
    response = admin_controllers.delete_an_user(userid, db)
    return response


# Admin CRUD on Entries
@router.get(
    "/entry/all",
    description="Get all the enteries as an admin",
    response_model=Page[EntryDispay],
)
async def get_all_entries(
    current_user=Depends(admin_login),
    db: Session = Depends(get_db),
    is_achieved: bool = None,
):
    validation(current_user)
    response = admin_controllers.get_entries(db, is_achieved)
    return paginate(response)


@router.post("/entry/create", description="Create an entry for a user")
async def create_an_entry(
    request: EntryBaseAdmin,
    current_user=Depends(admin_login),
    db: Session = Depends(get_db),
):
    validation(current_user)
    response = admin_controllers.create_entry(request, db)
    return response


@router.get(
    "/entry/{userid}/all",
    description="Get all the entries by a user",
    response_model=Page[EntryDispay],
)
async def get_user_entry(
    userid: int, db: Session = Depends(get_db), current_user=Depends(admin_login)
):
    validation(current_user)
    response = admin_controllers.user_entry(userid, db)
    return paginate(response)


@router.put("/entry/{entryid}", description="Update an entry")
async def update_entry(
    entryid: int,
    request: EntryBaseAdminUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_login),
):
    validation(current_user)
    reponse = admin_controllers.update_entry(entryid, request, db)
    return reponse


@router.delete("/entry/{entryid}", description="Delete an entry")
async def delete_entry(
    entryid: int, db: Session = Depends(get_db), current_user=Depends(admin_login)
):
    validation(current_user)
    response = admin_controllers.delete_entry(entryid, db)
    return response

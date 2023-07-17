from fastapi import APIRouter, HTTPException, status
from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session
from db.db import get_db
from db.schema import EntryBase, EntryUpdate, EntryDispay
from controllers import entries_controller
from auth.user_authentication import get_loggedin_user
from fastapi_pagination import Page, paginate


router = APIRouter(prefix="/entry", tags=["User Level Permissions"])

# A HTTP error/exception to be raised if an unauthorized action is been performed.
UNAUTHORIZED_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"Not authorized",
)


@router.post("/{username}/create", description="Add an entry")
async def create_entry(
    username,
    request: EntryBase,
    db: Session = Depends(get_db),
    current_user=Depends(get_loggedin_user),
):
    if username != current_user.username:
        raise UNAUTHORIZED_ERROR
    response = entries_controller.create_entry(db, request, current_user)
    return response


@router.get(
    "/{username}/all",
    description="Get all the enteries by an user",
    response_model=Page[EntryDispay],
)
async def get_enteries(
    username,
    db: Session = Depends(get_db),
    current_user=Depends(get_loggedin_user),
    is_achieved: bool = None,
):
    if username != current_user.username:
        raise UNAUTHORIZED_ERROR
    response = entries_controller.get_entries(db, current_user, is_achieved)
    return paginate(response)


@router.put("/{username}/{entryid}", description="Update an entry")
async def update_entry(
    username,
    entryid,
    request: EntryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_loggedin_user),
):
    if username != current_user.username:
        raise UNAUTHORIZED_ERROR

    response = entries_controller.update_entry(db, current_user, entryid, request)
    return response


@router.delete("/{username}/{entryid}", description="Delete an entry")
async def update_entry(
    username,
    entryid,
    db: Session = Depends(get_db),
    current_user=Depends(get_loggedin_user),
):
    if username != current_user.username:
        raise UNAUTHORIZED_ERROR

    response = entries_controller.delete_entries(db, current_user, entryid)
    return response

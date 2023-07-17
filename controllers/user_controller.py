from db.schema import UserBase, UserUpdate
from sqlalchemy.orm.session import Session
from db.models import Users
from auth.hashing import Hash
from fastapi import status, HTTPException
from sqlalchemy.orm import defer


# Raise unauthorized access error
UNAUTHORIZED_ACCESS_STATUS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"You are not authrized to access this endpoint.",
)


def create_user(db: Session, request: UserBase):
    # Making a check that the username or email is already taken or not | Good for authentication purpose
    username_check = db.query(Users).filter(Users.username == request.username).first()
    email_check = db.query(Users).filter(Users.email == request.email).first()
    if username_check != None and email_check != None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Username/Email provided already exists",
        )

    # Try to create a new user based on the request (body) provided
    try:
        new_user = Users(
            name=request.name,
            username=request.username,
            email=request.email,
            password=Hash.bcrypt(password=request.password),
            expected_calories=request.expected_calories,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to create a new user. Try again",
        )


def user_detail(db: Session, username: str, current_user):
    user = (
        db.query(Users)
        .filter(Users.username == username)
        .options(defer(Users.password))
        .first()
    )

    if user == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with username: {username} not found",
        )
    # Crosscheking if the loggedin user is accessing their own records or not
    if user.username != current_user.username:
        raise UNAUTHORIZED_ACCESS_STATUS
    return user


def update_user(username: str, db: Session, request: UserUpdate, current_user):
    user = (
        db.query(Users)
        .filter(Users.username == username)
        .options(defer(Users.password))
        .first()
    )
    if user != None:
        if user.username != current_user.username:
            # Crosscheking if the loggedin user is accessing their own records or not
            raise UNAUTHORIZED_ACCESS_STATUS
        # Converting a Pydantic model instance to a dictionary
        user_data = request.dict(exclude_unset=True)
        for key, value in user_data.items():
            setattr(user, key, value)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with username: {username} not found",
        )


def delete_user(username: str, db: Session, current_user):
    user = db.query(Users).filter(Users.username == username).first()
    if user != None:
        if user.username != current_user.username:
            raise UNAUTHORIZED_ACCESS_STATUS
        db.delete(user)
        db.commit()
        return {
            "status": status.HTTP_202_ACCEPTED,
            "message": f"Deleted user with username: {username}",
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with username: {username} not found",
        )

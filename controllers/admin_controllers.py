from sqlalchemy.orm.session import Session
from db.models import Users, Entries
from fastapi import status, HTTPException
from sqlalchemy.orm import defer
from db.schema import UserUpdate, EntryBaseAdmin, EntryBaseAdminUpdate
import datetime
from utils import calories


# Admin actions on the users
def get_all_users(db: Session, name):
    if name is None:
        userlist = db.query(Users).all()
    else:
        # Runing a query based on the name provided in the query
        userlist = db.query(Users).filter(Users.name.ilike(f"%{name}%")).all()
    if userlist:
        return userlist
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No users found",
        )


def get_an_user(userid: int, db: Session):
    user = (
        db.query(Users)
        .filter(Users.userid == userid)
        .options(defer(Users.password))
        .first()
    )
    if user == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with userid: {userid} not found",
        )
    return user


def update_an_user(userid: int, db: Session, request: UserUpdate):
    user = (
        db.query(Users)
        .filter(Users.userid == userid)
        .options(defer(Users.password))
        .first()
    )
    if user:
        # Converting a Pydantic model instance to a dictionary
        user_data = request.dict(exclude_unset=True)
        for key, value in user_data.items():
            setattr(user, key, value)

        # Commiting the required changes
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with userid: {userid} not found",
        )


def delete_an_user(userid: int, db):
    user = (
        db.query(Users)
        .filter(Users.userid == userid)
        .options(defer(Users.password))
        .first()
    )
    if user != None:
        db.delete(user)
        db.commit()
        return {"message": f"User with userid: {userid} has been deleted"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with userid: {userid} not found",
        )


# Admin actions on the entries
def get_entries(db: Session, is_achieved):
    if is_achieved is None:
        entries = db.query(Entries).all()
    else:
        entries = db.query(Entries).filter(Entries.is_achieved == is_achieved).all()
    if entries:
        return entries
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No entries in the Database",
        )


def create_entry(request: EntryBaseAdmin, db: Session):
    # Admin must specify for which user he/she want to make an entry
    user = db.query(Users).filter(Users.userid == request.userid).first()
    if user != None:
        # Getting the data from the request
        entered_text = request.text
        total_calories = request.calories_count

        # Action if the calories count is not provided by the user - we need to make an API call now
        if total_calories == None:
            calculated_calories = calories.calculate(query=entered_text)

            # If the value returned from the API is null in case of exception
            if calculated_calories:
                total_calories = calculated_calories

        # Fetchin the daily goal set by the user and make comparison with the provided/fetched value
        daily_calories_goal = user.expected_calories
        daily_goal_achieved = (
            request.is_achieved
            if request.is_achieved is not None
            else total_calories >= daily_calories_goal
        )
        try:
            new_entry = Entries(
                date=datetime.date.today(),
                time=datetime.datetime.now().time(),
                text=request.text,
                calories_count=total_calories,
                is_achieved=daily_goal_achieved,
                userid=user.userid,
            )
            db.add(new_entry)
            db.commit()
            db.refresh(new_entry)
            return new_entry
        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unable to create a new entry",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with userid: {request.userid} not found",
        )


def user_entry(userid: int, db: Session):
    user = (
        db.query(Users)
        .filter(Users.userid == userid)
        .options(defer(Users.password))
        .first()
    )
    if user:
        entries = db.query(Entries).filter(Entries.userid == userid).all()
        if entries:
            return entries
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No entries found for userid: {userid}",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with userid: {userid} not found",
        )


def update_entry(entryid: int, request: EntryBaseAdminUpdate, db: Session):
    # Fetching the entry from the Id that Admin wants to update
    entry = db.query(Entries).filter(Entries.entryid == entryid).first()
    if entry:
        # Fetching the user detail from the databse to which the entry belongs
        user = db.query(Users).filter(Users.userid == entry.userid).first()

        # Retreiving the data from the request body
        entered_text = request.text if request.text else entry.text
        total_calories = request.text if request.text else entry.calories_count

        # In case the only text field is updated by the user - then we must update the calories field also
        if request.calories_count is None and request.text:
            calculated_calories = calories.calculate(query=entered_text)
            if calculated_calories:
                total_calories = calculated_calories

        # Get the daily goal from the user data and make comparison
        daily_calories_goal = user.expected_calories
        daily_goal_chieved = (
            request.is_achieved
            if request.is_achieved is not None
            else total_calories >= daily_calories_goal
        )
        # Converting a Pydantic model instance to a dictionary
        post_data = request.dict(exclude_unset=True)
        post_data["calories_count"] = total_calories
        post_data["is_achieved"] = daily_goal_chieved
        for key, value in post_data.items():
            setattr(entry, key, value)
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No entry with id: {entryid} found",
        )


def delete_entry(entryid: int, db: Session):
    entry = db.query(Entries).filter(Entries.entryid == entryid).first()
    if entry:
        db.delete(entry)
        db.commit()
        return {
            "data": entry,
            "status": status.HTTP_200_OK,
            "message": f"The entry with id: {entryid} has been deleted",
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry with id: {entryid} not found",
        )

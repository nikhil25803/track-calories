from sqlalchemy.orm.session import Session
from db.schema import EntryBase, EntryUpdate
from fastapi import HTTPException, status
from db.models import Entries
import datetime
from utils import calories


# Raise unauthorized access error
UNAUTHORIZED_ACCESS_STATUS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"You are not authrized to access this endpoint.",
)


def create_entry(db: Session, request: EntryBase, current_user):
    # Fetching the data from the request(body)
    entered_text = request.text
    total_calories = request.calories_count

    # If calories count is not provided by the user
    if total_calories == None:
        calculated_calories = calories.calculate(query=entered_text)
        if calculated_calories:
            total_calories = calculated_calories

    # Fetch the daily expected daily calories from the loggedin user data and make comparison
    daily_calories_goal = current_user.expected_calories
    daily_goal_chieved = (
        request.is_achieved
        if request.is_achieved
        else total_calories >= daily_calories_goal
    )
    try:
        new_entry = Entries(
            date=datetime.date.today(),
            time=datetime.datetime.now().time(),
            text=request.text,
            calories_count=total_calories,
            is_achieved=daily_goal_chieved,
            userid=current_user.userid,
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


def get_entries(db: Session, current_user, is_achieved):
    # Querying only the enrties which is marked as true in the is_achieved field
    if is_achieved is not None:
        enteries = (
            db.query(Entries)
            .filter(
                Entries.userid == current_user.userid,
                Entries.is_achieved == is_achieved,
            )
            .all()
        )
    else:
        enteries = db.query(Entries).filter(Entries.userid == current_user.userid).all()

    # In case no entry is available for the loggedin user
    if not enteries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User: {current_user.username} do not have any entry yet.",
        )

    return enteries


def update_entry(db: Session, current_user, entryid, request: EntryUpdate):
    # Searching the entry the loggedin user wants to update and proced only if the entry exist
    entry = db.query(Entries).filter(Entries.entryid == entryid).first()

    # Covering some error case to deliver the exact issue to the user
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry with id: {entryid} not found",
        )
    if entry.userid != current_user.userid:
        raise UNAUTHORIZED_ACCESS_STATUS
    try:
        # Getting the data from the request and updaing only the fields provided by the user else same as in the entry collection
        entered_text = request.text if request.text else entry.text
        total_calories = request.text if request.text else entry.calories_count
        is_achieved = request.is_achieved if request.is_achieved else entry.is_achieved

        # If only text is provided by the user not the calorie count
        if request.calories_count is None and request.text:
            calculated_calories = calories.calculate(query=entered_text)
            if calculated_calories:
                total_calories = calculated_calories

        daily_calories_goal = current_user.expected_calories
        daily_goal_chieved = (
            is_achieved
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
    except:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Unable to update the entry",
        )


def delete_entries(db: Session, current_user, entryid):
    entry = db.query(Entries).filter(Entries.entryid == entryid).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry with id: {entryid} not found",
        )
    if entry.userid != current_user.userid:
        raise UNAUTHORIZED_ACCESS_STATUS
    db.delete(entry)
    db.commit()
    return {
        "status": status.HTTP_202_ACCEPTED,
        "message": f"Deleted entry with entryid: {entryid}",
    }

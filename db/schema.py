from pydantic import BaseModel
from typing import Optional
from datetime import date, time


# User class schema for user registration
class UserBase(BaseModel):
    name: str
    username: str
    email: str
    password: str
    expected_calories: float


# To map the output of the user class - Only the fields mentioned here will be served as the output.
class UserDisplay(BaseModel):
    userid: int
    name: str
    username: str
    email: str
    expected_calories: float

    class Config:
        orm_mode = True


# User class schema for user update request
class UserUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    expected_calories: Optional[float] = None


# Entries Class Schema
class EntryBase(BaseModel):
    text: str
    calories_count: Optional[float] = None
    is_achieved: Optional[bool] = None


# Entry class schema for entries update
class EntryUpdate(BaseModel):
    text: Optional[str] = None
    calories_count: Optional[float] = None
    is_achieved: Optional[bool] = None


# To map entries output
class EntryDispay(BaseModel):
    entryid: int
    date: date
    time: time
    text: str
    calories_count: float
    is_achieved: bool
    userid: int

    class Config:
        orm_mode = True


# Entries Schema for Admins
class EntryBaseAdmin(BaseModel):
    text: str
    calories_count: Optional[float] = None
    is_achieved: Optional[bool] = None
    userid: int


# Entries schema for admins to make an update to the data
class EntryBaseAdminUpdate(BaseModel):
    text: Optional[str] = None
    calories_count: Optional[float] = None
    is_achieved: Optional[bool] = None

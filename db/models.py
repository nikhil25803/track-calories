from sqlalchemy import Column, String, Float, Integer, Date, Time, Boolean
from db.db import Base
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship


# User Model
class Users(Base):
    __tablename__ = "users"

    userid = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    expected_calories = Column(Float, default=0.0)
    entries = relationship("Entries", back_populates="user")


# Entry Model
class Entries(Base):
    __tablename__ = "entries"

    entryid = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=True)
    time = Column(Time, nullable=True)
    text = Column(String)
    calories_count = Column(Float)
    is_achieved = Column(Boolean)
    userid = Column(Integer, ForeignKey("users.userid"))
    user = relationship("Users", back_populates="entries")

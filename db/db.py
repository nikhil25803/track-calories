from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

SQLALCHEMY_DATABASE_URl = "sqlite:///./sqlite_database.db"

# The Engine is responsible for connecting to the database and executing SQL statements.
engine = create_engine(
    SQLALCHEMY_DATABASE_URl, connect_args={"check_same_thread": False}
)


SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

#  The Base class will be used as a base class for all the model classes (ORM classes) we define.
Base = declarative_base()


# get_db that returns a generator. When called, it creates a new SessionLocal object (a new database session)
def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.close()

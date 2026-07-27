from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .config import config
from .models import Base

engine = create_engine(
    f"postgresql://{config.db_user}:{config.db_passwd}@{config.db_host}/{config.db_name}",
    echo=False,
)  # fastapi is the database name, make sure to create it in your PostgreSQL server before running the code.


def create_tables():
    "Create tables in the database if they don't exist already."
    Base.metadata.create_all(
        engine
    )  # this will create the tables in the database if they don't exist already.


def get_session():
    with Session(engine) as session:
        yield session

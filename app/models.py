from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Memory(Base):  # SQLAlchemy model for the Memory table
    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(primary_key=True)  # marks id as primary key
    title: Mapped[str]  # makes title a required field and not nullable
    content: Mapped[str]  # make content a required field and not nullable
    # published: Mapped[bool] = mapped_column(
    #     default=True
    # )  # makes published a boolean field with a default value of True
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default="now()"
    )  # adds a timestamp field with a default value of the current time
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="cascade"))
    owner: Mapped["User"] = relationship(
        "User"
    )  # fastapi checks for column that has foreign key pointing at the table named in the relationship function here and returns
    # the instance of that specific User.
    # say if owner_id is 1 then it returns user instance of user id 1.

    def __repr__(self) -> str:
        return f"Memory(id={self.id}, title={self.title!r}, content={self.content!r})"
        # return f"Memory(id={self.id}, title={self.title!r}, content={self.content!r}, published={self.published})"


class User(Base):  # SQLAlchemy model for the User table
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)  # marks id as primary key
    email: Mapped[str] = mapped_column(
        unique=True
    )  # makes email a required field, unique and not nullable
    password: Mapped[str]  # makes password a required field and not nullable
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default="now()"
    )  # adds a timestamp field with a default value of the current time

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email!r}, password={self.password!r})"

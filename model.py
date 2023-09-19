from sqlmodel import SQLModel, Field
from typing import Optional


class UserBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(description="Username")
    email: str = Field(description="Email address")
    fullname: Optional[str] = Field(description="Optional full name")


class User(UserBase, table=True):
    __tablename__ = "user"
    password: Optional[str] = Field(description="Optional encrypted password")

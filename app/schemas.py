from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from .auth import LocalJWTAuthBackend, get_auth_backend


class MySchema(BaseModel):  # Pydantic model for request validation and serialization
    title: str
    content: str


class UserSchema(BaseModel):  # Pydantic model for request validation and serialization
    email: EmailStr
    password: str


class LocalJWTUserSchemaOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime


class CognitoSignUpUserSchemaOut(BaseModel):
    email: EmailStr
    confirmation_status: str


class ConfirmSignUpSchema(BaseModel):
    verification_code: str
    email: EmailStr
    password: str


class CognitoSchemaOut(LocalJWTUserSchemaOut):
    pass


def get_owner_schema():
    if isinstance(get_auth_backend(), LocalJWTAuthBackend):
        return LocalJWTUserSchemaOut
    return CognitoSignUpUserSchemaOut


class MySchemaOut(MySchema):  # Pydantic model for response serialization
    id: int
    created_at: datetime
    owner_id: int
    owner: Optional[CognitoSignUpUserSchemaOut | LocalJWTUserSchemaOut]

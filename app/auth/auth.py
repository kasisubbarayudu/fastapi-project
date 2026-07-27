from typing import Annotated


from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from ..exceptions import MemAPIException
from . import LocalJWTAuthBackend, get_auth_backend


from .. import database

auth_backend = get_auth_backend()


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(
    session: Annotated[Session, Depends(database.get_session)],
    user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    try:
        if isinstance(auth_backend, LocalJWTAuthBackend):
            access_token = auth_backend.login(
                session,
                {
                    "username": user_credentials.username,
                    "password": user_credentials.password,
                },
            )
        else:
            access_token = auth_backend.login(
                user_credentials.username, user_credentials.password
            )
        return access_token
    except MemAPIException as e:
        raise HTTPException(**(e.to_dict()))

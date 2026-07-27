from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from .auth import get_auth_backend
from .exceptions import MemAPIException

oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")

auth_backend = get_auth_backend()


def get_current_user(token: Annotated[str, Depends(oauth_scheme)]):
    try:
        id = auth_backend.verify_rs256_token(token)
    except MemAPIException as e:
        raise HTTPException(**(e.to_dict()))
    return id

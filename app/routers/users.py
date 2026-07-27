from typing import Annotated

from sqlalchemy import  select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Response, status

from .. import oauth2, schemas
from ..database import get_session
from ..exceptions import MemAPIException
from ..models import User
from .utils import create_user

router = APIRouter(prefix="/users", tags=["Users"])


from ..auth import CognitoAuthBackend, LocalJWTAuthBackend, get_auth_backend

auth_backend = get_auth_backend()


def return_signup_schema():
    if isinstance(auth_backend, LocalJWTAuthBackend):
        return schemas.LocalJWTUserSchemaOut
    else:
        return schemas.CognitoSignUpUserSchemaOut


def return_schema():
    if isinstance(auth_backend, LocalJWTAuthBackend):
        return schemas.LocalJWTUserSchemaOut
    else:
        return schemas.CognitoSchemaOut


@router.post("/signup", response_model=return_signup_schema())
def signup(session: Annotated[Session, Depends(get_session)], user: schemas.UserSchema):
    if isinstance(auth_backend, LocalJWTAuthBackend):
        try:
            resp = create_user(session, user.email, user.password)
        except MemAPIException as e:
            raise HTTPException(**(e.to_dict()))
    else:
        try:
            resp = auth_backend.signup(user.email, user.password)
        except MemAPIException as e:
            raise HTTPException(**(e.to_dict()))
    return resp


if isinstance(auth_backend, CognitoAuthBackend):

    @router.post("/confirmSignUP", response_model=schemas.CognitoSignUpUserSchemaOut)
    def confirmSignUP(
        data: schemas.ConfirmSignUpSchema,
        session: Annotated[Session, Depends(get_session)],
    ):
        try:
            resp = auth_backend.confirmSignup(
                data.verification_code, data.email, data.password, session
            )
        except MemAPIException as e:
            raise HTTPException(**(e.to_dict()))
        return resp


@router.get(
    "/",
    response_model=list[return_schema()],
    dependencies=[Depends(oauth2.get_current_user)],
)
def get_users(session: Annotated[Session, Depends(get_session)]):

    users = session.execute(select(User)).scalars().all()
    print(users)
    return users


@router.get(
    "/{id}",
    response_model=return_schema(),
    dependencies=[Depends(oauth2.get_current_user)],
)
def get_user(session: Annotated[Session, Depends(get_session)], id: int):

    user = session.get(User, str(id))
    print(user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id: {id} not found",
        )
    return user


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(oauth2.get_current_user)],
)
def delete_user(session: Annotated[Session, Depends(get_session)], id: int):

    user = session.get(User, str(id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exist"
        )
    if isinstance(auth_backend, CognitoAuthBackend):
        auth_backend.delete_user(user.email)
    print(">>> user was ", user)
    session.delete(user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

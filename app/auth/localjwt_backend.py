import os
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import ExpiredSignatureError as TokenExpired
from jwt.exceptions import PyJWTError as JWTError
from sqlalchemy import select

from fastapi import APIRouter, status

from .. import models
from ..config import config
from ..exceptions import MemAPIException
from ..hash import verify_password

pwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


with open(os.path.join(pwd, "certs", "private_key.pem"), "r") as f:
    PRIVATE_KEY = f.read()
with open(os.path.join(pwd, "certs", "public_key.pem"), "r") as f:
    PUBLIC_KEY = f.read()


router = APIRouter(prefix="/auth", tags=["Authentication"])


class LocalJWTAuthBackend:

    def create_rs256_token(self, data: dict) -> str:
        payload = {
            "sub": data.get("sub"),
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=config.access_token_expiry_period_in_minutes),
            "roles": data.get("roles"),
            "id": data.get("id"),
        }
        access_token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
        return {"access_token": access_token}

    def login(
        self,
        session,
        user_credentials: dict,
    ):

        user = (
            session.execute(
                select(models.User).where(
                    models.User.email == user_credentials["username"]
                )
            )
            .scalars()
            .first()
        )
        if not user:
            # print(">>>>>>", user)
            raise MemAPIException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exist"
            )

        if not verify_password(user_credentials["password"], user.password):
            raise MemAPIException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
            )

        access_token = self.create_rs256_token(
            data={"sub": str(user.email), "id": str(user.id), "roles": ["admin"]}
        )
        return access_token

    def verify_rs256_token(self, token: str):
        try:
            payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
            id = payload.get("id")
            if not id:
                raise MemAPIException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )
        except TokenExpired:
            raise MemAPIException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
            )
        except JWTError:
            raise MemAPIException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        print(f"Token verified and returning id: {id}")
        return id

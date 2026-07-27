from fastapi import status

from ..exceptions import MemAPIException
from ..hash import hash_password
from ..models import User


def create_user(session, email, password):
    password = hash_password(password)
    user = User(email=email, password=password)
    try:
        session.add(user)
        session.commit()
        print(user)

        return user
    except Exception as e:
        session.rollback()
        raise MemAPIException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

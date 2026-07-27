from ..config import config
from .congito_backend import CognitoAuthBackend
from .localjwt_backend import LocalJWTAuthBackend


def get_auth_backend():
    if not config.cognito_backend:
        print(">>>> local backend is chosen")
        return LocalJWTAuthBackend()
    print(">>>>> cognito backend is chosen")
    return CognitoAuthBackend()

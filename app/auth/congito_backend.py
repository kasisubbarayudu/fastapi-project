from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from fastapi import status

from ..config import config
from ..database import engine
from ..exceptions import MemAPIException
from ..models import User

if config.cognito_backend:
    from ..config import initialise_boto3
    cognito_idp_client = initialise_boto3()

from ..routers.utils import create_user


class CognitoAuthBackend:
    def get_usermame_from_email(self, email):
        username = (email.split("@"))[0]
        return username

    def signup(self, email, password):
        """Registers a new user with Cognito. Returns the Cognito 'sub'."""
        try:
            response = cognito_idp_client.sign_up(
                ClientId=config.cognito_client_id,
                Username=self.get_usermame_from_email(email),
                Password=password,
                UserAttributes=[{"Name": "email", "Value": email}],
            )

        except cognito_idp_client.exceptions.UsernameExistsException:
            raise MemAPIException(detail="User already exists", status_code=400)
        except cognito_idp_client.exceptions.InvalidPasswordException as e:
            raise MemAPIException(detail=f"Weak password: {e}", status_code=400)
        except Exception as e:
            raise MemAPIException(detail="Exception raised: " + str(e), status_code=400)

        print("response received was >>> : ", response)

        return {"email": email, "confirmation_status": "Pending"}

    def confirmSignup(self, verification_code, email, password, session):
        try:
            cognito_idp_client.confirm_sign_up(
                ClientId=config.cognito_client_id,
                Username=self.get_usermame_from_email(email),
                ConfirmationCode=verification_code,
            )
        except cognito_idp_client.exceptions.CodeMismatchException:
            raise MemAPIException(detail="Invalid confirmation code", status_code=400)
        except cognito_idp_client.exceptions.ExpiredCodeException:
            raise MemAPIException("Confirmation code expired", status_code=400)
        except Exception as e:
            raise MemAPIException("Exception raised: " + str(e), status_code=400)
        # fetch the sub now that the account is confirmed
        # user_data = cognito_idp_client.admin_get_user(
        #     UserPoolId=config.cognito_user_pool_id, Username=self.get_usermame_from_email(email)
        # )
        # cognito_sub = next(
        #     attr["Value"] for attr in user_data["UserAttributes"] if attr["Name"] == "sub"
        # ) # cognito_sub is user id.
        # cognito_username = user_data["Username"]
        # since cognito user was confirmed, create user in db.

        try:
            create_user(session, email, password)
        except Exception as e:
            # delete orphaned cognito user incase db user creation fails...
            cognito_idp_client.admin_delete_user(
                UserPoolId=config.cognito_user_pool_id,
                Username=self.get_usermame_from_email(email),
            )
            session.rollback()
            raise MemAPIException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )
        return {"email": email, "confirmation_status": "Confirmed"}

    def login(self, email, password):
        try:
            response = cognito_idp_client.initiate_auth(
                ClientId=config.cognito_client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": self.get_usermame_from_email(email),
                    "PASSWORD": password,
                },
            )
        except cognito_idp_client.exceptions.NotAuthorizedException:
            raise MemAPIException(
                detail="Invalid credentials", status_code=status.HTTP_401_UNAUTHORIZED
            )
        except cognito_idp_client.exceptions.UserNotConfirmedException:
            raise Exception(
                detail="Please confirm your email before logging in",
                status_code=status.HTTP_400_UNAUTHORIZED,
            )

        tokens = response["AuthenticationResult"]
        return {
            "access_token": tokens["AccessToken"],
            "id_token": tokens["IdToken"],
            "refresh_token": tokens["RefreshToken"],
        }

    def verify_rs256_token(self, token):
        try:
            response = cognito_idp_client.get_user(AccessToken=token)
        except cognito_idp_client.exceptions.NotAuthorizedException:
            raise MemAPIException(
                detail="Invalid Token", status_code=status.HTTP_401_UNAUTHORIZED
            )
        token_email = next(
            attr["Value"]
            for attr in response["UserAttributes"]
            if attr["Name"] == "email"
        )
        try:
            with Session(engine) as session:
                print(">>>> ", response)
                user = (
                    session.execute(select(User).filter(User.email == token_email))
                    .scalars()
                    .one()
                )

        except NoResultFound as e:
            raise MemAPIException(
                detail="User with this email doesn't exist. Orphaned user has to be deleted in cognito",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return user.id

    def delete_user(self, email):
        try:
            cognito_idp_client.admin_delete_user(
                UserPoolId=config.cognito_user_pool_id,
                Username=self.get_usermame_from_email(email),
            )
        except Exception as e:
            raise MemAPIException(
                detail="Deletion of user failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

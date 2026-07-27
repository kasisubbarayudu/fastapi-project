import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import get_session
from app.main import app
from app.models import Base
from fastapi.testclient import TestClient  # noqa

from app.config import config

@pytest.fixture(scope="session")
def client():
    engine = create_engine(
        f"postgresql://{config.db_user}:{config.db_passwd}@{config.db_host}/testingdb",
        # echo=True,
    )

    def create_tables():
        "Create tables in the database if they don't exist already."
        Base.metadata.create_all(
            engine
        )  # this will create the tables in the database if they don't exist already.

    create_tables()

    def get_session_override():
        with Session(engine) as session:
            yield session

    client = TestClient(app)
    app.dependency_overrides[get_session] = get_session_override
    return client


@pytest.fixture(scope="session")
def test_user_localjwt_backend(client):
    password = "maa@123"
    res = client.post(
        "/users/signup", json=({"email": "tesuser2@gmail.com", "password": password})
    )
    user = res.json()
    user["password"] = password
    print(">>>> printing user ", user)
    return user


@pytest.fixture(scope="session")
def login(client, test_user_localjwt_backend):
    print(">>>> creating test user for posts creation...")
    res = client.post(
        "/auth/login",
        data=(
            {
                "username": test_user_localjwt_backend["email"],
                "password": test_user_localjwt_backend["password"],
            }
        ),
    )
    token = res.json().get("access_token")
    yield token
    print(">>>> Deleting test user...")
    id = test_user_localjwt_backend["id"]
    headers = {
        "Authorization": f"Bearer {token}",
    }
    res = client.delete(f"/users/{id}", headers=headers)
    print(">>>> failed res: ", res)
    print(res.status_code)


@pytest.fixture(scope="session")
def test_memory(login, client):
    headers = {
        "Authorization": f"Bearer {login}",
    }
    title = "Test post 2"
    content = "This pos2t is created for testing"
    res = client.post(
        "/memories", json=({"title": title, "content": content}), headers=headers
    )
    return res

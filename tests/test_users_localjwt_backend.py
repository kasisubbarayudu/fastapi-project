import pytest

token = None
userid = None


def test_user_create(client):
    response = client.post(
        "/users/signup", json=({"email": "tesuser@gmail.com", "password": "maa@123"})
    )
    global userid
    userid = response.json().get("id")

    assert response.status_code == 200


def test_login_user(client):
    res = client.post(
        "/auth/login", data=({"username": "tesuser@gmail.com", "password": "maa@123"})
    )
    # print(">>>>>>>>>", res.json())

    assert res.status_code == 200
    global token

    print(">>>> kashi: userid ", userid, res)
    token = res.json().get("access_token")


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("shivaji@gmail.com", "shivaji", 404),
        ("shambhaji@gmail.com", "shambhaji", 404),
        ("tesuser@gmail.com", "maa@1234", 401),
    ],
)
def test_incorrect_login(client, email, password, status_code):
    res = client.post("/auth/login", data=({"username": email, "password": password}))

    assert res.status_code == status_code


def test_user_del(client):
    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = client.delete(f"/users/{userid}", headers=headers)
    assert response.status_code == 204

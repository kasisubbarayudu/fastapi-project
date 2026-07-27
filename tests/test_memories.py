def test_create_memory(login, client):
    headers = {
        "Authorization": f"Bearer {login}",
    }
    title = "Test post"
    content = "This post is created for testing"
    res = client.post(
        "/memories", json=({"title": title, "content": content}), headers=headers
    )

    assert res.json().get("title") == title
    assert res.json().get("content") == content


def test_update_memory(login, client, test_memory):
    headers = {
        "Authorization": f"Bearer {login}",
    }
    title = "Test post2"
    content = "updated post2"
    post_id = test_memory.json().get("id")
    res = client.put(
        f"/memories/{post_id}",
        json=({"title": title, "content": content}),
        headers=headers,
    )
    print(res.json())
    # assert res.json().get("title") == title
    # assert res.json().get("content") == content


def test_delete_memory(login, client, test_memory):
    headers = {
        "Authorization": f"Bearer {login}",
    }
    post_id = test_memory.json().get("id")
    res = client.delete(f"/memories/{post_id}", headers=headers)
    assert res.status_code == 204

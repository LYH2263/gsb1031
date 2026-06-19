def test_user_full_flow_login_borrow_query_return(client, normal_user, sample_book):
    login_resp = client.post(
        "/token",
        data={"username": "13800000000", "password": "password"},
    )
    assert login_resp.status_code == 200, login_resp.text
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_resp = client.get("/users/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["phone"] == "13800000000"
    assert me_resp.json()["role"] == "user"

    borrow_resp = client.post(
        "/borrows/",
        json={"book_id": sample_book.id},
        headers=headers,
    )
    assert borrow_resp.status_code == 200, borrow_resp.text
    borrow_data = borrow_resp.json()
    borrow_id = borrow_data["id"]
    assert borrow_data["book_id"] == sample_book.id
    assert borrow_data["is_returned"] is False

    duplicate_resp = client.post(
        "/borrows/",
        json={"book_id": sample_book.id},
        headers=headers,
    )
    assert duplicate_resp.status_code == 400

    my_borrows_resp = client.get("/my-borrows", headers=headers)
    assert my_borrows_resp.status_code == 200
    borrows = my_borrows_resp.json()
    assert len(borrows) == 1
    assert borrows[0]["id"] == borrow_id
    assert borrows[0]["is_returned"] is False
    assert borrows[0]["book"]["id"] == sample_book.id

    return_resp = client.post(f"/borrows/{borrow_id}/return", headers=headers)
    assert return_resp.status_code == 200, return_resp.text
    returned = return_resp.json()
    assert returned["is_returned"] is True
    assert returned["return_date"] is not None

    after_resp = client.get("/my-borrows", headers=headers)
    assert after_resp.status_code == 200
    after = after_resp.json()
    assert len(after) == 1
    assert after[0]["is_returned"] is True

    return_again = client.post(f"/borrows/{borrow_id}/return", headers=headers)
    assert return_again.status_code == 400


def test_unauthenticated_request_rejected(client, sample_book):
    resp = client.get("/my-borrows")
    assert resp.status_code == 401

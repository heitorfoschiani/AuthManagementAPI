def test_register_user(client):
    response = client.post(
        "/auth-management/user/", 
        headers = {"Content-type": "application/json"},
        json = {
            "full_name": "Bruce Wayne",
            "email": "bruce.wayne@outlook.com",
            "phone": "11912345678",
            "username": "batman",
            "password": "ImBatman",
        }
    )

    assert response.status_code == 201
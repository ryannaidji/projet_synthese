import requests
import time

def test_create_delete_user(test_client, user_payload, auth_headers):
    response = test_client.post("/api/users/", json=user_payload, headers=auth_headers)
    response_json = response.json()
    assert response.status_code == 200

    response = test_client.delete(f"/api/users/2", headers=auth_headers)
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["message"] == "User deleted successfully"

def test_create_get_user(test_client, user_payload, auth_headers):
    response = test_client.post("/api/users/", json=user_payload, headers=auth_headers)
    response_json = response.json()
    assert response.status_code == 200

    response = test_client.get("/api/users/2", headers=auth_headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["username"] == "johndoe"
    assert response_json["role"] == "admin"

def test_update_user(test_client, user_payload_updated, auth_headers):
    response = test_client.put("/api/users/2", json=user_payload_updated, headers=auth_headers)
    response_json = response.json()
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["username"] == "janedoe"

def test_get_user_not_found(test_client, auth_headers):
    response = test_client.get(f"/api/users/10",headers=auth_headers)
    assert response.status_code == 404


def test_create_user_wrong_payload(test_client, auth_headers):
    response = test_client.post("/api/users/", json={},headers=auth_headers)
    assert response.status_code == 422

def test_update_user_doesnt_exist(test_client, user_payload_updated, auth_headers):
    response = test_client.put(f"/api/users/10", json=user_payload_updated, headers=auth_headers)
    assert response.status_code == 404

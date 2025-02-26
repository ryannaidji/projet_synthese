import requests
import time

def test_create_delete_diagnostic(test_client, diagnostic_payload, auth_headers):
    response = test_client.post("/api/diagnostics/", json=diagnostic_payload, headers=auth_headers)
    response_json = response.json()
    assert response.status_code == 200

    response = test_client.delete(f"/api/diagnostics/1", headers=auth_headers)
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["message"] == "Diagnostic deleted"

def test_create_get_diagnostic(test_client, diagnostic_payload, auth_headers):
    response = test_client.post("/api/diagnostics/", json=diagnostic_payload, headers=auth_headers)
    response_json = response.json()
    assert response.status_code == 200

    response = test_client.get("/api/diagnostics/1", headers=auth_headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["reviewed_comment"] == "average"
    assert response_json["prediction"] == "60"
    assert response_json["confidence"] == "0.99"

def test_update_diagnostic(test_client, diagnostic_payload_updated, auth_headers):
    response = test_client.put("/api/diagnostics/1", json=diagnostic_payload_updated, headers=auth_headers)
    response_json = response.json()
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["message"] == "Diagnostic updated"

def test_get_diagnostic_not_found(test_client, auth_headers):
    response = test_client.get(f"/api/diagnostics/10",headers=auth_headers)
    assert response.status_code == 404

def test_create_diagnostic_wrong_payload(test_client, auth_headers):
    response = test_client.post("/api/diagnostics/", json={},headers=auth_headers)
    assert response.status_code == 422

def test_update_diagnostic_doesnt_exist(test_client, diagnostic_payload,auth_headers):
    response = test_client.put(f"/api/diagnostics/10", json=diagnostic_payload, headers=auth_headers)
    assert response.status_code == 404

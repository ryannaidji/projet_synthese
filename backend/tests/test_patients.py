import requests
import time

def test_create_delete_patient(test_client, patient_payload, auth_headers):
    response = test_client.post("/api/patients/", json=patient_payload, headers=auth_headers)
    response_json = response.json()
    assert response.status_code == 200

    response = test_client.delete(f"/api/patients/1", headers=auth_headers)
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["message"] == "Patient deleted"

def test_create_get_patient(test_client, patient_payload, auth_headers):
    response = test_client.post("/api/patients/", json=patient_payload, headers=auth_headers)
    response_json = response.json()
    assert response.status_code == 200

    response = test_client.get("/api/patients/1", headers=auth_headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == "Guy Bol"
    assert response_json["address"] == "rue du Moulin"

def test_update_patient(test_client, patient_payload_updated, auth_headers):
    response = test_client.put("/api/patients/1", json=patient_payload_updated, headers=auth_headers)
    response_json = response.json()
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["name"] == "Guy Bol"
    assert response_json["address"] == "rue des Moulins"

def test_get_patient_not_found(test_client, auth_headers):
    response = test_client.get(f"/api/patients/10",headers=auth_headers)
    assert response.status_code == 404

def test_create_patient_wrong_payload(test_client, auth_headers):
    response = test_client.post("/api/patients/", json={},headers=auth_headers)
    assert response.status_code == 422

def test_update_patient_doesnt_exist(test_client, patient_payload,auth_headers):
    response = test_client.put(f"/api/patients/10", json=patient_payload, headers=auth_headers)
    assert response.status_code == 404

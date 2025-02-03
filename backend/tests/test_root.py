import requests
import time

def test_root(test_client):
    response = test_client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"message": "The API is LIVE!!"}

import requests
def test_root():
    response = requests.get("http://localhost:9000/api/health")
    assert response.status_code == 200
    assert response.json() == {"message": "The API is LIVE!!"}

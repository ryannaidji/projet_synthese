import requests
def test_root():
    response = requests.get("http://localhost:5000/health")
    assert response.status_code == 200
    assert response.json() == {"message": "The frontend is LIVE!!"}

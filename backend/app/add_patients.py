import requests

BASE_API_URL = "http://127.0.0.1:9000"  # FastAPI URL


from datetime import datetime

# Patient data
patients = [
    {"full_name": "John Doe", "date_of_birth": "2024-02-03" },
]

for patient in patients:
    response = requests.post(f"{BASE_API_URL}/patients", json=patient)
    if response.status_code == 201:
        print(f"Added patient: {response.json()}")
    else:
        print(f"Failed to add patient: {response.json()}")


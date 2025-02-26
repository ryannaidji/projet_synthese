from fastapi import APIRouter, HTTPException, UploadFile, File
import requests
import numpy as np
import cv2
import json
from os import environ

router = APIRouter(prefix="/api/predict", tags=["Predictions"])

# URL du serveur MLflow
MLFLOW_URL = f"http://{environ.get('MLFLOW_MODEL_URI')}:5001/invocations"

# Définition manuelle des classes (au lieu de class_names.pkl)
CLASS_NAMES = {
    0: "Gliome",
    1: "Méningiome",
    2: "Pas de tumeur",
    3: "Tumeur pituitaire"
}

def preprocess_image(image: bytes):
    """
    Convertit une image binaire en format compatible avec le modèle MLflow.
    """
    image_array = np.frombuffer(image, np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise HTTPException(status_code=400, detail="Format d'image invalide")

    img = cv2.resize(img, (128, 128))  # Redimensionner
    img = img.astype(np.float32) / 255.0  # Normaliser
    img = np.expand_dims(img, axis=-1)  # Ajouter dimension du canal
    img = np.expand_dims(img, axis=0)  # Ajouter dimension batch

    return img.tolist()

@router.post("/")
async def predict_brain_cancer(file: UploadFile = File(...)):
    """
    Endpoint API pour recevoir une image, la traiter et l'envoyer à MLflow.
    """
    try:
        image_bytes = await file.read()
        processed_image = preprocess_image(image_bytes)

        payload = {"instances": processed_image}
        response = requests.post(MLFLOW_URL, json=payload)

        if response.status_code == 200:
            predictions = response.json()["predictions"][0]
            predicted_class_index = np.argmax(predictions)
            predicted_label = CLASS_NAMES.get(predicted_class_index, "Classe inconnue")
            confidence = predictions[predicted_class_index]

            return {"prediction": predicted_label, "confidence": confidence}

        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction : {str(e)}")

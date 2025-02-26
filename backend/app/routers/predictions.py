from fastapi import APIRouter, HTTPException, UploadFile, File
import numpy as np
import cv2
import tensorflow as tf
import os
import threading

router = APIRouter(prefix="/api/predict", tags=["Predictions"])

# Chemin du modèle local
MODEL_PATH = "app/ml_models/brain_tumor_model.h5"

# Définition manuelle des classes
CLASS_NAMES = {
    0: "Gliome",
    1: "Méningiome",
    2: "Pas de tumeur",
    3: "Tumeur pituitaire"
}

# Chargement du modèle une seule fois au démarrage du serveur
if not os.path.exists(MODEL_PATH):
    raise RuntimeError(f"Modèle non trouvé à {MODEL_PATH}. Assurez-vous qu'il est bien sauvegardé.")

model = tf.keras.models.load_model(MODEL_PATH)
model_lock = threading.Lock()  # Verrou pour éviter les accès concurrents

def preprocess_image(image: bytes):
    """
    Convertit une image binaire en format compatible avec le modèle Keras.
    """
    image_array = np.frombuffer(image, np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise HTTPException(status_code=400, detail="Format d'image invalide")

    img = cv2.resize(img, (128, 128))  # Redimensionner à la taille d'entrée du modèle
    img = img.astype(np.float32) / 255.0  # Normaliser les valeurs [0,1]
    img = np.expand_dims(img, axis=-1)  # Ajouter dimension du canal (1 pour grayscale)
    img = np.expand_dims(img, axis=0)  # Ajouter la dimension batch

    return img

@router.post("/")
async def predict_brain_cancer(file: UploadFile = File(...)):
    """
    Endpoint API pour recevoir une image, la traiter et la passer au modèle local pour prédiction.
    """
    try:
        image_bytes = await file.read()
        processed_image = preprocess_image(image_bytes)

        # Verrouiller le modèle pendant la prédiction pour éviter les conflits multi-threads
        with model_lock:
            predictions = model.predict(processed_image)[0]

        predicted_class_index = np.argmax(predictions)
        predicted_label = CLASS_NAMES.get(predicted_class_index, "Classe inconnue")
        confidence = float(predictions[predicted_class_index])

        return {"prediction": predicted_label, "confidence": confidence}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction : {str(e)}")

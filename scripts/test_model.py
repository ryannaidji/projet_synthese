import requests
import numpy as np
import cv2
import pickle

# URL du serveur MLflow
MLFLOW_URL = "http://127.0.0.1:5001/invocations"

# Chemin des fichiers
IMAGE_PATH = "gl-0002.jpg"
CLASS_NAMES_PATH = "../dvc_storage/data/processed/class_names.pkl"

def load_class_names():
    """
    Charge les noms des classes à partir du fichier class_names.pkl.
    """
    with open(CLASS_NAMES_PATH, "rb") as f:
        class_names = pickle.load(f)

    print("Classes chargées :", class_names)
    return {i: class_names[i] for i in range(len(class_names))}

# Charger les noms des classes
CLASS_NAMES = load_class_names()

def preprocess_image(image_path):
    """
    Charge et prétraite une image pour qu'elle corresponde au format attendu par le modèle MLflow.
    """
    # Charger l'image en niveaux de gris
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        raise FileNotFoundError(f"Impossible de charger l'image: {image_path}")

    # Redimensionner à 128x128 (taille attendue par le modèle)
    img = cv2.resize(img, (128, 128))

    # Normaliser les pixels (0-1)
    img = img.astype(np.float32) / 255.0

    # Ajouter la dimension de canal (1 pour grayscale)
    img = np.expand_dims(img, axis=-1)  # (128, 128, 1)

    # Ajouter la dimension batch
    img = np.expand_dims(img, axis=0)  # (1, 128, 128, 1)

    return img.tolist()  # Convertir en liste pour JSON

def send_request(image_array):
    """
    Envoie l'image prétraitée au modèle via l'API MLflow et récupère la classe prédite.
    """
    payload = {"instances": image_array}
    
    response = requests.post(MLFLOW_URL, json=payload)

    if response.status_code == 200:
        predictions = response.json()["predictions"][0]  # Extraire les probabilités
        predicted_class_index = np.argmax(predictions)  # Trouver l'index avec la plus grande probabilité
        predicted_label = CLASS_NAMES[predicted_class_index]  # Nom de la classe prédite
        confidence = predictions[predicted_class_index]  # Confiance associée à la prédiction

        print(f"Prédiction brute : {predictions}")
        print(f"Classe prédite : {predicted_label} (confiance : {confidence:.2%})")
    
    else:
        print(f"Erreur {response.status_code}: {response.text}")

if __name__ == "__main__":
    try:
        image_array = preprocess_image(IMAGE_PATH)
        send_request(image_array)
    except Exception as e:
        print("Erreur:", str(e))

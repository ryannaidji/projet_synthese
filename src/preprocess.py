import os
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
import pickle

# Paramètres de prétraitement
DATA_PATH = os.path.abspath("data/raw/brain-tumor-mri-dataset/")
OUTPUT_PATH = os.path.abspath("data/processed/brain-tumor-mri-dataset-processed/")
IMAGE_SIZE = (128, 128)  # Taille cible des images

def load_and_preprocess_images(data_path, image_size):
    """
    Charge et prétraite les images d'un dossier.
    - Conversion en niveaux de gris
    - Redimensionnement
    - Normalisation
    
    Args:
        data_path (str): Chemin vers le répertoire des données brutes.
        image_size (tuple): Taille cible des images (largeur, hauteur).
        
    Returns:
        images (numpy.ndarray): Tableau des images prétraitées.
        labels (numpy.ndarray): Tableau des étiquettes encodées.
        class_names (list): Liste des noms de classes.
    """
    images = []
    labels = []
    class_names = os.listdir(data_path)
    num_classes = len(class_names)
    
    for idx, cls in enumerate(class_names):
        class_folder = os.path.join(data_path, cls)
        for img_name in os.listdir(class_folder):
            img_path = os.path.join(class_folder, img_name)
            try:
                # Chargement, conversion en grayscale et redimensionnement
                img = Image.open(img_path).convert("L")  # "L" = Grayscale
                img = img.resize(image_size)
                images.append(np.array(img))
                labels.append(idx)
            except Exception as e:
                print(f"Erreur avec l'image {img_name}: {e}")
    
    images = np.array(images) / 255.0  # Normalisation
    images = images[..., np.newaxis]  # Ajout d'une dimension pour le canal (grayscale)
    labels = to_categorical(labels, num_classes=num_classes)  # Encodage One-Hot
    
    print(f"Images chargées : {images.shape}")
    print(f"Labels chargés : {labels.shape}")
    return images, labels, class_names

def save_data(output_path, X_train, y_train, X_test, y_test):
    """
    Sauvegarde les données prétraitées au format Pickle.
    
    Args:
        output_path (str): Chemin vers le dossier de sauvegarde.
        X_train, y_train, X_test, y_test: Données d'entraînement et de test.
    """
    os.makedirs(output_path, exist_ok=True)
    
    with open(os.path.join(output_path, 'X_train.pkl'), 'wb') as f:
        pickle.dump(X_train, f)
    with open(os.path.join(output_path, 'y_train.pkl'), 'wb') as f:
        pickle.dump(y_train, f)
    with open(os.path.join(output_path, 'X_test.pkl'), 'wb') as f:
        pickle.dump(X_test, f)
    with open(os.path.join(output_path, 'y_test.pkl'), 'wb') as f:
        pickle.dump(y_test, f)
    
    print(f"Données sauvegardées dans '{output_path}'.")

def main():
    print("Début du prétraitement des données...")
    images, labels, class_names = load_and_preprocess_images(DATA_PATH, IMAGE_SIZE)
    
    # Division en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=42)
    print(f"Ensemble d'entraînement : {X_train.shape[0]} images")
    print(f"Ensemble de test : {X_test.shape[0]} images")
    
    # Sauvegarde des données
    save_data(OUTPUT_PATH, X_train, y_train, X_test, y_test)
    print("Prétraitement terminé.")

if __name__ == "__main__":
    main()

import os
import numpy as np
from pathlib import Path
from PIL import Image
from sklearn.model_selection import train_test_split
import pickle

# Définition des chemins des données
DATA_PATH = Path("dvc_storage/data/raw/")
OUTPUT_PATH = Path("dvc_storage/data/processed/")
IMAGE_SIZE = (128, 128)  # Taille standard pour l'entraînement

def load_and_preprocess_images(data_path, image_size):
    """
    Charge et prétraite les images :
    - Conversion en niveaux de gris
    - Redimensionnement
    - Normalisation

    Args:
        data_path (Path): Répertoire contenant les images classées par dossier.
        image_size (tuple): Taille cible des images (largeur, hauteur).

    Returns:
        images (numpy.ndarray): Tableau des images prétraitées.
        labels (numpy.ndarray): Étiquettes encodées.
        class_names (list): Liste des noms de classes.
    """
    images = []
    labels = []
    class_names = sorted([d.name for d in data_path.iterdir() if d.is_dir()])
    num_classes = len(class_names)
    
    for idx, cls in enumerate(class_names):
        class_folder = data_path / cls
        for img_name in class_folder.iterdir():
            try:
                # Chargement de l'image, conversion en grayscale et redimensionnement
                img = Image.open(img_name).convert("L")  # "L" = grayscale
                img = img.resize(image_size)
                images.append(np.array(img))
                labels.append(idx)
            except Exception as e:
                print(f"Erreur avec l'image {img_name}: {e}")
    
    images = np.array(images) / 255.0  #  Normalisation entre 0 et 1
    images = images[..., np.newaxis]  #  Ajout du canal unique pour grayscale
    labels = np.array(labels)

    print(f"Images chargées : {images.shape}")
    print(f"Labels chargés : {labels.shape}")
    return images, labels, class_names

def save_data(output_path, X_train, y_train, X_test, y_test, class_names):
    """
    Sauvegarde les ensembles train/test sous forme de fichiers Pickle.

    Args:
        output_path (Path): Répertoire de sauvegarde.
        X_train, y_train, X_test, y_test: Données d'entraînement et de test.
        class_names (list): Noms des classes.
    """
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / 'X_train.pkl', 'wb') as f:
        pickle.dump(X_train, f)
    with open(output_path / 'y_train.pkl', 'wb') as f:
        pickle.dump(y_train, f)
    with open(output_path / 'X_test.pkl', 'wb') as f:
        pickle.dump(X_test, f)
    with open(output_path / 'y_test.pkl', 'wb') as f:
        pickle.dump(y_test, f)
    with open(output_path / 'class_names.pkl', 'wb') as f:
        pickle.dump(class_names, f)

    print(f"Données sauvegardées dans {output_path}")

def main():
    print("Début du prétraitement des images...")
    images, labels, class_names = load_and_preprocess_images(DATA_PATH, IMAGE_SIZE)

    # Séparer en ensembles d'entraînement et de test (80/20)
    X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=42)
    
    print(f"Entraînement : {X_train.shape[0]} images")
    print(f"Test : {X_test.shape[0]} images")

    # Sauvegarde des fichiers
    save_data(OUTPUT_PATH, X_train, y_train, X_test, y_test, class_names)
    print("Prétraitement terminé !")

if __name__ == "__main__":
    main()

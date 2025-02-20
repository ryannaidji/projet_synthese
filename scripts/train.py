import os
import pickle
import mlflow
import mlflow.keras
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, Activation
import argparse

# Définition des chemins des données et du modèle
PROCESSED_DATA_DIR = "dvc_storage/data/processed/"
MODEL_OUTPUT_DIR = "mlflow/model/"
MLFLOW_EXPERIMENT_NAME = "BrainTumor_Classification"
mlflow.set_tracking_uri("file:mlflow/mlruns")

# Hyperparamètres définis directement dans le script
INPUT_SHAPE = (128, 128, 1)  # 1 canal pour grayscale
NUM_CLASSES = 4  # Nombre de classes dans le dataset
LEARNING_RATE = 0.001
EPOCHS = 10
BATCH_SIZE = 32

# Charger les données
def load_data(data_dir):
    with open(os.path.join(data_dir, "X_train.pkl"), "rb") as f:
        X_train = pickle.load(f)
    with open(os.path.join(data_dir, "y_train.pkl"), "rb") as f:
        y_train = pickle.load(f)
    with open(os.path.join(data_dir, "X_test.pkl"), "rb") as f:
        X_test = pickle.load(f)
    with open(os.path.join(data_dir, "y_test.pkl"), "rb") as f:
        y_test = pickle.load(f)
    
    return X_train, y_train, X_test, y_test

# Construire le modèle CNN
def build_model():
    model = Sequential([
        Conv2D(32, (3, 3), padding="same", input_shape=INPUT_SHAPE, activation="relu"),
        MaxPooling2D(pool_size=(2, 2)),

        Conv2D(64, (3, 3), padding="same", activation="relu"),
        MaxPooling2D(pool_size=(2, 2)),

        Conv2D(128, (3, 3), padding="same", activation="relu"),
        MaxPooling2D(pool_size=(2, 2)),

        Flatten(),
        Dense(256, activation="relu"),
        Dropout(0.5),
        Dense(NUM_CLASSES, activation="softmax"),
    ])

    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
                  loss="categorical_crossentropy",
                  metrics=["accuracy"])
    
    return model

# Entraîner le modèle avec MLflow
def train_model(data_dir, output_dir):
    print("Chargement des données...")
    X_train, y_train, X_test, y_test = load_data(data_dir)

    # Correction : conversion des labels en one-hot encoding
    y_train = tf.keras.utils.to_categorical(y_train, num_classes=NUM_CLASSES)
    y_test = tf.keras.utils.to_categorical(y_test, num_classes=NUM_CLASSES)

    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    with mlflow.start_run():
        mlflow.log_param("learning_rate", LEARNING_RATE)
        mlflow.log_param("epochs", EPOCHS)
        mlflow.log_param("batch_size", BATCH_SIZE)

        model = build_model()
        history = model.fit(X_train, y_train, 
                            validation_data=(X_test, y_test),
                            epochs=EPOCHS, 
                            batch_size=BATCH_SIZE,
                            verbose=1)

        #  Log des métriques
        mlflow.log_metric("train_loss", history.history["loss"][-1])
        mlflow.log_metric("train_accuracy", history.history["accuracy"][-1])
        mlflow.log_metric("val_loss", history.history["val_loss"][-1])
        mlflow.log_metric("val_accuracy", history.history["val_accuracy"][-1])

        #  Sauvegarde du modèle avec MLflow
        mlflow.keras.save_model(model, MODEL_OUTPUT_DIR)
    
    print(f"Modèle sauvegardé dans {MODEL_OUTPUT_DIR}")
    return model

#  Script principal
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, default=PROCESSED_DATA_DIR)
    parser.add_argument("--output", type=str, default=MODEL_OUTPUT_DIR)
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    train_model(args.data, args.output)

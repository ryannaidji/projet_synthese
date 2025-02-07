import mlflow

# Définir l'URI du backend de tracking
mlflow.set_tracking_uri("sqlite:///mlflow/mlflow.db")

# Définir le nom de l'expérience
mlflow.set_experiment("brain_tumor_detection")

print("MLflow est configuré avec SQLite.")

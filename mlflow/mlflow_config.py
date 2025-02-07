import mlflow

# Utilisation d'une base SQLite locale pour le tracking
MLFLOW_DB_PATH = "sqlite:///mlflow/mlflow.db"

# Définir l'URI du backend de tracking
mlflow.set_tracking_uri(MLFLOW_DB_PATH)

# Définir l'expérience MLflow
mlflow.set_experiment("BrainTumor_Classification")

print(f"MLflow configuré avec {MLFLOW_DB_PATH}")

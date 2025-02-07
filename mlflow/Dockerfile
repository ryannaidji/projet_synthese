# Utiliser une image légère avec Python
FROM python:3.9

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY mlflow/models/ /app/model/
COPY requirements.txt /app/requirements.txt

# Installer les dépendances
RUN pip install --no-cache-dir -r /app/requirements.txt

# Exposer le port utilisé par MLflow (par défaut 5000)
EXPOSE 5000

# Lancer le modèle MLflow en mode serveur
CMD ["mlflow", "models", "serve", "-m", "/app/model", "-p", "5000"]

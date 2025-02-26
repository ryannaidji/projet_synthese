# Utiliser Python 3.10 (compatible avec ton modèle MLflow)
FROM python:3.10.16

WORKDIR /app

# Copier le modèle et les dépendances
COPY model /app/model
COPY requirements.txt /app/requirements.txt

# Mise à jour pip + installation des dépendances sans cache
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Optimisations pour éviter les erreurs GPU et réduire la consommation mémoire
ENV CUDA_VISIBLE_DEVICES=""
ENV MLFLOW_MODEL_URI="/app/model"
ENV TF_ENABLE_ONEDNN_OPTS=0
ENV TF_CPP_MIN_LOG_LEVEL=2
ENV MLFLOW_DISABLE_ENV_MANAGER=1

# Exposer le port utilisé sur Render
EXPOSE 5001

# Démarrer MLflow en utilisant la variable PORT définie par Render
CMD ["sh", "-c", "mlflow models serve -m /app/model -p ${PORT} --host 0.0.0.0 --no-conda"]

# Utiliser Python 3.10 (compatible avec ton modèle MLflow)
FROM python:3.10.16

WORKDIR /app

# Copier le modèle et les dépendances
COPY model /app/model
COPY requirements.txt /app/requirements.txt

# Mise à jour pip + installation des dépendances sans cache
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Empêcher TensorFlow de chercher un GPU (CUDA inutilisé)
ENV CUDA_VISIBLE_DEVICES=""

# Exposer le bon port pour Render
EXPOSE 5001
ENV PORT=5001  


# Lancer MLflow avec Gunicorn pour éviter les crashs mémoire
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5001", "--timeout", "90", "mlflow.pyfunc.scoring_server.wsgi:app"]

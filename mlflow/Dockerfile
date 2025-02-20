FROM python:3.9

WORKDIR /app

COPY model /app/model
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 5001

CMD ["mlflow", "models", "serve", "-m", "/app/model", "--no-conda", "--port", "5001", "--host", "0.0.0.0"]
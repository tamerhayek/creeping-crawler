FROM python:3.11-slim

WORKDIR /app

# Layer 1: dipendenze — cache valida finché requirements.txt non cambia
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Layer 2: sorgenti
COPY . .

EXPOSE 8004
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8004"]

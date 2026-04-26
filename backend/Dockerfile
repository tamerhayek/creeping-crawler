FROM python:3.11-slim

WORKDIR /app

# Layer 1: dipendenze pip — invalidata solo se requirements.txt cambia
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Layer 2: browser Playwright — pesante (~300MB), cache separata da pip
RUN python -m playwright install --with-deps chromium

# Layer 3: sorgenti — invalidata ad ogni modifica del codice
COPY backend/ .
COPY gs_data /gs_data
COPY domains.json .

EXPOSE 8003
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8003"]

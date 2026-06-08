FROM python:3.11-slim

WORKDIR /app

# OS deps richieste dal connettore MariaDB (compilazione del bindings nativo).
# libmariadb-dev-compat fornisce il tool 'mariadb_config' usato da pip durante
# il build della wheel di mariadb-connector-python.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libmariadb-dev \
        libmariadb-dev-compat \
        gcc \
    && rm -rf /var/lib/apt/lists/*

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

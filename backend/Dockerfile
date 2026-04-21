FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -m playwright install --with-deps chromium

EXPOSE 8003
CMD ["python", "main.py", "serve", "--host", "0.0.0.0"]

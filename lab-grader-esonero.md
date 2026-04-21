# README - GRADER ESONERO 1

# Laboratorio di Ingegneria Informatica - A.A. 2025/2026

Di seguito sono riportate le istruzioni per eseguire il grader del progetto.

Scaricare il grader da Classroom.

## Istruzioni

1. Caricare l’immagine Docker del grader:

    ```bash
    docker load -i lab-grader-esonero.tar.gz
    ```

2. Avviare il proprio progetto:

    ```bash
    docker compose up --build -d
    ```

3. Eseguire il grader passando la propria matricola:

    ```bash
    docker run --network host lab-grader-esonero-1:1.0.1 <vostra_matricola>
    ```

### Nota importante

Se riscontrate errori, anomalie nel comportamento del grader o problemi nelle istruzioni, segnalateli tempestivamente su Classroom.


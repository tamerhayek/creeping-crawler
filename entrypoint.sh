#!/bin/sh
# Avvia ollama in background, scarica il modello qwen3:4b
# e poi resta in foreground sul server.
set -e

ollama serve &
sleep 5
ollama pull qwen3:4b
wait

#!/bin/sh
# Start ollama in the background, pull the llama3.2:3b model,
# then stay in the foreground on the server process.
set -e

ollama serve &
sleep 5
ollama pull llama3.2:3b
wait

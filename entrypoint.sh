#!/bin/bash
set -e
set -o pipefail

echo "[entrypoint] Starting container" 
echo "[entrypoint] MODEL_PATH: ${MODEL_PATH:-not set}" 
echo "[entrypoint] MODEL_URL: ${MODEL_URL:-not set}" 
if [ -n "${API_KEY}" ]; then
  echo "[entrypoint] API_KEY is set"
else
  echo "[entrypoint] WARNING: API_KEY is not set"
fi

if [ -z "$MODEL_PATH" ]; then
  MODEL_FILENAME=$(basename "$MODEL_URL")
  export MODEL_PATH="/models/${MODEL_FILENAME}"
  echo "[entrypoint] MODEL_PATH not set. Derived from MODEL_URL: ${MODEL_PATH}"
else
  echo "[entrypoint] Using MODEL_PATH: ${MODEL_PATH}"
fi

if [ ! -f "$MODEL_PATH" ]; then
  echo "[entrypoint] Model not found. Downloading from ${MODEL_URL}..."
  curl -L "$MODEL_URL" -o "$MODEL_PATH"
else
  echo "[entrypoint] Model already exists: ${MODEL_PATH}"
fi

exec uvicorn main:app --host 0.0.0.0 --port 8000

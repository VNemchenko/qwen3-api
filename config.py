import os

MODEL_PATH = os.getenv("MODEL_PATH")
API_KEY = os.getenv("API_KEY", "supersecretkey")

if not MODEL_PATH:
    raise EnvironmentError("MODEL_PATH must be set by entrypoint.sh before starting FastAPI")

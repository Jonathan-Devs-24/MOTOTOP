# desktop/app/core/config.py
from decouple import Config, RepositoryEnv
from pathlib import Path

# Subís dos niveles: app/core → app → desktop → MotoTop
BASE_DIR = Path(__file__).resolve().parents[3]

env_path = BASE_DIR / ".env"

config = Config(RepositoryEnv(env_path))

API_BASE_URL = config("API_BASE_URL")

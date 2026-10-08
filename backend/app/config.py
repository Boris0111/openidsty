import os
from pathlib import Path

ROOT = Path(os.getenv('PROJECT_ROOT', Path(__file__).resolve().parents[2]))
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg://industry:industry@localhost:5433/industry')
MAP_DIR = ROOT / 'industry-map'
DATA_DIR = ROOT / 'data'

import os

from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.environ.get('POSTGRES_DB', 'spimex_trading_results')
DB_HOST = os.environ.get('POSTGRES_HOST', 'db')
DB_PORT = os.environ.get('POSTGRES_PORT', '5432')
DB_USER = os.environ.get('POSTGRES_USER', 'postgres')
DB_PASS = os.environ.get('POSTGRES_PASSWORD', '123')

DB_MODEL_STR_MAX_LENGTH = 254

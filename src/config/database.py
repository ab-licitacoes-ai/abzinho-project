import os
from dotenv import load_dotenv
import psycopg2
from fastapi import HTTPException

# Load environment variables from .env file
load_dotenv(dotenv_path="../../config/.env") 

# Load configuration from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

# Ltring connection postgresql
DATABASE_URL = f"dbname={DB_NAME} user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT}"

def get_db_connection():
    """Tenta conectar ao DB usando a URL segura do .env."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        # For not exposed details in production
        print(f"Erro Crítico de Conexão com o Banco de Dados. Host: {DB_HOST}.")
        raise HTTPException(status_code=503, detail="Serviço de Banco de Dados Indisponível (503)")
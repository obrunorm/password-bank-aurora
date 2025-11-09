"""
Configurações do projeto Aurora
"""
import os

# Caminho do banco de dados
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "senhas.db")

# Garantir que a pasta data existe
os.makedirs(DATA_DIR, exist_ok=True)

# Configurações de criptografia
PBKDF2_ITERATIONS = 390000
SALT_LENGTH = 16




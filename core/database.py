"""
Módulo de gerenciamento do banco de dados SQLite
"""
import sqlite3
import os
from .config import DB_PATH, DATA_DIR


def inicializar_banco():
    """
    Inicializa o banco de dados SQLite se ele não existir.
    Cria a tabela 'senhas' com os campos necessários.
    """
    # Garante que a pasta data existe
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE senhas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            usuario TEXT,
            senha_cript BLOB NOT NULL,
            salt BLOB NOT NULL
        );
        """)
        conn.commit()
        conn.close()
        return True
    return False


def verificar_banco():
    """
    Verifica se o banco de dados existe e está acessível.
    """
    return os.path.exists(DB_PATH)




"""
Módulo de gerenciamento e criptografia de senhas
"""
import base64
import os
import sqlite3
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from .config import DB_PATH, PBKDF2_ITERATIONS, SALT_LENGTH
from .database import inicializar_banco, verificar_banco


def gerar_chave(senha_mestra, salt):
    """
    Gera uma chave de criptografia usando PBKDF2HMAC.
    
    Args:
        senha_mestra: A senha-mestra do usuário
        salt: Salt único para esta senha
    
    Returns:
        Chave Fernet codificada em base64
    """
    # Garante que a senha mestra é uma string e usa UTF-8 explicitamente
    if not isinstance(senha_mestra, str):
        senha_mestra = str(senha_mestra)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(senha_mestra.encode('utf-8')))


def criptografar(chave, texto):
    """
    Criptografa um texto usando a chave fornecida.
    
    Args:
        chave: Chave Fernet (bytes)
        texto: Texto a ser criptografado (str)
    
    Returns:
        Texto criptografado (bytes)
    """
    if not isinstance(texto, str):
        texto = str(texto)
    return Fernet(chave).encrypt(texto.encode('utf-8'))


def descriptografar(chave, texto_cript):
    """
    Descriptografa um texto usando a chave fornecida.
    
    Args:
        chave: Chave Fernet (bytes)
        texto_cript: Texto criptografado (bytes)
    
    Returns:
        Texto descriptografado (str)
    """
    return Fernet(chave).decrypt(texto_cript).decode('utf-8')


def salvar_senha(nome, usuario, senha, senha_mestra):
    """
    Salva uma nova senha no banco de dados, criptografada.
    
    Args:
        nome: Nome/identificação do site/serviço
        usuario: Nome de usuário (pode ser None)
        senha: Senha a ser salva
        senha_mestra: Senha-mestra para criptografar
    
    Returns:
        True se salvou com sucesso, False caso contrário
    """
    try:
        # Garante que o banco existe
        inicializar_banco()
        
        # Garante que a senha mestra é uma string
        if not isinstance(senha_mestra, str):
            senha_mestra = str(senha_mestra)
        
        # Gera salt único para esta senha
        salt = os.urandom(SALT_LENGTH)
        chave = gerar_chave(senha_mestra, salt)
        senha_cript = criptografar(chave, senha)

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO senhas (nome, usuario, senha_cript, salt) VALUES (?, ?, ?, ?)",
                (nome, usuario, senha_cript, salt)
            )
            conn.commit()
        
        # Limpeza de memória
        del senha_mestra, chave, salt
        
        return True
    except Exception as e:
        print(f"Erro ao salvar senha: {e}")
        return False


def ler_senhas(senha_mestra):
    """
    Lê todas as senhas do banco e as descriptografa.
    
    Args:
        senha_mestra: Senha-mestra para descriptografar
    
    Returns:
        Lista de tuplas (id, nome, usuario, senha_decifrada)
        Se a senha-mestra estiver incorreta, retorna "⚠️ Senha incorreta"
    """
    senhas = []
    
    if not verificar_banco():
        return senhas
    
    try:
        # Garante que a senha mestra é uma string
        if not isinstance(senha_mestra, str):
            senha_mestra = str(senha_mestra)
        
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            for id_senha, nome, usuario, senha_cript, salt in c.execute(
                "SELECT id, nome, usuario, senha_cript, salt FROM senhas"
            ):
                chave = gerar_chave(senha_mestra, salt)
                try:
                    senha_decifrada = descriptografar(chave, senha_cript)
                    senhas.append((id_senha, nome, usuario, senha_decifrada))
                except Exception:
                    senhas.append((id_senha, nome, usuario, "⚠️ Senha incorreta"))
                finally:
                    # Limpeza de memória
                    del chave
        
        return senhas
    except Exception as e:
        print(f"Erro ao ler senhas: {e}")
        return []


def deletar_senha(senha_id):
    """
    Deleta uma senha do banco de dados pelo ID.
    
    Args:
        senha_id: ID da senha a ser deletada
    
    Returns:
        True se deletou com sucesso, False caso contrário
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM senhas WHERE id = ?", (senha_id,))
            conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao deletar senha: {e}")
        return False


def deletar_todas_senhas():
    """
    Deleta todas as senhas do banco de dados.
    
    Returns:
        True se deletou com sucesso, False caso contrário
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM senhas")
            conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao deletar todas as senhas: {e}")
        return False


def obter_todas_senhas_com_id():
    """
    Retorna todas as senhas com seus IDs (sem descriptografar).
    Útil para listagem antes de descriptografar.
    
    Returns:
        Lista de tuplas (id, nome, usuario)
    """
    if not verificar_banco():
        return []
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            return c.execute("SELECT id, nome, usuario FROM senhas").fetchall()
    except Exception as e:
        print(f"Erro ao obter senhas: {e}")
        return []


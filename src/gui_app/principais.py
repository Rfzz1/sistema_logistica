from conexao import conectar_bd
import pymysql
from datetime import datetime
import hashlib
import os
import uuid
from auxiliares import garantir_endereco_texto

# --- Funções Principais de Lógica ---

def garantir_usuario_no_bd(username, nome=None):
    conn = conectar_bd()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id_usuarios FROM tb_usuarios WHERE username = %s", (username,)
        )
        row = cur.fetchone()
        if row:
            return row["id_usuarios"]

        cur.execute(
            "INSERT INTO tb_usuarios (nome, username, senha_hash, tipo) VALUES (%s, %s, '', 'operador')",
            (nome or username, username),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def buscar_status_id_por_nome(nome):
    conn = conectar_bd()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_status FROM tb_status WHERE nome = %s", (nome,))
        row = cur.fetchone()
        return row["id_status"] if row else None
    finally:
        conn.close()


def buscar_primeiro_status():
    conn = conectar_bd()
    if not conn:
        return 1
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_status FROM tb_status LIMIT 1")
        row = cur.fetchone()
        return row["id_status"] if row else None
    finally:
        conn.close()


def obter_status_names():
    conn = conectar_bd()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("SELECT nome FROM tb_status ORDER BY nome")
        return [r["nome"] for r in cur.fetchall()]
    finally:
        conn.close()



def inserir_envio_db(
    codigo, descricao, id_status, origem_txt, destino_txt, data_postagem, id_usuario
):
    if not codigo:
        codigo = uuid.uuid4().hex[:10].upper()

    conn = conectar_bd()
    if not conn:
        return False, "Erro BD"

    try:
        # 1. Criar IDs para os endereços baseados no texto
        id_origem = garantir_endereco_texto(conn, origem_txt)
        id_destino = garantir_endereco_texto(conn, destino_txt)

        # 2. Inserir Envio
        cur = conn.cursor()
        sql = """INSERT INTO tb_envios 
            (codigo_rastreio, descricao, id_endereco_origem, id_endereco_destino, data_postagem, id_status_atual) 
            VALUES (%s, %s, %s, %s, %s, %s)"""
        cur.execute(
            sql, (codigo, descricao, id_origem, id_destino, data_postagem, id_status)
        )
        id_envio = cur.lastrowid
        conn.commit()

        # 3. Inserir Primeiro Histórico
        sql_hist = """INSERT INTO tb_historico_status 
            (id_envio, id_status, localizacao, observacao, data_evento) 
            VALUES (%s, %s, %s, %s, %s)"""
        cur.execute(
            sql_hist,
            (id_envio, id_status, origem_txt, "Postagem inicial", data_postagem),
        )
        conn.commit()

        # 4. Auditoria
        if id_usuario:
            inserir_auditoria(id_usuario, "criar_envio", "tb_envios", codigo)

        return True, codigo
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def atualizar_envio_db(
    codigo, descricao, id_status, destino_texto, data_postagem, id_usuario
):
    conn = conectar_bd()
    if not conn:
        return False, "Erro BD"
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id_envios, id_status_atual FROM tb_envios WHERE codigo_rastreio = %s",
            (codigo,)
        )
        row = cur.fetchone()
        if not row:
            return False, "Não encontrado"

        id_envio = row["id_envios"]
        status_antigo = row["id_status_atual"]
        # Atualiza status atual
        cur.execute(
            "UPDATE tb_envios SET descricao=%s, id_status_atual=%s WHERE id_envios=%s",
            (descricao, id_status, id_envio),
        )

        # Insere novo histórico
        cur.execute(
            "INSERT INTO tb_historico_status (id_envio, id_status, localizacao, observacao, data_evento) VALUES (%s, %s, %s, %s, %s)",
            (id_envio, id_status, destino_texto, descricao, data_postagem),
        )
        conn.commit()

        if id_usuario:
            inserir_auditoria(
                id_usuario,
                "atualizar",
                "tb_envios",
                codigo,
                status_antigo=status_antigo,
                status_novo=id_status
            )

        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def inserir_auditoria(id_usuario, acao, tabela, reg_id, status_antigo="", status_novo=""):
    conn = conectar_bd()
    if conn:
        try:
            cur = conn.cursor()
            sql = """
                INSERT INTO tb_auditoria 
                (id_usuario, acao, status_antigo, status_novo, tabela_afetada, registro_id, data_evento)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            cur.execute(sql, (id_usuario, acao, str(status_antigo), str(status_novo), tabela, reg_id))
            conn.commit()
        except Exception:
            pass
        finally:
            conn.close()


# --- Auth Utils ---
def gerar_senha_hash(senha):
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, 100000)
    return salt.hex() + ":" + key.hex()


def verificar_senha(senha, senha_hash):
    try:
        salt_hex, key_hex = senha_hash.split(":")
        new_key = hashlib.pbkdf2_hmac(
            "sha256", senha.encode(), bytes.fromhex(salt_hex), 100000
        )
        return new_key == bytes.fromhex(key_hex)
    except:
        return False


def obter_usuario_login(username):
    conn = conectar_bd()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tb_usuarios WHERE username = %s", (username,))
        return cur.fetchone()
    finally:
        conn.close()


def inserir_usuario_completo(nome, user, senha_hash):
    conn = conectar_bd()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tb_usuarios (nome, username, senha_hash, tipo) VALUES (%s,%s,%s,'operador')",
            (nome, user, senha_hash),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()
from datetime import datetime
import pymysql
from pymysql.err import MySQLError as Error
import hashlib
import os
import uuid
import random
import sys
import time


FONTE_TITULO = ("Arial", 48, "bold")
FONTE_TEXTO = ("Arial", 22)
FONTE_INPUT = ("Arial", 20)

ALTURA_INPUT = 55
LARGURA_INPUT = 500

ALTURA_BOTAO = 60
LARGURA_BOTAO = 300

BTN_PRIMARY = "#3b82f6"
BTN_PRIMARY_HOVER = "#2563eb"
BTN_SECONDARY = "#6b7280"
BTN_SECONDARY_HOVER = "#4b5563"
BTN_SUCCESS = "#10b981"
BTN_SUCCESS_HOVER = "#059669"
BTN_DANGER = "#ef4444"
BTN_DANGER_HOVER = "#dc2626"


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "db_provapython"
}


usuarios = {}   
registros = []  


class EntrySim:
    def __init__(self, initial=""):
        self._value = str(initial)

    def get(self):
        return self._value

    def insert(self, pos, text):
        if pos in (0, "0", "start"):
            self._value = str(text) + self._value
        else:
            self._value = str(text)

    def delete(self, a, b=None):
        self._value = ""

    def set(self, text):
        self._value = str(text)

class OptionMenuSim:
    def __init__(self, values=None):
        self.values = values or []
        self._value = self.values[0] if self.values else None

    def get(self):
        return self._value

    def set(self, v):
        self._value = v
        if v not in self.values:
            self.values.append(v)

class TextSim:
    def __init__(self):
        self._lines = []

    def insert(self, pos, text):
        self._lines.append(str(text))

    def delete(self, a, b=None):
        self._lines = []

    def getvalue(self):
        return "\n".join(self._lines)

    def display(self):
        content = self.getvalue()
        print(content if content else "[vazio]")


def conectar_bd():
    try:
        conn = pymysql.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Error as e:
        print("Erro ao conectar ao banco:", e)
        return None

def garantir_usuario_no_bd(username, nome=None):
    conn = conectar_bd()
    if conn is None:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_usuarios FROM tb_usuarios WHERE username = %s", (username,))
        row = cur.fetchone()
        if row:
            return row['id_usuarios']
        cur.execute(
            "INSERT INTO tb_usuarios (nome, username, senha_hash, tipo) VALUES (%s, %s, %s, %s)",
            (nome or username, username, "", "operador")
        )
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print("Erro garantir_usuario_no_bd:", e)
        return None
    finally:
        conn.close()

def buscar_envio_por_codigo(codigo):
    conn = conectar_bd()
    if conn is None:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_envios, codigo_rastreio, descricao, id_status_atual, data_postagem FROM tb_envios WHERE codigo_rastreio = %s", (codigo,))
        return cur.fetchone()
    except Error:
        return None
    finally:
        conn.close()

def buscar_status_id_por_nome(nome_status):
    conn = conectar_bd()
    if conn is None:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_status FROM tb_status WHERE nome = %s", (nome_status,))
        row = cur.fetchone()
        return row['id_status'] if row else None
    except Error:
        return None
    finally:
        conn.close()

def buscar_primeiro_status():
    conn = conectar_bd()
    if conn is None:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_status FROM tb_status ORDER BY id_status LIMIT 1")
        row = cur.fetchone()
        return row['id_status'] if row else None
    except Error:
        return None
    finally:
        conn.close()

def inserir_envio_db(codigo, descricao, id_status, destino_texto, data_postagem=None, id_usuario=None, id_end_origem=1, id_end_destino=1):
    if not codigo:
        codigo = uuid.uuid4().hex[:10].upper()
    conn = conectar_bd()
    if conn is None:
        return False, "Erro conectar BD"
    try:
        cur = conn.cursor()
        sql = "INSERT INTO tb_envios (codigo_rastreio, descricao, id_endereco_origem, id_endereco_destino, data_postagem, id_status_atual) VALUES (%s, %s, %s, %s, %s, %s)"
        cur.execute(sql, (codigo, descricao, 1, 1, data_postagem or datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id_status))
        conn.commit()
        id_envio = cur.lastrowid

        cur.execute("INSERT INTO tb_historico_status (id_envio, id_status, localizacao, observacao, data_evento) VALUES (%s, %s, %s, %s, %s)",
                    (id_envio, id_status, destino_texto or "", descricao or "", data_postagem or datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()

        if id_usuario:
            inserir_auditoria(id_usuario, "criar_envio", "tb_envios", codigo, None)

        return True, codigo
    except Error as e:
        return False, str(e)
    finally:
        conn.close()

def atualizar_envio_db(codigo, descricao=None, id_status=None, destino_texto=None, data_postagem=None, id_usuario=None):
    conn = conectar_bd()
    if conn is None:
        return False, "Erro conectar BD"
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_envios FROM tb_envios WHERE codigo_rastreio = %s", (codigo,))
        row = cur.fetchone()
        if not row:
            return False, "Encomenda não encontrada"
        id_envio = row['id_envios']

        cur2 = conn.cursor()
        cur2.execute("UPDATE tb_envios SET descricao = %s, id_status_atual = %s, data_postagem = %s WHERE id_envios = %s",
                     (descricao, id_status, data_postagem, id_envio))
        conn.commit()

        cur2.execute("INSERT INTO tb_historico_status (id_envio, id_status, localizacao, observacao, data_evento) VALUES (%s, %s, %s, %s, NOW())",
                     (id_envio, id_status, destino_texto or "", descricao or ""))
        conn.commit()

        if id_usuario:
            inserir_auditoria(id_usuario, "atualizar_envio", "tb_envios", codigo, None)

        return True, None
    except Error as e:
        return False, str(e)
    finally:
        conn.close()

def obter_status_names():
    conn = conectar_bd()
    if conn is None:
        return []
    try:
        cur = conn.cursor()
        cur.execute("SELECT nome FROM tb_status ORDER BY nome")
        rows = cur.fetchall()
        return [r['nome'] for r in rows]
    except Error:
        return []
    finally:
        conn.close()

def inserir_historico(id_envio, id_status, localizacao, observacao):
    conn = conectar_bd()
    if conn is None:
        return False, "Erro conexão"
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tb_historico_status (id_envio, id_status, localizacao, observacao, data_evento) VALUES (%s, %s, %s, %s, NOW())",
            (id_envio, id_status, localizacao, observacao)
        )
        conn.commit()
        return True, None
    except Error as e:
        return False, f"Erro inserir_historico: {e}"
    finally:
        conn.close()

def atualizar_status_envio(id_envio, id_status):
    conn = conectar_bd()
    if conn is None:
        return False, "Erro conexão"
    try:
        cur = conn.cursor()
        cur.execute("UPDATE tb_envios SET id_status_atual = %s WHERE id_envios = %s", (id_status, id_envio))
        conn.commit()
        return True, None
    except Error as e:
        return False, f"Erro atualizar_status_envio: {e}"
    finally:
        conn.close()

def inserir_auditoria(id_usuario, acao, tabela_afetada, registro_id, ip_origem=None):
    conn = conectar_bd()
    if conn is None:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tb_auditoria (id_usuario, acao, tabela_afetada, registro_id, ip_origem, data_evento) VALUES (%s, %s, %s, %s, %s, NOW())",
            (id_usuario, acao, tabela_afetada, registro_id, ip_origem)
        )
        conn.commit()
        return True
    except Error as e:
        print("Erro inserir_auditoria:", e)
        return False
    finally:
        conn.close()


def gerar_senha_hash(senha: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt, 100_000)
    return salt.hex() + ':' + key.hex()

def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        salt_hex, key_hex = senha_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt, 100_000)
        return new_key == key
    except Exception:
        return False

def obter_usuario_por_username(username):
    conn = conectar_bd()
    if conn is None:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_usuarios, nome, username, senha_hash, tipo FROM tb_usuarios WHERE username = %s", (username,))
        return cur.fetchone()
    except Error as e:
        print("Erro obter_usuario_por_username:", e)
        return None
    finally:
        conn.close()

def inserir_ou_atualizar_usuario(username, nome, senha_hash=None):
    conn = conectar_bd()
    if conn is None:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_usuarios FROM tb_usuarios WHERE username = %s", (username,))
        row = cur.fetchone()
        if row:
            uid = row['id_usuarios']
            if senha_hash is not None:
                cur.execute("UPDATE tb_usuarios SET senha_hash = %s, nome = %s WHERE id_usuarios = %s", (senha_hash, nome or username, uid))
                conn.commit()
            return uid

        cur.execute(
            "INSERT INTO tb_usuarios (nome, username, senha_hash, tipo) VALUES (%s, %s, %s, %s)",
            (nome or username, username, senha_hash or "", "operador")
        )
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print("Erro inserir_ou_atualizar_usuario:", e)
        return None
    finally:
        conn.close()

def buscar_status_nome_por_id(id_status):
    if id_status is None:
        return None
    conn = conectar_bd()
    if conn is None:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT nome FROM tb_status WHERE id_status = %s", (id_status,))
        row = cur.fetchone()
        return row['nome'] if row else None
    finally:
        conn.close()

def buscar_ultimo_historico(id_envio):
    conn = conectar_bd()
    if conn is None:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT localizacao, observacao, data_evento FROM tb_historico_status WHERE id_envio = %s ORDER BY data_evento DESC LIMIT 1", (id_envio,))
        return cur.fetchone()
    finally:
        conn.close()


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")

def pausa(msg="Pressione Enter para continuar..."):
    input(msg)


class TelaCadastro:
    def __init__(self, parent):
        self.parent = parent
        self.entry_user = EntrySim()
        self.entry_pass = EntrySim()
        self.label_msg = ""

    def run(self):
        limpar_tela()
        print("=== Cadastro de Usuário ===")
        usuario = input("Novo Usuário: ").strip()
        senha = input("Senha: ").strip()
        self.entry_user.set(usuario)
        self.entry_pass.set(senha)
        self.cadastrar()
        print(self.label_msg)
        pausa()

    def cadastrar(self):
        usuario = self.entry_user.get().strip()
        senha = self.entry_pass.get().strip()

        if not usuario or not senha:
            self.label_msg = "Preencha todos os campos."
            return

        if usuario in usuarios or obter_usuario_por_username(usuario):
            self.label_msg = "Usuário já existe."
            return

        senha_hash = gerar_senha_hash(senha)
        usuarios[usuario] = {"senha_hash": senha_hash, "nome": usuario}
        uid = inserir_ou_atualizar_usuario(usuario, nome=usuario, senha_hash=senha_hash)
        self.label_msg = "Usuário cadastrado."




class TelaLogin:
    def __init__(self):
        self.title = "Login - Rastreamento"
        self.label_msg = ""
        self.entry_user = EntrySim()
        self.entry_pass = EntrySim()
        self.cad_nome = EntrySim()
        self.cad_user = EntrySim()
        self.cad_pass = EntrySim()
        self.label_msg_cad = ""

    def run(self):
        while True:
            limpar_tela()
            print("=== Bem-vindo ao Sistema de Rastreamento ===")
            if self.label_msg:
                print(self.label_msg)
            print("\n1) Entrar")
            print("2) Cadastrar-se")
            print("0) Sair")

            escolha = input("Escolha: ").strip()
            if escolha == '1':
                self.mostrar_login()
            elif escolha == '2':
                self.mostrar_cadastro()
            elif escolha == '0':
                print("Saindo...")
                sys.exit(0)
            else:
                pausa("Opção inválida.")

    def mostrar_login(self):
        limpar_tela()
        print("=== Login ===")
        usuario = input("Usuário: ").strip()
        senha = input("Senha: ").strip()
        self.entry_user.set(usuario)
        self.entry_pass.set(senha)
        self.fazer_login()

    def mostrar_cadastro(self):
        limpar_tela()
        print("=== Cadastro de Usuário ===")
        nome = input("Nome Completo: ").strip()
        usuario = input("Usuário: ").strip()
        senha = input("Senha: ").strip()

        self.cad_nome.set(nome)
        self.cad_user.set(usuario)
        self.cad_pass.set(senha)
        self.cadastrar_usuario()

    def cadastrar_usuario(self):
        nome = self.cad_nome.get().strip()
        usuario = self.cad_user.get().strip()
        senha = self.cad_pass.get().strip()

        if not nome or not usuario or not senha:
            print("Preencha todos os campos.")
            pausa()
            return

        senha_hash = gerar_senha_hash(senha)
        usuarios[usuario] = {"senha_hash": senha_hash, "nome": nome}
        inserir_ou_atualizar_usuario(usuario, nome=nome, senha_hash=senha_hash)

        print("Usuário cadastrado!")
        pausa()

    def fazer_login(self):
        usuario = self.entry_user.get().strip()
        senha = self.entry_pass.get().strip()

        # memória
        user_local = usuarios.get(usuario)
        if user_local and verificar_senha(senha, user_local["senha_hash"]):
            inserir_ou_atualizar_usuario(usuario, nome=user_local["nome"])
            TelaMenuEnvios(self, usuario).run()
            return

        # banco
        db_user = obter_usuario_por_username(usuario)
        if db_user and verificar_senha(senha, db_user["senha_hash"]):
            usuarios[usuario] = {"senha_hash": db_user["senha_hash"], "nome": db_user["nome"]}
            TelaMenuEnvios(self, usuario).run()
            return

        self.label_msg = "Usuário ou senha inválidos"
        pausa(self.label_msg)

# ===============================
# TELA MENU ENCOMENDAS
# ===============================
class TelaMenuEnvios:
    def __init__(self, parent, usuario):
        self.title = "Menu de Encomendas"
        self.usuario = usuario
        self.parent = parent

        # cadastro
        self.cad_codigo = EntrySim()
        self.cad_descricao = EntrySim()
        sts = obter_status_names()
        if not sts: sts = ["Postado"]
        self.cad_status = OptionMenuSim(sts)
        self.cad_destino = EntrySim()
        self.cad_data = EntrySim(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.cad_msg = ""

        # buscar
        self.bus_codigo = EntrySim()
        self.bus_text = TextSim()

        # atualizar
        self.atu_codigo = EntrySim()
        self.atu_descricao = EntrySim()
        sts2 = obter_status_names()
        self.atu_status = OptionMenuSim(sts2)
        self.atu_destino = EntrySim()
        self.atu_data = EntrySim()
        self.atu_msg = ""

    def run(self):
        while True:
            limpar_tela()
            print(f"=== Menu de Encomendas - Usuário: {self.usuario} ===")
            print("1) Cadastrar Encomenda")
            print("2) Buscar Encomenda")
            print("3) Atualizar Encomenda")
            print("4) Listar Últimos Eventos")
            print("5) Voltar (Logout)")
            print("6) Listar Encomendas por Status")
            print("0) Sair")

            escolha = input("Escolha: ").strip()
            if escolha == '1':
                self.menu_cadastrar()
            elif escolha == '2':
                self.menu_buscar()
            elif escolha == '3':
                self.menu_atualizar()
            elif escolha == '4':
                self.menu_listar_eventos()
            elif escolha == '5':
                pausa("Saindo do menu...")
                return
            elif escolha == '6':
                self.menu_listar_por_status()
            elif escolha == '0':
                sys.exit(0)
            else:
                pausa("Opção inválida.")

    # =============== CADASTRAR ===============
    def menu_cadastrar(self):
        limpar_tela()
        print("=== Cadastrar Encomenda ===")
        codigo = input("Código (enter para gerar): ").strip() or None
        descricao = input("Descrição: ").strip()
        sts = obter_status_names()
        if not sts: sts = ["Postado"]
        print("Status:", ", ".join(sts))
        status = input(f"Status [{sts[0]}]: ").strip() or sts[0]
        destino = input("Destino: ").strip()
        data = input(f"Data postagem [{self.cad_data.get()}]: ").strip() or self.cad_data.get()

        self.cad_codigo.set(codigo or "")
        self.cad_descricao.set(descricao)
        self.cad_status.set(status)
        self.cad_destino.set(destino)
        self.cad_data.set(data)

        self.cad_salvar()
        pausa(self.cad_msg)

    def cad_salvar(self):
        codigo = self.cad_codigo.get().strip() or None
        descricao = self.cad_descricao.get().strip()
        status_nome = self.cad_status.get()
        id_status = buscar_status_id_por_nome(status_nome) or buscar_primeiro_status()
        destino = self.cad_destino.get().strip()
        data_postagem = self.cad_data.get().strip() or None
        if not descricao:
            self.cad_msg = "Descrição obrigatória."
            return
        id_usuario = garantir_usuario_no_bd(self.usuario, nome=self.usuario)
        ok, result = inserir_envio_db(codigo, descricao, id_status, destino, data_postagem, id_usuario)
        self.cad_msg = f"Criado. Código: {result}" if ok else f"Erro: Código já existe"

    # =============== BUSCAR ===============
    def menu_buscar(self):
        limpar_tela()
        print("=== Buscar ===")
        codigo = input("Código: ").strip()
        self.bus_codigo.set(codigo)
        self.buscar_interno()
        print("--- Resultado ---")
        self.bus_text.display()
        pausa()

    def buscar_interno(self):
        codigo = self.bus_codigo.get().strip()
        envio = buscar_envio_por_codigo(codigo)
        self.bus_text.delete('1.0')
        if not envio:
            self.bus_text.insert('end', f"Encomenda não encontrada: {codigo}\n")
            return
        self.bus_text.insert('end', f"Código: {envio['codigo_rastreio']}\n")
        self.bus_text.insert('end', f"Descrição: {envio['descricao']}\n")
        self.bus_text.insert('end', f"Status: {buscar_status_nome_por_id(envio['id_status_atual'])}\n")
        self.bus_text.insert('end', f"Data postagem: {envio['data_postagem']}\n")
        ultimo = buscar_ultimo_historico(envio['id_envios'])
        if ultimo:
            self.bus_text.insert('end', f"Último histórico - Local: {ultimo['localizacao']} | Obs: {ultimo['observacao']} | Data: {ultimo['data_evento']}\n")

    # =============== ATUALIZAR ===============
    def menu_atualizar(self):
        limpar_tela()
        print("=== Atualizar ===")
        codigo = input("Código: ").strip()
        self.atu_codigo.set(codigo)
        self.atual_carregar()

        if not self.atu_descricao.get():
            pausa("Encomenda não encontrada.")
            return

        print("Campos carregados:")
        print("Descrição:", self.atu_descricao.get())
        print("Status:", self.atu_status.get())
        print("Destino:", self.atu_destino.get())
        print("Data:", self.atu_data.get())

        descricao = input("Nova descrição (enter p/ manter): ").strip() or self.atu_descricao.get()
        status_nome = input(f"Novo status (enter p/ manter '{self.atu_status.get()}'): ").strip() or self.atu_status.get()
        destino = input("Novo destino (enter p/ manter): ").strip() or self.atu_destino.get()
        data_postagem = input("Nova data (enter p/ manter): ").strip() or self.atu_data.get()

        self.atu_descricao.set(descricao)
        self.atu_status.set(status_nome)
        self.atu_destino.set(destino)
        self.atu_data.set(data_postagem)

        self.atual_atualizar()
        pausa(self.atu_msg)

    def atual_carregar(self):
        codigo = self.atu_codigo.get().strip()
        envio = buscar_envio_por_codigo(codigo)
        if not envio:
            self.atu_msg = "Encomenda não encontrada."
            return

        self.atu_descricao.set(envio['descricao'] or "")
        nome_status = buscar_status_nome_por_id(envio['id_status_atual'])
        self.atu_status.set(nome_status)
        ultimo = buscar_ultimo_historico(envio['id_envios'])
        self.atu_destino.set(ultimo['localizacao'] if ultimo else "")
        self.atu_data.set(str(envio['data_postagem']))
        self.atu_msg = "Carregado."

    def atual_atualizar(self):
        codigo = self.atu_codigo.get().strip()
        descricao = self.atu_descricao.get().strip()
        status_nome = self.atu_status.get()
        id_status = buscar_status_id_por_nome(status_nome) or buscar_primeiro_status()
        destino = self.atu_destino.get().strip()
        data_postagem = self.atu_data.get().strip()

        id_usuario = garantir_usuario_no_bd(self.usuario, nome=self.usuario)
        ok, msg = atualizar_envio_db(codigo, descricao, id_status, destino, data_postagem, id_usuario)
        self.atu_msg = "Encomenda atualizada." if ok else f"Erro: {msg}"

    # =============== LISTAR EVENTOS ===============
    def menu_listar_eventos(self):
        limpar_tela()
        print("=== Últimos Eventos ===")
        self.listar_eventos()
        pausa()

    def listar_eventos(self):
        conn = conectar_bd()
        if conn is None:
            print("Erro banco.")
            return

        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT h.data_evento, e.codigo_rastreio AS tag, h.localizacao AS local,
                       h.observacao AS item, s.nome AS status, e.data_postagem AS publicada
                FROM tb_historico_status h
                JOIN tb_envios e ON h.id_envio = e.id_envios
                LEFT JOIN tb_status s ON h.id_status = s.id_status
                ORDER BY h.data_evento DESC
                LIMIT 100
            """)
            rows = cur.fetchall()
        except Error as e:
            print("Erro:", e)
            return
        finally:
            conn.close()

        for r in rows:
            ts = r["data_evento"]
            pub = r["publicada"]

            ts_str = ts.strftime("%d/%m/%Y %H:%M:%S") if isinstance(ts, datetime) else str(ts)
            pub_str = pub.strftime("%d/%m/%Y %H:%M:%S") if isinstance(pub, datetime) else str(pub)

            print(f"[{ts_str}] Publicada: {pub_str} | {r['local']} -> {r['item']} (TAG: {r['tag']}) | Status: {r['status']}")
        print()

    # =============== LISTAR POR STATUS ===============
    def menu_listar_por_status(self):
        limpar_tela()
        print("=== Listar Encomendas por Status ===")
        print("1) Pendentes")
        print("2) Em Trânsito")
        print("3) Entregues")
        print("0) Voltar")

        op = input("Escolha: ").strip()

        if op == '1':
            self.listar_por_status_interno([
                'Postado',
                'Coletado',
                'Centro da Distribuidora',
                'Aguardando Retirada',
                'Retido'
            ])
        elif op == '2':
            self.listar_por_status_interno([
                'Em Transito',
                'Saiu para entrega'
            ])
        elif op == '3':
            self.listar_por_status_interno(['Entregue'])
        elif op == '0':
            return
        else:
            pausa("Opção inválida.")

    def listar_por_status_interno(self, lista_status):
        conn = conectar_bd()
        if conn is None:
            print("Erro ao conectar ao banco.")
            pausa()
            return

        try:
            cur = conn.cursor()
            sql = """
                SELECT e.codigo_rastreio, e.descricao, s.nome AS status, e.data_postagem
                FROM tb_envios e
                JOIN tb_status s ON e.id_status_atual = s.id_status
                WHERE s.nome IN (%s)
                ORDER BY e.data_postagem DESC
            """ % (",".join(["%s"] * len(lista_status)))

            cur.execute(sql, lista_status)
            rows = cur.fetchall()

        except Error as e:
            print("Erro:", e)
            pausa()
            return
        finally:
            conn.close()

        limpar_tela()
        print("=== Resultados ===\n")

        if not rows:
            print("Nenhuma encomenda encontrada.")
        else:
            for r in rows:
                print(f"Código: {r['codigo_rastreio']} | Desc: {r['descricao']} | Status: {r['status']} | Data: {r['data_postagem']}")

        print()
        pausa()

# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    try:
        TelaLogin().run()
    except KeyboardInterrupt:
        print("\nEncerrado.")
        sys.exit(0)

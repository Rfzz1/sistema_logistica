from conexao import conectar_bd, DB_CONFIG
import pymysql
import customtkinter as ctk
import tkinter as tk
from datetime import datetime
import hashlib
import os
import uuid
from auxiliares import garantir_endereco_texto, buscar_dados_completos_envio, garantir_cidade_padrao, listar_historico_envio
from principais import garantir_usuario_no_bd, buscar_status_id_por_nome, inserir_envio_db, atualizar_envio_db, obter_status_names, gerar_senha_hash, verificar_senha, obter_usuario_login, inserir_usuario_completo

# =========================
# CONFIGURAÇÃO GLOBAL
# =========================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Fontes e tamanhos
FONTE_TITULO = ("Arial", 48, "bold")
FONTE_TEXTO = ("Arial", 22)
FONTE_INPUT = ("Arial", 20)
ALTURA_INPUT = 55
LARGURA_INPUT = 500
ALTURA_BOTAO = 60
LARGURA_BOTAO = 300

# Cores
BTN_PRIMARY = "#3b82f6"
BTN_PRIMARY_HOVER = "#2563eb"
BTN_SECONDARY = "#6b7280"
BTN_SECONDARY_HOVER = "#4b5563"
BTN_SUCCESS = "#10b981"
BTN_SUCCESS_HOVER = "#059669"
BTN_DANGER = "#ef4444"
BTN_DANGER_HOVER = "#dc2626"

# Memória Local
usuarios = {}


# ===============================
# INTERFACE GRÁFICA (GUI)
# ===============================


# Funções Fullscreen
def alternar_fullscreen(event, janela):
    janela.attributes("-fullscreen", not janela.attributes("-fullscreen"))


def sair_fullscreen(event, janela):
    janela.attributes("-fullscreen", False)


class TelaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login Logística")
        self.attributes("-fullscreen", True)
        self.bind("<F11>", lambda e: alternar_fullscreen(e, self))
        self.bind("<Escape>", lambda e: sair_fullscreen(e, self))

        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill="both", expand=True)
        self.show_login()

    def limpar(self):
        for w in self.frame.winfo_children():
            w.destroy()

    def show_login(self):
        self.limpar()
        ctk.CTkLabel(self.frame, text="Sistema Logístico", font=FONTE_TITULO).pack(
            pady=40
        )

        self.entry_user = ctk.CTkEntry(
            self.frame,
            width=LARGURA_INPUT,
            height=ALTURA_INPUT,
            placeholder_text="Usuário",
            font=FONTE_INPUT,
        )
        self.entry_user.pack(pady=15)
        self.entry_pass = ctk.CTkEntry(
            self.frame,
            width=LARGURA_INPUT,
            height=ALTURA_INPUT,
            placeholder_text="Senha",
            show="*",
            font=FONTE_INPUT,
        )
        self.entry_pass.pack(pady=15)

        ctk.CTkButton(
            self.frame,
            text="Entrar",
            width=LARGURA_BOTAO,
            height=ALTURA_BOTAO,
            command=self.login,
            font=FONTE_TEXTO,
            fg_color=BTN_PRIMARY,
        ).pack(pady=20)
        ctk.CTkButton(
            self.frame,
            text="Cadastrar Novo Usuário",
            width=LARGURA_BOTAO,
            height=ALTURA_BOTAO,
            command=self.show_cadastro,
            font=FONTE_TEXTO,
            fg_color=BTN_SECONDARY,
        ).pack(pady=10)
        ctk.CTkButton(
            self.frame,
            text="Sair",
            width=LARGURA_BOTAO,
            height=ALTURA_BOTAO,
            command=self.quit,
            font=FONTE_TEXTO,
            fg_color=BTN_DANGER,
        ).pack(pady=30)

        self.lbl_msg = ctk.CTkLabel(self.frame, text="", font=FONTE_TEXTO)
        self.lbl_msg.pack()

    def show_cadastro(self):
        self.limpar()
        ctk.CTkLabel(self.frame, text="Novo Usuário", font=FONTE_TITULO).pack(pady=30)

        self.cad_nome = ctk.CTkEntry(
            self.frame,
            width=LARGURA_INPUT,
            height=ALTURA_INPUT,
            placeholder_text="Nome Completo",
            font=FONTE_INPUT,
        )
        self.cad_nome.pack(pady=10)
        self.cad_user = ctk.CTkEntry(
            self.frame,
            width=LARGURA_INPUT,
            height=ALTURA_INPUT,
            placeholder_text="Username",
            font=FONTE_INPUT,
        )
        self.cad_user.pack(pady=10)
        self.cad_pass = ctk.CTkEntry(
            self.frame,
            width=LARGURA_INPUT,
            height=ALTURA_INPUT,
            placeholder_text="Senha",
            show="*",
            font=FONTE_INPUT,
        )
        self.cad_pass.pack(pady=10)

        ctk.CTkButton(
            self.frame,
            text="Salvar",
            width=LARGURA_BOTAO,
            height=ALTURA_BOTAO,
            command=self.registrar,
            font=FONTE_TEXTO,
            fg_color=BTN_SUCCESS,
        ).pack(pady=20)
        ctk.CTkButton(
            self.frame,
            text="Voltar",
            width=LARGURA_BOTAO,
            height=ALTURA_BOTAO,
            command=self.show_login,
            font=FONTE_TEXTO,
            fg_color=BTN_SECONDARY,
        ).pack(pady=10)

        self.lbl_cad_msg = ctk.CTkLabel(self.frame, text="", font=FONTE_TEXTO)
        self.lbl_cad_msg.pack()

    def login(self):
        u = self.entry_user.get().strip()
        p = self.entry_pass.get().strip()

        # Verifica Memória
        if u in usuarios and verificar_senha(p, usuarios[u]["senha_hash"]):
            self.abrir_sistema(u)
            return

        # Verifica Banco
        db_user = obter_usuario_login(u)
        if db_user and verificar_senha(p, db_user["senha_hash"]):
            usuarios[u] = {
                "senha_hash": db_user["senha_hash"],
                "nome": db_user["nome"],
            }  # Cache
            self.abrir_sistema(u)
            return

        self.lbl_msg.configure(text="Dados inválidos!", text_color="red")

    def registrar(self):
        n = self.cad_nome.get()
        u = self.cad_user.get()
        p = self.cad_pass.get()
        if not n or not u or not p:
            self.lbl_cad_msg.configure(text="Preencha tudo!", text_color="red")
            return

        ph = gerar_senha_hash(p)
        if inserir_usuario_completo(n, u, ph):
            usuarios[u] = {"senha_hash": ph, "nome": n}
            self.lbl_cad_msg.configure(
                text="Sucesso! Volte para logar.", text_color="green"
            )
        else:
            self.lbl_cad_msg.configure(text="Usuário já existe.", text_color="red")

    def abrir_sistema(self, usuario):
        self.withdraw()
        TelaMenuEnvios(self, usuario)


class TelaMenuEnvios(ctk.CTkToplevel):
    def __init__(self, parent, usuario):
        super().__init__(parent)
        self.title("Gestão de Encomendas")
        self.attributes("-fullscreen", True)
        self.bind("<F11>", lambda e: alternar_fullscreen(e, self))
        self.bind("<Escape>", lambda e: sair_fullscreen(e, self))

        self.usuario = usuario
        self.parent = parent

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        self.frames = {}
        self.criar_menus()
        self.show("menu")

    def criar_menus(self):
        # MENU PRINCIPAL
        menu = ctk.CTkFrame(self.container)
        ctk.CTkLabel(menu, text=f"Bem-vindo, {self.usuario}", font=FONTE_TITULO).pack(
            pady=20
        )
        
        # Buscar tipo de usuário
        db_user = obter_usuario_login(self.usuario)
        self.user_role = db_user["tipo"] if db_user else "comum"

        botoes = [
            ("Cadastrar Encomenda", "cadastrar", BTN_PRIMARY),
            ("Buscar Encomenda", "buscar", BTN_PRIMARY),
        ]
        
        # Operador/Admin ganham o botão Atualizar
        if self.user_role in ("operador", "admin"):
            botoes.append(("Atualizar Encomenda", "atualizar", BTN_PRIMARY))

        # Sempre tem o logout
        botoes.append(("Sair (Logout)", "sair", BTN_DANGER))

        for txt, acao, cor in botoes:
            cmd = self.sair if acao == "sair" else lambda a=acao: self.show(a)
            ctk.CTkButton(
                menu,
                text=txt,
                width=400,
                height=ALTURA_BOTAO,
                font=FONTE_TEXTO,
                fg_color=cor,
                command=cmd,
            ).pack(pady=15)
        self.frames["menu"] = menu

        # CADASTRAR (Adicionado campo Origem)
        cad = ctk.CTkFrame(self.container)
        ctk.CTkLabel(cad, text="Nova Encomenda", font=FONTE_TITULO).pack(pady=10)

        self.cad_cod = ctk.CTkEntry(
            cad,
            width=600,
            height=ALTURA_INPUT,
            placeholder_text="Código (Opcional)",
            font=FONTE_INPUT,
        )
        self.cad_cod.pack(pady=5)

        self.cad_desc = ctk.CTkEntry(
            cad,
            width=600,
            height=ALTURA_INPUT,
            placeholder_text="Descrição do Produto",
            font=FONTE_INPUT,
        )
        self.cad_desc.pack(pady=5)

        # CAMPO ORIGEM NOVO
        self.cad_origem = ctk.CTkEntry(
            cad,
            width=600,
            height=ALTURA_INPUT,
            placeholder_text="Endereço de Origem (Texto)",
            font=FONTE_INPUT,
        )
        self.cad_origem.pack(pady=5)

        self.cad_dest = ctk.CTkEntry(
            cad,
            width=600,
            height=ALTURA_INPUT,
            placeholder_text="Endereço de Destino (Texto)",
            font=FONTE_INPUT,
        )
        self.cad_dest.pack(pady=5)

        opts = obter_status_names() or ["Postado"]
        self.cad_status = ctk.CTkOptionMenu(
            cad, values=opts, width=300, height=50, font=FONTE_INPUT
        )
        self.cad_status.pack(pady=5)
        self.cad_status.set(opts[0])

        self.cad_data = ctk.CTkEntry(
            cad, width=600, height=ALTURA_INPUT, font=FONTE_INPUT
        )
        self.cad_data.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.cad_data.pack(pady=5)

        ctk.CTkButton(
            cad,
            text="SALVAR",
            width=300,
            height=ALTURA_BOTAO,
            fg_color=BTN_SUCCESS,
            command=self.salvar_envio,
        ).pack(pady=15)
        ctk.CTkButton(
            cad,
            text="Voltar",
            width=300,
            height=ALTURA_BOTAO,
            fg_color=BTN_SECONDARY,
            command=lambda: self.show("menu"),
        ).pack(pady=5)
        self.cad_msg = ctk.CTkLabel(cad, text="", font=FONTE_TEXTO)
        self.cad_msg.pack()
        self.frames["cadastrar"] = cad

        # BUSCAR (Com histórico completo)
        bus = ctk.CTkFrame(self.container)
        ctk.CTkLabel(bus, text="Rastreamento Detalhado", font=FONTE_TITULO).pack(
            pady=10
        )

        self.bus_cod = ctk.CTkEntry(
            bus,
            width=500,
            height=ALTURA_INPUT,
            placeholder_text="Digite o código",
            font=FONTE_INPUT,
        )
        self.bus_cod.pack(pady=10)
        ctk.CTkButton(
            bus,
            text="PESQUISAR",
            width=200,
            height=ALTURA_BOTAO,
            command=self.realizar_busca,
        ).pack(pady=5)

        self.bus_txt = ctk.CTkTextbox(bus, width=800, height=400, font=("Consolas", 16))
        self.bus_txt.pack(pady=10)

        ctk.CTkButton(
            bus,
            text="Voltar",
            width=300,
            height=ALTURA_BOTAO,
            fg_color=BTN_SECONDARY,
            command=lambda: self.show("menu"),
        ).pack(pady=5)
        self.frames["buscar"] = bus

        # ATUALIZAR
        atu = ctk.CTkFrame(self.container)
        ctk.CTkLabel(atu, text="Atualizar Status", font=FONTE_TITULO).pack(pady=10)

        self.atu_cod = ctk.CTkEntry(
            atu,
            width=500,
            height=ALTURA_INPUT,
            placeholder_text="Código",
            font=FONTE_INPUT,
        )
        self.atu_cod.pack(pady=5)
        ctk.CTkButton(
            atu,
            text="Carregar",
            width=200,
            height=50,
            command=self.carregar_para_atualizar,
        ).pack(pady=5)

        self.atu_desc = ctk.CTkEntry(
            atu,
            width=600,
            height=ALTURA_INPUT,
            placeholder_text="Nova Descrição/Obs",
            font=FONTE_INPUT,
        )
        self.atu_desc.pack(pady=5)

        self.atu_status = ctk.CTkOptionMenu(
            atu, values=opts, width=300, height=50, font=FONTE_INPUT
        )
        self.atu_status.pack(pady=5)

        self.atu_local = ctk.CTkEntry(
            atu,
            width=600,
            height=ALTURA_INPUT,
            placeholder_text="Local Atual (Cidade/Unidade)",
            font=FONTE_INPUT,
        )
        self.atu_local.pack(pady=5)

        self.atu_data = ctk.CTkEntry(
            atu, width=600, height=ALTURA_INPUT, font=FONTE_INPUT
        )
        self.atu_data.pack(pady=5)

        ctk.CTkButton(
            atu,
            text="ATUALIZAR",
            width=300,
            height=ALTURA_BOTAO,
            fg_color=BTN_SUCCESS,
            command=self.confirmar_atualizacao,
        ).pack(pady=15)
        ctk.CTkButton(
            atu,
            text="Voltar",
            width=300,
            height=ALTURA_BOTAO,
            fg_color=BTN_SECONDARY,
            command=lambda: self.show("menu"),
        ).pack(pady=5)
        self.atu_msg = ctk.CTkLabel(atu, text="", font=FONTE_TEXTO)
        self.atu_msg.pack()
        self.frames["atualizar"] = atu

        # Esconde todos
        for f in self.frames.values():
            f.pack(fill="both", expand=True)
            f.pack_forget()

    def show(self, name):
        for k, v in self.frames.items():
            if k == name:
                v.pack(fill="both", expand=True)
            else:
                v.pack_forget()

    def sair(self):
        self.parent.deiconify()
        self.destroy()

    # --- LÓGICA UI ---

    def salvar_envio(self):
        c = self.cad_cod.get().strip()
        d = self.cad_desc.get().strip()
        o = self.cad_origem.get().strip()  # Novo campo
        dt = self.cad_dest.get().strip()
        s = self.cad_status.get()
        date = self.cad_data.get()

        if not d or not o or not dt:
            self.cad_msg.configure(
                text="Preencha Descrição, Origem e Destino!", text_color="red"
            )
            return

        sid = buscar_status_id_por_nome(s) or 1
        uid = garantir_usuario_no_bd(self.usuario)

        ok, res = inserir_envio_db(c, d, sid, o, dt, date, uid)
        if ok:
            self.cad_msg.configure(text=f"Sucesso! Código: {res}", text_color="green")
            self.cad_cod.delete(0, tk.END)
            self.cad_desc.delete(0, tk.END)
            self.cad_origem.delete(0, tk.END)
            self.cad_dest.delete(0, tk.END)
        else:
            self.cad_msg.configure(text=f"Falha ao registrar: Esse código de rastreio já existe", text_color="red")

    def realizar_busca(self):
        cod = self.bus_cod.get().strip()
        self.bus_txt.delete("1.0", tk.END)

        dados = buscar_dados_completos_envio(cod)
        if not dados:
            self.bus_txt.insert(tk.END, "ENCOMENDA NÃO ENCONTRADA.")
            return

        # Exibe Cabeçalho
        txt = f"""{'='*40}
RASTREIO: {dados['codigo_rastreio']}
{'='*40}
PRODUTO:   {dados['descricao']}
STATUS:    {dados['status_nome']}
DATA POST: {dados['data_postagem']}

ORIGEM:    {dados['origem_rua']}
DESTINO:   {dados['destino_rua']}

----------------------------------------
HISTÓRICO DE MOVIMENTAÇÕES:
----------------------------------------
"""
        self.bus_txt.insert(tk.END, txt)

        # Exibe Timeline
        hist = listar_historico_envio(dados["id_envios"])
        if not hist:
            self.bus_txt.insert(tk.END, "Sem movimentações registradas.")
        else:
            for h in hist:
                linha = f"[{h['data_evento']}] {h['status_nome']}\n   Local: {h['localizacao']}\n   Obs: {h['observacao']}\n{'-'*40}\n"
                self.bus_txt.insert(tk.END, linha)

    def carregar_para_atualizar(self):
        cod = self.atu_cod.get().strip()
        dados = buscar_dados_completos_envio(cod)
        if not dados:
            self.atu_msg.configure(text="Não encontrado.", text_color="red")
            return

        self.atu_desc.delete(0, tk.END)
        self.atu_desc.insert(0, dados["descricao"])
        self.atu_status.set(dados["status_nome"] or "")

        # Tenta pegar último local do histórico
        hist = listar_historico_envio(dados["id_envios"])
        self.atu_local.delete(0, tk.END)
        if hist:
            self.atu_local.insert(0, hist[0]["localizacao"])

        self.atu_data.delete(0, tk.END)
        self.atu_data.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.atu_msg.configure(text="Carregado!", text_color="green")

    def confirmar_atualizacao(self):
        cod = self.atu_cod.get().strip()
        d = self.atu_desc.get().strip()
        s = self.atu_status.get()
        l = self.atu_local.get().strip()
        date = self.atu_data.get()

        if not cod or not d:
            return

        sid = buscar_status_id_por_nome(s) or 1
        uid = garantir_usuario_no_bd(self.usuario)

        ok, msg = atualizar_envio_db(cod, d, sid, l, date, uid)
        if ok:
            self.atu_msg.configure(text="Atualizado com sucesso!", text_color="green")
        else:
            self.atu_msg.configure(text=f"Erro: {msg}", text_color="red")


if __name__ == "__main__":
    app = TelaLogin()
    app.mainloop()

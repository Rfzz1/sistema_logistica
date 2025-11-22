from conexao import conectar_bd, DB_CONFIG
import pymysql
import uuid

# --- Funções Auxiliares para Lidar com Endereços Complexos ---
def garantir_cidade_padrao(conn):
    """Garante que exista pelo menos uma cidade para vincular endereços rápidos."""
    cur = conn.cursor()
    cur.execute("SELECT id_cidades FROM tb_cidades LIMIT 1")
    row = cur.fetchone()
    if row:
        return row["id_cidades"]
    # Cria cidade padrão se não existir
    cur.execute("INSERT INTO tb_cidades (nome, estado) VALUES ('Cidade Padrão', 'XX')")
    conn.commit()
    return cur.lastrowid


def garantir_endereco_texto(conn, texto_endereco):
    """
    Recebe um texto (ex: 'Rua X, Centro'), cria um registro em tb_enderecos
    vinculado a uma cidade padrão e retorna o ID do endereço novo.
    Isso resolve a complexidade do banco relacional sem mudar a UI.
    """
    if not texto_endereco:
        texto_endereco = "Endereço não informado"

    id_cidade = garantir_cidade_padrao(conn)

    # Simplificação: Jogamos o texto todo no campo 'rua' e preenchemos o resto com dummy
    # para satisfazer as restrições do banco (NOT NULL)
    cur = conn.cursor()
    sql = """
    INSERT INTO tb_enderecos (rua, numero, bairro, cep, id_cidade) 
    VALUES (%s, 'S/N', 'Geral', '00000-000', %s)
    """
    cur.execute(sql, (texto_endereco, id_cidade))
    conn.commit()
    return cur.lastrowid


def buscar_dados_completos_envio(codigo):
    """Busca envio fazendo JOIN com endereços para mostrar texto legível."""
    conn = conectar_bd()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        # Query poderosa para trazer tudo de uma vez
        sql = """
            SELECT 
                e.id_envios, e.codigo_rastreio, e.descricao, e.data_postagem,
                s.nome as status_nome, e.id_status_atual,
                end_orig.rua as origem_rua,
                end_dest.rua as destino_rua
            FROM tb_envios e
            LEFT JOIN tb_status s ON e.id_status_atual = s.id_status
            LEFT JOIN tb_enderecos end_orig ON e.id_endereco_origem = end_orig.id_enderecos
            LEFT JOIN tb_enderecos end_dest ON e.id_endereco_destino = end_dest.id_enderecos
            WHERE e.codigo_rastreio = %s
        """
        cur.execute(sql, (codigo,))
        return cur.fetchone()
    finally:
        if conn:
            conn.close()


def listar_historico_envio(id_envio):
    """Retorna lista de movimentações."""
    conn = conectar_bd()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        sql = """
            SELECT h.data_evento, h.localizacao, h.observacao, s.nome as status_nome
            FROM tb_historico_status h
            LEFT JOIN tb_status s ON h.id_status = s.id_status
            WHERE h.id_envio = %s
            ORDER BY h.data_evento DESC
        """
        cur.execute(sql, (id_envio,))
        return cur.fetchall()
    finally:
        if conn:
            conn.close()
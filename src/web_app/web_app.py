import os
import shutil
import webbrowser
import sys

# Configurações
PASTA_ORIGEM = "C:\Disciplinas\Python\Provas\PROVA_PY_GRUPO_RAFAEL_GUSTAVO_THIAGO_BRANDELLI\src\web_app\sys_rast_log"  # Pasta onde estão os arquivos PHP/CSS 
PASTA_DESTINO = "C:/xampp/htdocs/sys_rast_log"
URL_SITE = "http://localhost/sys_rast_log/index.php"

def instalar_web():
    print("--- INICIANDO INSTALAÇÃO DA INTERFACE WEB ---")
    
    # 1. Verifica se a pasta de origem existe
    if not os.path.exists(PASTA_ORIGEM):
        print(f"[ERRO] A pasta '{PASTA_ORIGEM}' não foi encontrada.")
        print("Coloque os arquivos (index.php, estilo.css, etc) dentro de uma pasta chamada 'sys_rast_log'.")
        return

    # 2. Cria a pasta no XAMPP (ou limpa se já existir)
    if os.path.exists(PASTA_DESTINO):
        try:
            shutil.rmtree(PASTA_DESTINO)
            print(f"[OK] Limpeza da pasta antiga {PASTA_DESTINO} realizada.")
        except Exception as e:
            print(f"[ERRO] Não foi possível limpar a pasta: {e}")
            return
    
    # 3. Copia os arquivos
    try:
        shutil.copytree(PASTA_ORIGEM, PASTA_DESTINO)
        print(f"[SUCESSO] Arquivos copiados para {PASTA_DESTINO}")
    except Exception as e:
        print(f"[ERRO] Falha ao copiar arquivos: {e}")
        return

    # 4. Abre o navegador
    print(f"[ABRINDO] Iniciando navegador em: {URL_SITE}")
    webbrowser.open(URL_SITE)

if __name__ == "__main__":
    # Verifica se está rodando como administrador (necessário para escrever no C:)
    try:
        instalar_web()
    except PermissionError:
        print("[ERRO] Permissão negada. Execute o terminal como Administrador.")
    input("\nPressione ENTER para sair...")
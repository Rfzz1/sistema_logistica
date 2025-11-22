# Sistema de Rastreamento Logístico 

O projeto consiste em um sistema de rastreamento de encomendas feito em *3 interfaces distintas*, sendo em *GUI* feita em python, Sistema em *console* feito em python e um *sistema web* feito em HTML, PHP e CSS, todos integrados em um *Banco de Dados* feito em MySQL. O projeto foi desenvolvido para atender a uma demanda estabelecida durante a prova final de Programação em Python do Curso Técnico em Desenvolvimento de Sistemas do SENAI-RS.

## Pré-Requisitos de instalações para o funcionamento das interfaces 
**Instalação do programa XAMPP Control Panel**
    * Acesse: [text](https://www.apachefriends.org/pt_br/index.html)
    * Clique em XAMPP para Windows
    * Irá aparecer uma janela pop-up do seu explorador de arquivos. aLI, Escolha onde quer instalar o xampp, de preferência no seu disco local C
    * Inicialize esse instalador e siga as instruções
**Instalação do python**
    * Acesse: [text](https://www.python.org/downloads/)
    * Clique em ``Download Python install manager``
    * Faça o download no disco local c
**Instalação das bibliotecas CustomTkinter, Datetime, mysql.connector, hashlib, random, uuid, time e pymysql**
    - Utilize o código modelo abaixo para todas as bibliotecas descrtitas: ```py -m pip install biblioteca``

## Instruções de instalação e funcionamento
Instale o arquivo zip e extraia ele
### Sobre o Sistema na Interface GUI Para rodar o sistema na interface GUI
É necessário abrir a pasta"PROVA_PY_GRUPO_RAFAEL_GUSTAVO_THIAGO_BRANDELLI" que está dentro do zip. dentro dela, é necessário abrir a pasta "build", onde o haverá o arquivo executável gui_executable.exe". antes de abrir o arquivo, é necessário inicializar o serviço de MySQL, dentro do XAMPP Control Panel, para inicializar o serviço de Banco de Dados em servidor local. após esse processo, abra o arquivo "gui_executable.exe" e estará funcionando. 
### Sobre o Sistema em Console Para rodar o sistema feito em Console
É necessário abrir a pasta "PROVA_PY_GRUPO_RAFAEL_GUSTAVO_THIAGO_BRANDELLI". dentro dela, é necessário abrir a pasta "build", onde o haverá o arquivo executável "cli_executable.exe". antes de abrir o arquivo, é necessário inicializar o serviço de MySQL, dentro do XAMPP Control Panel, para inicializar o serviço de Banco de Dados em servidor local. após esse processo, abra o arquivo "cli_executable.exe" e estará funcionando. 
### Sobre o sistema Web Para rodar o sistema Web
É necessário abrir a pasta "PROVA_PY_GRUPO_RAFAEL_GUSTAVO_THIAGO_BRANDELLI". dentro dela, é necessário abrir a pasta "build", onde o haverá o arquivo executável "web_executable.py". antes de abrir o arquivo, é necessário inicializar o serviço de MySQL e de Apache, dentro do XAMPP Control Panel, para inicializar o serviço de Banco de Dados e de servidor Web em servidor local. após esse processo, abra o arquivo "web_executable.py", que instalará o programa web na sua máquina, e daí estará funcionando.

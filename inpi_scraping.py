# ########################################################## #
# ##                  Web Scraping Script                 ## #
# ##               Author: Your Name Here                 ## #
# ##               Date:   September, 2023                ## #
# ##               Version: 1.0                           ## #
# ##               Description:                           ## #
# ##               This script performs web scraping      ## #
# ##               of patent data from the INPI website.  ## #
# ########################################################## #


# Importação das bibliotecas necessárias
from bs4 import BeautifulSoup
import requests
import re
import csv
import time
import os

# URL base e cabeçalhos para as requisições HTTP
_base_url_ = "busca.inpi.gov.br"
_headers_ = {"User-Agent":"Mozilla/5.0"}
session = requests.Session()
session.headers.update(_headers_)

# Função para realizar uma requisição de login e obter os cookies
def login_request(url_part):
    # Envia uma requisição do tipo GET para obter os cookies de login
    retries = 3
    delay = 5  # segundos
    for _ in range(retries):
        try:
            url = f"https://{_base_url_}{url_part}"
            login_response = session.get(url)
            cookies = login_response.cookies
            return cookies
        except requests.exceptions.ConnectionError as e:
            print(f"Erro de conexão: {e}")
            print("Tentando novamente em um momento...")
            time.sleep(delay)
    return None  # Retorna None se as tentativas se esgotarem

# Função para realizar uma requisição de URL e extrair links
def result_url_request(url_part, cookies, pedido):
    # Preparação dos dados do formulário
    form_data = {
        "Action": "SearchBasico",
        "NumPedido": pedido,
        "RegisterPerPage": "20"
    }

    # Envio do formulário usando uma requisição POST
    url = f"https://{_base_url_}{url_part}"
    result_response = requests.post(url, data=form_data, cookies=cookies, headers=_headers_)

    time.sleep(3)

    # Análise da resposta HTML
    parsed_response = BeautifulSoup(result_response.content, "html.parser")

    # Encontrar todas as tags de âncora com atributo "href" começando com "/pePI/servlet/PatenteServletController"
    for link in parsed_response.find_all('a', attrs={'href': re.compile("^/pePI/servlet/PatenteServletController")}):
        # Exibir as URLs encontradas
        print(link.get('href'))
        return link.get('href')

# Função para realizar uma requisição de URL e extrair dados
def result_data_request(row, cookies):
    # Preparação dos dados fictícios do formulário
    form_data = {
        "Action": "SearchBasico",
        "NumPedido": "PI0406712", # Não importa muito, só precisamos passar pelo site para prosseguir com a busca
        "RegisterPerPage": "20"
    }

    # Envio do formulário usando uma requisição POST
    url = f"https://{_base_url_}{'/pePI/servlet/PatenteServletController'}"
    result_response = requests.post(url, data=form_data, cookies=cookies, headers=_headers_)

    time.sleep(3)

    # Após isso, continua com a busca...

    # Formatação da URL da patente
    # Extrai a URL da lista de entrada
    url_part = row[0].strip()  # Remove espaços em branco no início/fim

    # Substitui espaços por '%20'
    url_part_encoded = url_part.replace(" ", "%20")

    # Concatena a URL base com a parte da URL codificada
    url = f"https://{_base_url_}{url_part_encoded}"
    
    result_response = session.get(url, cookies=cookies, timeout=10)
    time.sleep(3)

    data_result = BeautifulSoup(result_response.content, "html.parser")

    country = number = date = "-"
    # Encontrar a linha da tabela relevante para informações de prioridade
    priority_tag = data_result.find('font', class_='alerta', string='(30)')
    if priority_tag:
        priority_row = priority_tag.find_parent('tr')

        # Extrair valores da linha de prioridade
        if priority_row:
            priority_info = priority_row.find_all('font', class_='alerta')
            if len(priority_info) >= 6:
                country = priority_info[4].get_text(strip=True)
                number = priority_info[5].get_text(strip=True)
                date = priority_info[6].get_text(strip=True)

    # Extração da classificação IPC
    ipc_tag = data_result.find('font', class_='normal', string='Classificação IPC:')
    siglasIPC = []
    descIPC = []

    if ipc_tag:
        a_tags_with_onmouseout = data_result.select('a[onmouseout^="hideMe(\'classificacao"]')
        # Extrair os valores dentro das tags <a>
        siglasIPC = [a.get_text(strip=True) for a in a_tags_with_onmouseout]
        
        div_tags = ipc_tag.find_all_next('div', id=lambda x: x and x.startswith('classificacao'))
        for div in div_tags:
            desc = div.find('font', class_='normal').get_text(strip=True)
            descIPC.append(desc)

    # Extração da classificação CPC
    cpc_tag = data_result.find('font', class_='normal', string='Classificação CPC:')
    siglasCPC = []
    descCPC = []

    if cpc_tag:
        a_tags_with_onmouseout = data_result.select('a[onmouseout^="hideMe(\'classificacaocpc"]')
        # Extrair os valores dentro das tags <a>
        siglasCPC = [a.get_text(strip=True) for a in a_tags_with_onmouseout]
        
        div_tags = ipc_tag.find_all_next('div', id=lambda x: x and x.startswith('classificacaocpc'))
        for div in div_tags:
            desc = div.find('font', class_='normal').get_text(strip=True)
            descCPC.append(desc)

    # Tratamento de informações que não estão presentes em todas as patentes
    depositante = titular = fasenacional = pct = wo = dividido = "-"

    if data_result.find('font', class_='normal', string='Nome do Depositante:'):
        depositante = data_result.find('font', class_='normal', string='Nome do Depositante:').find_next('font', class_='normal').get_text(strip=True)

    if data_result.find('font', class_='normal', string='Nome do Titular:'):
        titular = data_result.find('font', class_='normal', string='Nome do Titular:').find_next('font', class_='normal').get_text(strip=True)

    if data_result.find('font', class_='normal', string='Início da Fase Nacional:'):
        fasenacional = data_result.find('font', class_='normal', string='Início da Fase Nacional:').find_next('font', class_='normal').get_text(strip=True)
    
    if data_result.find('font', class_='normal', string='PCT'):
        pct_number = data_result.find('font', class_='normal', string='PCT').find_next('font', class_='normal').find_next('font', class_='normal').get_text(strip=True)
        pct_date = data_result.find('font', class_='normal', string='PCT').find_next('font', class_='normal').find_next('font', class_='normal').find_next('font', class_='normal').find_next('font', class_='normal').get_text(strip=True)
        pct = [pct_number, pct_date]

    if data_result.find('font', class_='normal', string='W.O.'):
        wo_number = data_result.find('font', class_='normal', string='W.O.').find_next('font', class_='normal').find_next('font', class_='normal').get_text(strip=True)
        wo_date = data_result.find('font', class_='normal', string='W.O.').find_next('font', class_='normal').find_next('font', class_='normal').find_next('font', class_='normal').find_next('font', class_='normal').get_text(strip=True)
        wo = [wo_number, wo_date]

    if data_result.find('font', class_='normal', string='Número Dividido:'):
        dividido = data_result.find('font', class_='normal', string='Número Dividido:').find_next('font', class_='normal').get_text(strip=True)

    # Dicionário vazio para armazenar os elementos de dados extraídos
    data = {
        "numeroPedido": data_result.find('font', class_='marcador').get_text(strip=True),                                                                           # (21)
        "dataDeposito": data_result.find('font', class_='normal', string='Data do Depósito:').find_next('font', class_='normal').get_text(strip=True),              # (22)
        "dataPublicacao": data_result.find('font', class_='normal', string='Data da Publicação:').find_next('font', class_='normal').get_text(strip=True),          # (43)
        "dataConcessao": data_result.find('font', class_='normal', string='Data da Concessão:').find_next('font', class_='normal').get_text(strip=True),            # (47)
        "puPais": country or "-",                                                                                                                                   # PRIORIDADE UNIONISTA (30) -> (33)
        "puNumero": number or "-",                                                                                                                                  # PRIORIDADE UNIONISTA (30) -> (31)
        "puData": date or "-",                                                                                                                                      # PRIORIDADE UNIONISTA (30) -> (32)
        "siglasIPC": siglasIPC,                                                                                                                                     # (51)
        "descIPC": descIPC, 
        "siglasCPC": siglasCPC or "-",                                                                                                                               # (52)
        "descCPC": descCPC or "-",
        "titulo": data_result.find('div', id='tituloContext').find('font').get_text(strip=True),                                                                    # (54)
        "resumo": data_result.find('div', id='resumoContext').find('font').get_text(strip=True),                                                                    # (57)
        "nomeDepositante": depositante,                                                                                                                             # (71)
        "nomeInventor": data_result.find('font', class_='normal', string='Nome do Inventor:').find_next('font', class_='normal').get_text(strip=True),              # (72)
        "nomeTitular": titular,                                                                                                                                     # (73)
        "nomeProcurador": data_result.find('font', class_='normal', string=' Nome do Procurador:').find_next('font', class_='normal').get_text(strip=True),         # (74), aqui há um espaço em branco antes do conteúdo
        "inicioFaseNacional": fasenacional,                                                                                                                         # (85)
        "numPCT": pct,                                                                                                                                              # (86)
        "numWO": wo,                                                                                                                                                # (87)
        "numeroDividido": dividido,
    }
    
    return data

# Função para realizar a raspagem das URLs
def url_scraping(input_filename, output_filename, start_from, cookies):
    # Verificar se o arquivo de saída já existe
    file_exists = os.path.exists(output_filename)

    with open(input_filename, 'r') as file:
        csvreader = csv.reader(file)
        
        # Inicializar uma flag para determinar quando começar a escrever no arquivo de saída
        start_writing = False

        for row in csvreader:
            # Se start_from estiver especificado e ainda não foi alcançado, continue para a próxima linha
            if start_from and not start_writing:
                if row[0] == start_from:
                    start_writing = True
                continue

            link = result_url_request("/pePI/servlet/PatenteServletController", cookies, row)

            # Abrir o arquivo de saída no modo de anexar ('a') ou no modo de escrita ('w') conforme necessário
            with open(output_filename, 'a' if file_exists else 'w', newline='') as output_file:
                writer = csv.writer(output_file)
                writer.writerow([link])

            file_exists = True  # O arquivo de saída agora existe

# Função para realizar a raspagem dos dados
def data_scraping(input_filename, output_filename, start_from, cookies):
    # Verificar se o arquivo de saída já existe
    file_exists = os.path.exists(output_filename)

    extracted_data = []

    with open(input_filename, 'r') as file:
        csvreader = csv.reader(file)
        
        # Inicializar uma flag para determinar quando começar a escrever no arquivo de saída
        start_writing = False

        for row in csvreader:
            if not start_writing:
                if row[0] == start_from:
                    start_writing = True
                continue

            if row:
                data = result_data_request(row[0], cookies)
                extracted_data.append(data)

                # Abrir o arquivo de saída no modo de anexar ('a') ou no modo de escrita ('w') conforme necessário
                with open(output_filename, 'a' if file_exists else 'w', newline='', encoding='utf-8') as csvfile:
                    csv_writer = csv.writer(csvfile, delimiter='\t')

                    # Se o arquivo de saída ainda não existe, escreva a linha de cabeçalho
                    if not file_exists:
                        header = data.keys()
                        csv_writer.writerow(header)
                        file_exists = True

                    # Escrever a linha de dados
                    row_values = [data[key] for key in header]
                    csv_writer.writerow(row_values)

# Função principal
def main():
    # 1 - Passa pela página de login, obtendo os cookies necessários
    cookies = login_request("/pePI/servlet/LoginController?action=login")
    if cookies is None:
        print("Não foi possível estabelecer conexão após as tentativas.")
    else:
        print("Conexão bem-sucedida!")
        # 2 - Leitura de parâmetros
        input_filename = str(input("Nome do arquivo de entrada: ")).rstrip() # Nome do arquivo de entrada
        output_filename = str(input("Nome do arquivo de saída: ")).rstrip() # Nome do arquivo de saída
        start_from = str(input("Primeira linha a ser lida: "))
        op = int(input("Operação a ser realizada: ")) # i ∈ [0,1]

        # 3 - Direciona para a operação escolhida
        match op:
            case 0:
                print("Realizando a extração de URL (OP: 0)")
                print()
                url_scraping(input_filename, output_filename, start_from, cookies)

            case 1:
                print("Realizando a extração de dados (OP: 1)")
                print()
                data_scraping(input_filename, output_filename, start_from, cookies)
            case _:
                print("Operação inválida")
        
        print("Raspagem de dados finalizada.")

# Executar a função principal se o script for executado diretamente
if __name__ == "__main__":
    main()
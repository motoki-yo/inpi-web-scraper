# ######################################################### #
# ## Web Scraping The INPI Site                          ## #
# ######################################################### #

from bs4 import BeautifulSoup
import requests
import re
import csv
import time

_base_url_ = "busca.inpi.gov.br"
_headers_ = {"User-Agent":"Mozilla/5.0"}
session = requests.Session()
session.headers.update(_headers_)

def login_request(url_part):
    # Envia uma requisição do tipo GET para obter os cookies de login
    retries = 3
    delay = 5  # seconds
    for _ in range(retries):
        try:
            url = f"https://{_base_url_}{url_part}"
            login_response = session.get(url)
            cookies = login_response.cookies
            return cookies
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
            print("Retrying in a moment...")
            time.sleep(delay)
    return None  # Return None if retries are exhausted

def result_url_request(url_part, cookies, pedido):
    # Prepare form data
    form_data = {
        "Action": "SearchBasico",
        "NumPedido": pedido,
        "RegisterPerPage": "20"
    }

    # Submit the form using POST request
    url = f"https://{_base_url_}{url_part}"
    result_response = requests.post(url, data=form_data, cookies=cookies, headers=_headers_)

    time.sleep(3)

    # Parse the response
    parsed_response = BeautifulSoup(result_response.content, "html.parser")

    # find all the anchor tags with "href"  
    # attribute starting with "/pePI/servlet/PatenteServletController"
    for link in parsed_response.find_all('a', attrs={'href': re.compile("^/pePI/servlet/PatenteServletController")}):
        # display the actual urls
        print(link.get('href'))
        return link.get('href')

def result_data_request(row, cookies):
    # Prepare dummy form data
    form_data = {
        "Action": "SearchBasico",
        "NumPedido": "PI0406712", # não importa muito, só precisamos passar pelo site para prosseguir com a busca
        "RegisterPerPage": "20"
    }
    # Submit the form using POST request
    url = f"https://{_base_url_}{'/pePI/servlet/PatenteServletController'}"
    result_response = requests.post(url, data=form_data, cookies=cookies, headers=_headers_)

    time.sleep(3)

    # Após isso, continua com a busca...

    # Formata a URL da patente
    # Extract the URL from the row list
    url_part = row[0].strip()  # Remove any leading/trailing spaces

    # Replace spaces with '%20'
    url_part_encoded = url_part.replace(" ", "%20")

    # Concatenate the base URL with the encoded URL part
    url = f"https://{_base_url_}{url_part_encoded}"
    
    result_response = session.get(url, cookies=cookies, timeout=10)
    time.sleep(3)

    data_result = BeautifulSoup(result_response.content, "html.parser")

    country = number = date = "-"
    # Find the relevant table row for priority information
    priority_tag = data_result.find('font', class_='alerta', string='(30)')
    if priority_tag:
        priority_row = priority_tag.find_parent('tr')

        # Extract values from the priority row
        if priority_row:
            priority_info = priority_row.find_all('font', class_='alerta')
            if len(priority_info) >= 6:
                country = priority_info[4].get_text(strip=True)
                number = priority_info[5].get_text(strip=True)
                date = priority_info[6].get_text(strip=True)

    # Extração da classificação IPC
    # Find the relevant table row for IPC classifications
    ipc_tag = data_result.find('font', class_='normal', string='Classificação IPC:')
    siglasIPC = []
    descIPC = []

    if ipc_tag:
        a_tags_with_onmouseout = data_result.select('a[onmouseout^="hideMe(\'classificacao"]')
        # Extract the values inside the <a> tags
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
        # Extract the values inside the <a> tags
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


    # Empty dictionary that will store the extracted data elements
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
    
    #print("Pedido: ", data_result.find('font', class_='marcador').get_text(strip=True))
    #print(data)
    #print()

    return data
    
    

# Extrai as URLs
def url_scraping(input_filename, output_filename, cookies):
    links = []
    # Leitura do arquivo de entrada, contendo os números de protocolo das patentes
    with open(input_filename, 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            link = result_url_request("/pePI/servlet/PatenteServletController",cookies, row)
            links.append(link)

    with open(output_filename,'w') as file:
        writer = csv.writer(file)
        for link in links:
            writer.writerow([link])


# Extrai os dados
def data_scraping(input_filename, output_filename, cookies):
    extracted_data = []
    # Leitura do arquivo de entrada, contendo a URL de cada patente a ser consultada
    with open(input_filename, 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if row:
                extracted_data.append(result_data_request(row, cookies))

    # Write the data to a CSV file with tab separator
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter='\t')

        # Write the header row
        header = extracted_data[0].keys()  # Assuming at least one row exists
        csv_writer.writerow(header)

        # Write the data rows
        for data_row in extracted_data:
            row_values = [data_row[key] for key in header]
            csv_writer.writerow(row_values)
                    


def main():
    # 1 - Passa pela página de login, obtendo os cookies necessários
    cookies = login_request("/pePI/servlet/LoginController?action=login")
    if cookies is None:
        print("Unable to establish connection after retries.")
    else:
        print("Connection successful!")
        # 2 - Leitura de parâmetros
        input_filename = str(input("Nome do arquivo de entrada: ")).rstrip() # nome do arquivo de entrada
        output_filename = str(input("Nome do arquivo de saida: ")).rstrip() # nome do arquivo de saída
        op = int(input("Operacao a ser realizada: ")) # i ∈ [0,1]

        # 3 - Direciona para a operação escolhida
        match op:
            case 0:
                print("Realizando a extração de URL (OP: 0)")
                print()
                url_scraping(input_filename, output_filename, cookies)

            case 1:
                print("Realizando a extração de dados (op 1)")
                print()
                data_scraping(input_filename, output_filename, cookies)
            case _:
                print("Operacao invalida")
        
        print("Raspagem de dados finalizada.")

    

if __name__ == "__main__":
    main()
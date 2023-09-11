# README - Web Scraping do INPI

Este README fornece instruções sobre como utilizar o código de web scraping para extrair informações do site do INPI (Instituto Nacional da Propriedade Industrial).

## Descrição do Código

O código Python fornecido utiliza as bibliotecas BeautifulSoup e Requests para realizar web scraping no site do INPI. Ele é capaz de realizar duas operações principais:

1. **Extração de URLs**: Esta operação permite obter as URLs das patentes com base em números de protocolo fornecidos em um arquivo CSV de entrada. As URLs são então salvas em um arquivo CSV de saída.

2. **Extração de Dados**: Esta operação permite extrair informações detalhadas de patentes com base nas URLs fornecidas em um arquivo CSV de entrada. As informações extraídas incluem detalhes da patente, classificações IPC e CPC, dados do depositante, datas importantes e muito mais. Os dados extraídos são salvos em um arquivo CSV de saída.

## Instruções de Uso

Siga estas etapas para utilizar o código de web scraping do INPI:

1. **Requisitos de Instalação**:

   - Certifique-se de ter o Python 3 instalado em seu sistema.
   - Instale as bibliotecas necessárias executando o seguinte comando:

     ```
     pip install beautifulsoup4 requests
     ```

2. **Preparação de Arquivos**:

   - Crie um arquivo CSV de entrada contendo os números de protocolo das patentes que deseja consultar (um código de patente por linha).
   - Escolha ou crie um arquivo CSV de saída para armazenar as URLs extraídas ou os dados das patentes, dependendo da operação que deseja realizar.

3. **Execução do Código**:

   - Execute o código Python fornecido, que solicitará informações como o nome do arquivo de entrada, o nome do arquivo de saída e a operação desejada (0 para Extração de URLs e 1 para Extração de Dados).
   - O código realizará a operação escolhida e salvará os resultados no arquivo de saída especificado.

4. **Acompanhamento**:

   - O progresso da execução será exibido no terminal, incluindo mensagens informativas e de erro.

## Exemplo de Uso

No repositório onde se encontram o código e os arquivos, digite, no terminal (prompt de comando):

     ```
     python inpi_scraping.py
     ```

Aqui está um exemplo de como utilizar o código:

1. Crie um arquivo CSV de entrada chamado `patentes.csv` contendo os números de protocolo das patentes a serem consultadas.

2. Execute o código Python e siga as instruções. Por exemplo, para extrair URLs, você pode escolher a operação 0 e fornecer o nome do arquivo de entrada como `patentes.csv` e o nome do arquivo de saída como `urls.csv`.

3. O código realizará a extração e salvará as URLs no arquivo `urls.csv`.

4. Para extrair dados detalhados, você pode escolher a operação 1 e fornecer os mesmos arquivos de entrada e saída.

5. Os dados detalhados serão extraídos e salvos no arquivo `dados_patentes.csv`.

Certifique-se de que os arquivos de entrada e saída estejam no mesmo diretório em que você executa o código.

## Notas Importantes

- O código utiliza o site do INPI para realizar web scraping, portanto, esteja ciente das políticas de uso e da possibilidade de bloqueio por parte do site do INPI se houver uso excessivo.

- Este código é fornecido apenas para fins educacionais e de demonstração. Respeite os termos de uso e políticas de privacidade do site do INPI ao utilizá-lo.

- Esteja ciente de que a estrutura do site do INPI pode mudar ao longo do tempo, o que pode exigir ajustes no código para garantir seu funcionamento correto.

- O código pode ser modificado e personalizado de acordo com suas necessidades específicas.

- Certifique-se de possuir as permissões necessárias para acessar e utilizar os dados do INPI.

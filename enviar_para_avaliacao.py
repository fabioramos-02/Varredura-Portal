import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep

# Configurações
LIMITE_ARQUIVOS_POR_LOTE = 5  # Quantidade de arquivos por lote
NUM_THREADS = 6  # Número de threads para processar os lotes paralelamente
NUM_ARQUIVOS_A_PROCESSAR = None  # Defina o número de arquivos que deseja processar ou coloque None para processar todos os arquivos.

# Função para enviar arquivos para avaliação
def enviar_arquivos_para_avaliacao(arquivos_txt, url):
    """
    Envia um lote de arquivos para avaliação usando requests.
    """
    print(f"Enviando lote de {len(arquivos_txt)} arquivos para avaliação...")

    files = []
    for arquivo in arquivos_txt:
        arquivo_absoluto = os.path.join(os.getcwd(), 'Servicos', arquivo)  # Garantir o caminho correto
        
        # Verifique se o arquivo existe antes de tentar enviá-lo
        if not os.path.exists(arquivo_absoluto):
            print(f"Arquivo não encontrado: {arquivo_absoluto}")
            continue  # Ignora o arquivo que não foi encontrado
        
        files.append(('files', open(arquivo_absoluto, 'rb')))  # Envia o arquivo em modo binário

    try:
        # Envia os arquivos via POST
        response = requests.post(url, files=files)

        # Fechar os arquivos após o envio
        for file in files:
            file[1].close()

        # Verifique se a resposta foi bem-sucedida
        if response.status_code == 200:
            print(f"Arquivos enviados com sucesso!")
            return response.text  # Retorna o HTML gerado após o envio
        else:
            print(f"Erro ao enviar arquivos. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar os arquivos: {e}")
        return None

# Função para extrair pontuações da tabela HTML gerada
def extrair_pontuacoes(html_resultado):
    """
    Extrai pontuações da página HTML.
    """
    soup = BeautifulSoup(html_resultado, 'html.parser')
    tabela = soup.find('table', class_='TabelaNotas')
    
    pontuacoes = []
    if tabela:
        for row in tabela.find_all('tr')[1:]:  # Ignora o cabeçalho
            cols = row.find_all('td')
            if len(cols) == 13:
                nome_arquivo = cols[0].text.strip()
                notas = [col.text.strip() for col in cols[1:]]
                pontuacoes.append([nome_arquivo] + notas)
    else:
        print("Tabela de pontuações não encontrada!")
    
    return pontuacoes

# Função para salvar as pontuações extraídas em um arquivo Excel
def salvar_pontuacoes_em_excel(pontuacoes, output_file='resultado_avaliacao.xlsx'):
    """
    Salva as pontuações extraídas em um arquivo Excel.
    """
    if pontuacoes:
        colunas = [
            "Nome do Arquivo", "Nota 2.1", "Nota 2.2", "Nota 2.3", "Nota 2.4", "Nota 2.5", "Nota 2.6", "Nota 2.7", 
            "Nota 2.2 - Começa com verbo", "Nota 2.2 - Está entre 3 a 5 palavras", "Nota 2.2 - Verbo no infinitivo", 
            "Nota 2.3 - Acima de 10 palavras", "Nota 2.3 - Frases com duas ações"
        ]
        df = pd.DataFrame(pontuacoes, columns=colunas)
        df.to_excel(output_file, index=False)
        print(f"Pontuações salvas em {output_file}")
    else:
        print("Nenhuma pontuação para salvar.")

# Função para mesclar os resultados com a planilha servicos.xlsx
def mesclar_com_servicos(servicos_df, resultados_df, output_file='resultados_finais.xlsx'):
    """
    Mescla os resultados da avaliação com a planilha servicos.xlsx.
    """
    # Mesclar com base no nome do arquivo
    resultados_finais = pd.merge(servicos_df, resultados_df, left_on='titulo', right_on='Nome do Arquivo', how='left')
    
    # Salvar o arquivo final na pasta 'Planilhas'
    os.makedirs('Planilhas', exist_ok=True)
    output_file = os.path.join('Planilhas', output_file)
    resultados_finais.to_excel(output_file, index=False)
    print(f"Resultados finais mesclados e salvos em {output_file}")

# Função para processar os arquivos em lotes de forma paralela
def processar_lotes(arquivos_txt, url, servicos_df):
    """
    Processa os arquivos em lotes e mescla os resultados com a planilha de serviços.
    """
    lote_size = LIMITE_ARQUIVOS_POR_LOTE
    resultados = []

    # Se NUM_ARQUIVOS_A_PROCESSAR não for None, limite o número de arquivos a serem processados
    if NUM_ARQUIVOS_A_PROCESSAR is not None:
        arquivos_txt = arquivos_txt[:NUM_ARQUIVOS_A_PROCESSAR]

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = []
        
        # Envia os lotes de arquivos para avaliação paralelamente
        for i in range(0, len(arquivos_txt), lote_size):
            lote = arquivos_txt[i:i + lote_size]
            futures.append(executor.submit(enviar_arquivos_para_avaliacao, lote, url))
        
        # Processa os resultados dos lotes assim que cada um terminar
        for future in as_completed(futures):
            html_resultado = future.result()
            if html_resultado:
                pontuacoes = extrair_pontuacoes(html_resultado)
                resultados.extend(pontuacoes)
        
        # Salvar as pontuações
        salvar_pontuacoes_em_excel(resultados)
        
        # Mesclar os resultados com a planilha servicos.xlsx
        resultados_df = pd.DataFrame(resultados, columns=[ 
            "Nome do Arquivo", "Nota 2.1", "Nota 2.2", "Nota 2.3", "Nota 2.4", "Nota 2.5", "Nota 2.6", "Nota 2.7", 
            "Nota 2.2 - Começa com verbo", "Nota 2.2 - Está entre 3 a 5 palavras", "Nota 2.2 - Verbo no infinitivo", 
            "Nota 2.3 - Acima de 10 palavras", "Nota 2.3 - Frases com duas ações"
        ])
        mesclar_com_servicos(servicos_df, resultados_df)

# Função principal
def main():
    url_avaliacao = "https://linguagem-simples.ligo.go.gov.br/avaliararquivos"
    pasta_servicos = 'Servicos'
    arquivos_txt = [f for f in os.listdir(pasta_servicos) if f.endswith('.txt')]

    # Carregar a planilha servicos.xlsx
    servicos_df = pd.read_excel('Planilhas/servicos.xlsx')

    # Processar os lotes de arquivos
    processar_lotes(arquivos_txt, url_avaliacao, servicos_df)

if __name__ == "__main__":
    main()

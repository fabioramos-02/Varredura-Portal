import os
import requests
import pandas as pd
from bs4 import BeautifulSoup

def enviar_arquivos_para_avaliacao(arquivos_txt, url):
    """
    Envia um lote de arquivos para avaliação usando requests (sem Selenium).
    """
    print(f"Enviando lote de {len(arquivos_txt)} arquivos para avaliação...")

    # Prepare os arquivos para envio
    files = []
    for arquivo in arquivos_txt:
        arquivo_absoluto = os.path.join(os.getcwd(), 'Servicos', arquivo)  # Garantir o caminho correto
        print(f"Enviando arquivo: {arquivo_absoluto}")
        
        # Verifique se o arquivo existe antes de tentar enviá-lo
        if not os.path.exists(arquivo_absoluto):
            print(f"Arquivo não encontrado: {arquivo_absoluto}")
            continue  # Ignora o arquivo que não foi encontrado
        
        files.append(('files', open(arquivo_absoluto, 'rb')))  # Envia o arquivo em modo binário

    # Envia os arquivos via POST
    response = requests.post(url, files=files)

    # Fechar os arquivos após o envio
    for file in files:
        file[1].close()

    # Verifique se a resposta foi bem-sucedida
    if response.status_code == 200:
        print("Arquivos enviados com sucesso!")
        return response.text
    else:
        print(f"Erro ao enviar arquivos. Status code: {response.status_code}")
        return None

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

def mesclar_com_servicos(servicos_df, resultados_df, output_file='resultados_finais.xlsx'):
    """
    Mescla os resultados da avaliação com a planilha servicos.xlsx.
    """
    # Mesclar com base no nome do arquivo
    resultados_finais = pd.merge(servicos_df, resultados_df, left_on='titulo', right_on='Nome do Arquivo', how='left')
    
    # Salvar o arquivo final
    resultados_finais.to_excel(output_file, index=False)
    print(f"Resultados finais mesclados e salvos em {output_file}")

def processar_lotes(arquivos_txt, url, servicos_df):
    """
    Processa os arquivos em lotes de 5 por vez e mescla os resultados com a planilha de serviços.
    """
    lote_size = 5
    for i in range(0, len(arquivos_txt), lote_size):
        lote = arquivos_txt[i:i + lote_size]
        
        # Enviar os arquivos do lote para avaliação
        html_resultado = enviar_arquivos_para_avaliacao(lote, url)
        if not html_resultado:
            continue  # Se o envio falhar, pula para o próximo lote
        
        # Extrair as pontuações da avaliação
        pontuacoes = extrair_pontuacoes(html_resultado)
        
        # Salvar as pontuações em um arquivo Excel
        salvar_pontuacoes_em_excel(pontuacoes)
        
        # Mesclar os resultados com os dados da planilha servicos.xlsx
        resultados_df = pd.DataFrame(pontuacoes, columns=[ 
            "Nome do Arquivo", "Nota 2.1", "Nota 2.2", "Nota 2.3", "Nota 2.4", "Nota 2.5", "Nota 2.6", "Nota 2.7", 
            "Nota 2.2 - Começa com verbo", "Nota 2.2 - Está entre 3 a 5 palavras", "Nota 2.2 - Verbo no infinitivo", 
            "Nota 2.3 - Acima de 10 palavras", "Nota 2.3 - Frases com duas ações"
        ])
        mesclar_com_servicos(servicos_df, resultados_df)

def main():
    url_avaliacao = "https://linguagem-simples.ligo.go.gov.br/avaliararquivos"
    pasta_servicos = 'Servicos'
    arquivos_txt = [f for f in os.listdir(pasta_servicos) if f.endswith('.txt')]

    # Carregar a planilha servicos.xlsx
    servicos_df = pd.read_excel('servicos.xlsx')

    # Processar os lotes de arquivos
    processar_lotes(arquivos_txt, url_avaliacao, servicos_df)

if __name__ == "__main__":
    main()

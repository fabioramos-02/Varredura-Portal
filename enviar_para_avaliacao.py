import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time

def enviar_arquivo_para_avaliacao(arquivo_txt, url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Para rodar sem abrir a janela do navegador
    chrome_options.add_argument("--disable-gpu")  # Opcional para evitar problemas com gráficos
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        print(f"Acessando o site de avaliação: {url}")
        
        # Espera o carregamento completo do formulário
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'files')))
        
        # Enviar o arquivo .txt
        input_arquivo = driver.find_element(By.NAME, 'files')
        arquivo_absoluto = os.path.abspath(arquivo_txt)
        input_arquivo.send_keys(arquivo_absoluto)
        
        # Clicar no botão "Enviar"
        botao_enviar = driver.find_element(By.ID, 'EnviarFiles')
        botao_enviar.click()
        
        # Esperar até que os resultados sejam carregados
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'alerta')))
        
        print(f"Arquivo {arquivo_txt} enviado com sucesso!")
        
        # Obter o HTML da página com as pontuações
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Verifique a tabela
        tabela = soup.find('table', class_='TabelaNotas')
        if tabela:
            print("Tabela encontrada!")
            
            pontuacoes = []
            for row in tabela.find_all('tr')[1:]:  # Ignorar a linha de título
                cols = row.find_all('td')
                if len(cols) == 13:  # Verificar se a linha tem 13 colunas
                    nome_arquivo = cols[0].text.strip()
                    notas = [col.text.strip() for col in cols[1:]]
                    pontuacoes.append([nome_arquivo] + notas)
                else:
                    print(f"Linha com número inesperado de colunas: {len(cols)}")
            return pontuacoes
        else:
            print("Tabela de pontuação não encontrada.")
            return []
    finally:
        driver.quit()  # Fechar o navegador

def salvar_pontuacoes_em_excel(pontuacoes, output_file='pontuacoes_servicos.xlsx'):
    if pontuacoes:
        colunas = [
            "Nome do Arquivo", "Nota 2.1", "Nota 2.2", "Nota 2.3", "Nota 2.4", "Nota 2.5", "Nota 2.6", "Nota 2.7", 
            "Nota 2.2 - Começa com verbo", "Nota 2.2 - Está entre 3 a 5 palavras", "Nota 2.2 - Verbo no infinitivo", 
            "Nota 2.3 - Acima de 10 palavras", "Nota 2.3 - Frases com duas ações"
        ]
        
        # Criar um DataFrame com os dados
        df = pd.DataFrame(pontuacoes, columns=colunas)
        print(f"Salvando as seguintes pontuações no Excel: {df.head()}")

        # Salvar o DataFrame em um arquivo Excel
        df.to_excel(output_file, index=False)
        print(f"Pontuações salvas em {output_file}")
    else:
        print("Nenhuma pontuação para salvar.")

def extrair_pontuacoes(html_resultado):
    soup = BeautifulSoup(html_resultado, 'html.parser')
    tabela = soup.find('table', class_='TabelaNotas')
    pontuacoes = []
    if tabela:
        for row in tabela.find_all('tr')[1:]:  # Ignorar a linha de título
            cols = row.find_all('td')
            if len(cols) == 13:  # Verificar se a linha tem 13 colunas
                nome_arquivo = cols[0].text.strip()
                notas = [col.text.strip() for col in cols[1:]]
                pontuacoes.append([nome_arquivo] + notas)
    return pontuacoes

def processar_arquivo(arquivo, url_avaliacao):
    """
    Função para processar um arquivo individual, enviando para avaliação e extraindo pontuações.
    """
    arquivo_path = os.path.join('Servicos', arquivo)
    html_resultado = enviar_arquivo_para_avaliacao(arquivo_path, url_avaliacao)
    
    if html_resultado:
        # Extrair as pontuações da resposta HTML
        pontuacoes = extrair_pontuacoes(html_resultado)
        return pontuacoes
    return []

if __name__ == '__main__':
    url_avaliacao = "https://linguagem-simples.ligo.go.gov.br/avaliararquivos"
    num_arquivos_para_processar = 4  # Defina quantos arquivos processar ou use None para todos

    pasta_servicos = 'Servicos'
    arquivos_txt = [f for f in os.listdir(pasta_servicos) if f.endswith('.txt')]

    todas_pontuacoes = []

    # Usar ThreadPoolExecutor para paralelizar o processamento dos arquivos
    with ThreadPoolExecutor() as executor:
        if num_arquivos_para_processar is not None:
            arquivos_txt = arquivos_txt[:num_arquivos_para_processar]

        resultados = executor.map(lambda arquivo: processar_arquivo(arquivo, url_avaliacao), arquivos_txt)

        # Coletar todos os resultados
        for resultado in resultados:
            if resultado:
                todas_pontuacoes.extend(resultado)

    if todas_pontuacoes:
        salvar_pontuacoes_em_excel(todas_pontuacoes)
        for pontuacao in todas_pontuacoes:
            print(pontuacao)

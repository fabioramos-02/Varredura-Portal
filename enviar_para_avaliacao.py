import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from bs4 import BeautifulSoup

def enviar_arquivo_para_avaliacao(arquivo_txt, url):
    """
    Envia o arquivo .txt para a ferramenta de avaliação usando Selenium.
    """
    # Configuração do Selenium para usar o Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Para rodar sem abrir a janela do navegador
    chrome_options.add_argument("--disable-gpu")  # Opcional para evitar problemas com gráficos
    
    # Iniciar o navegador
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Acessar a página de avaliação
        driver.get(url)
        print(f"Acessando o site de avaliação: {url}")
        
        # Espera o carregamento completo do formulário
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'files')))
        
        # Encontrar o campo de input para arquivos e enviar o arquivo
        input_arquivo = driver.find_element(By.NAME, 'files')
        
        # Gerar o caminho absoluto para o arquivo
        arquivo_absoluto = os.path.abspath(arquivo_txt)
        
        input_arquivo.send_keys(arquivo_absoluto)  # Envia o arquivo .txt para o formulário
        
        # Clicar no botão "Enviar"
        botao_enviar = driver.find_element(By.ID, 'EnviarFiles')
        botao_enviar.click()
        
        # Aguardar até que a avaliação seja completada
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'alerta')))
        
        print(f"Arquivo {arquivo_txt} enviado com sucesso!")
        
        # Obter o HTML da página com as pontuações
        time.sleep(3)  # Esperar o tempo necessário para que os dados carreguem completamente
        html = driver.page_source
        
        return html
    
    finally:
        driver.quit()  # Fechar o navegador


def extrair_pontuacoes(html):
    """
    Extrai as pontuações da tabela HTML retornada pela ferramenta de avaliação.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Verificar se a tabela de pontuação existe
    tabela = soup.find('table', class_='TabelaNotas')
    if not tabela:
        print("Tabela de pontuação não encontrada.")
        return None
    
    print("Tabela de pontuação encontrada, extraindo dados...")
    
    # Extrair os dados das linhas da tabela
    pontuacoes = []
    for row in tabela.find_all('tr')[1:]:  # Ignorar a linha de título
        cols = row.find_all('td')
        if len(cols) == 12:  # Verificar se a linha tem 12 colunas
            nome_arquivo = cols[0].text.strip()
            notas = [col.text.strip() for col in cols[1:]]
            pontuacoes.append([nome_arquivo] + notas)

    return pontuacoes


def salvar_pontuacoes_em_excel(pontuacoes, output_file='pontuacoes_servicos.xlsx'):
    """
    Salva as pontuações extraídas em um arquivo Excel.
    """
    # Definir os cabeçalhos da tabela
    colunas = [
        "Nome do Arquivo", "Nota 2.1", "Nota 2.2", "Nota 2.3", "Nota 2.4", "Nota 2.5", "Nota 2.6", "Nota 2.7", 
        "Nota 2.2 - Começa com verbo", "Nota 2.2 - Está entre 3 a 5 palavras", "Nota 2.2 - Verbo no infinitivo", 
        "Nota 2.3 - Acima de 10 palavras", "Nota 2.3 - Frases com duas ações"
    ]
    
    # Criar um DataFrame com os dados
    df = pd.DataFrame(pontuacoes, columns=colunas)
    
    # Salvar o DataFrame em um arquivo Excel
    df.to_excel(output_file, index=False)
    print(f"Pontuações salvas em {output_file}")


if __name__ == '__main__':
    # URL da página de avaliação
    url_avaliacao = "https://linguagem-simples.ligo.go.gov.br/avaliararquivos"
    
    # Definir o número de arquivos a serem processados (use None para processar todos)
    num_arquivos_para_processar = 1  # Ajuste este valor para 3 ou outro número, ou use None para processar todos

    # Caminho da pasta onde os arquivos .txt estão localizados
    pasta_servicos = 'Servicos'

    # Obter todos os arquivos .txt na pasta
    arquivos_txt = [f for f in os.listdir(pasta_servicos) if f.endswith('.txt')]

    # Lista para armazenar as pontuações extraídas
    todas_pontuacoes = []

    # Iteração sobre os arquivos .txt e envio para avaliação
    for i, arquivo in enumerate(arquivos_txt):
        # Se num_arquivos_para_processar for diferente de None e o número de iterações atingir o limite, pare
        if num_arquivos_para_processar is not None and i >= num_arquivos_para_processar:
            break

        arquivo_path = os.path.join(pasta_servicos, arquivo)
        html_resultado = enviar_arquivo_para_avaliacao(arquivo_path, url_avaliacao)
        
        if html_resultado:
            # Extrair as pontuações da resposta HTML
            pontuacoes = extrair_pontuacoes(html_resultado)
            if pontuacoes:
                todas_pontuacoes.extend(pontuacoes)

    # Salvar as pontuações em um arquivo Excel
    if todas_pontuacoes:
        salvar_pontuacoes_em_excel(todas_pontuacoes)
        # Mostrar todas as pontuações extraídas
        for pontuacao in todas_pontuacoes:
            print(pontuacao)

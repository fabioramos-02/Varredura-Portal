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

def configurar_driver():
    """
    Configura e retorna uma instância do driver Chrome otimizado.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar sem abrir a janela do navegador
    chrome_options.add_argument("--disable-gpu")  # Desabilitar GPU para reduzir uso de recursos
    
    # Instala e configura o driver automaticamente
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

from selenium.common.exceptions import StaleElementReferenceException
import time

def enviar_arquivo_para_avaliacao(arquivo_txt, url, driver):
    """
    Envia um arquivo para avaliação e retorna as pontuações encontradas.
    """
    try:
        driver.get(url)
        print(f"Acessando o site de avaliação: {url}")

        # Esperar o formulário ser carregado
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'files')))

        # Repetir a interação com o elemento se o erro ocorrer
        retries = 3  # Número de tentativas
        for _ in range(retries):
            try:
                # Enviar o arquivo
                input_arquivo = driver.find_element(By.NAME, 'files')
                arquivo_absoluto = os.path.abspath(arquivo_txt)
                input_arquivo.send_keys(arquivo_absoluto)

                # Enviar o arquivo
                botao_enviar = driver.find_element(By.ID, 'EnviarFiles')
                botao_enviar.click()

                # Esperar o resultado
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'alerta')))
                print(f"Arquivo {arquivo_txt} enviado com sucesso!")
                break  # Se a interação foi bem-sucedida, saia do loop de tentativas
            except StaleElementReferenceException:
                print("Elemento não encontrado, tentando novamente...")
                time.sleep(2)  # Espera um pouco antes de tentar novamente

        # Extrair pontuações
        html = driver.page_source
        return extrair_pontuacoes(html)

    except Exception as e:
        print(f"Erro ao enviar o arquivo {arquivo_txt}: {e}")
        return []

        
def extrair_pontuacoes(html_resultado):
    """
    Extrai pontuações da página HTML.
    """
    soup = BeautifulSoup(html_resultado, 'html.parser')
    tabela = soup.find('table', class_='TabelaNotas')
    pontuacoes = []
    if tabela:
        for row in tabela.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) == 13:
                nome_arquivo = cols[0].text.strip()
                notas = [col.text.strip() for col in cols[1:]]
                pontuacoes.append([nome_arquivo] + notas)
    return pontuacoes

def salvar_pontuacoes_em_excel(pontuacoes, output_file='pontuacoes_servicos.xlsx'):
    """
    Salva as pontuações em um arquivo Excel.
    """
    if pontuacoes:
        colunas = [
            "Nome do Arquivo", "Nota 2.1", "Nota 2.2", "Nota 2.3", "Nota 2.4", "Nota 2.5", "Nota 2.6", "Nota 2.7", 
            "Nota 2.2 - Começa com verbo", "Nota 2.2 - Está entre 3 a 5 palavras", "Nota 2.2 - Verbo no infinitivo", 
            "Nota 2.3 - Acima de 10 palavras", "Nota 2.3 - Frases com duas ações"
        ]
        
        # Criar um DataFrame onde cada linha corresponde a uma pontuação extraída
        df = pd.DataFrame(pontuacoes, columns=colunas)
        
        # Salvar em um arquivo Excel, com as pontuações em linhas separadas
        df.to_excel(output_file, index=False)
        print(f"Pontuações salvas em {output_file}")
    else:
        print("Nenhuma pontuação para salvar.")


def processar_arquivo(arquivo, url_avaliacao, driver):
    """
    Função para processar um arquivo individual, enviando para avaliação e extraindo pontuações.
    """
    arquivo_path = os.path.join('Servicos', arquivo)
    pontuacoes = enviar_arquivo_para_avaliacao(arquivo_path, url_avaliacao, driver)
    return pontuacoes

if __name__ == '__main__':
    url_avaliacao = "https://linguagem-simples.ligo.go.gov.br/avaliararquivos"
    pasta_servicos = 'Servicos'
    arquivos_txt = [f for f in os.listdir(pasta_servicos) if f.endswith('.txt')]

    # Definir o número de arquivos a serem processados
    num_arquivos_para_processar = None  # Altere para o número desejado ou None para processar todos

    # Limitar o número de arquivos a serem processados
    if num_arquivos_para_processar is not None:
        arquivos_txt = arquivos_txt[:num_arquivos_para_processar]

    todas_pontuacoes = []
    
    # Configura o driver fora da thread
    driver = configurar_driver()

    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            resultados = executor.map(lambda arquivo: processar_arquivo(arquivo, url_avaliacao, driver), arquivos_txt)
            for resultado in resultados:
                if resultado:
                    todas_pontuacoes.extend(resultado)

    finally:
        driver.quit()  # Certifique-se de fechar o driver ao final

    if todas_pontuacoes:
        salvar_pontuacoes_em_excel(todas_pontuacoes)
        for pontuacao in todas_pontuacoes:
            print(pontuacao)

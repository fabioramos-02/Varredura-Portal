from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def obter_info_servico_com_selenium(url, nome_servico):
    """
    Usa o Selenium para acessar a página e obter a descrição do serviço.
    """
    print(f"Buscando o serviço: {nome_servico} na URL: {url}")
    
    # Configuração do Selenium para usar o Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Para rodar sem abrir a janela do navegador
    chrome_options.add_argument("--disable-gpu")  # Opcional para evitar problemas com gráficos

    # Usar o ChromeDriverManager para garantir que o driver seja instalado automaticamente
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Acessar a página
        driver.get(url)
        

        # Obter o HTML completo da página
        html = driver.page_source
      
        # Agora você pode usar o BeautifulSoup para extrair os dados do HTML carregado
        soup = BeautifulSoup(html, 'html.parser')
        
        # Procurar a descrição do serviço dividida nas seções
        descricao_parts = []
        sections = ['oquee', 'exigencias', 'quempodeutilizar', 'prazo', 'custos', 'etapas', 'outrasinformacoes']
        for section_id in sections:
            section_tag = soup.find('section', id=section_id)
            if section_tag:
                h4_tag = section_tag.find('h4')
                p_tags = section_tag.find_all('p')
                section_text = " ".join([p.text.strip() for p in p_tags if p.text.strip()])
                descricao_parts.append(f"{h4_tag.text.strip() if h4_tag else section_id.capitalize()}\n{section_text}\n")
            else:
                print(f"A seção {section_id} não foi encontrada na página.")
        
        # Juntar todas as partes para formar a descrição completa
        sobre_servico = "\n".join(descricao_parts)
        
        # Verificar se algum conteúdo foi encontrado
        if not sobre_servico:
            print(f"Nenhum conteúdo extraído para o serviço: {nome_servico}")
            sobre_servico = "Conteúdo não encontrado"

        return nome_servico, sobre_servico
    
    finally:
        driver.quit()  # Fechar o navegador

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from carregar import salvar_planilha_com_problemas
import traceback

def obter_info_servico_com_selenium(url, nome_servico):
    """
    Usa o Selenium para acessar a página e obter a descrição do serviço.
    """
    print(f"Buscando o serviço: {nome_servico} na URL: {url}")
    
    # Configuração do Selenium para usar o Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Para rodar sem abrir a janela do navegador
    chrome_options.add_argument("--disable-gpu")  # Opcional para evitar problemas com gráficos

    # Usando o ChromeDriverManager para garantir que o ChromeDriver correto será baixado
    driver = webdriver.Chrome(options=chrome_options)

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
        visited_sections = set()  # Controlar as seções já processadas
        
        for section_id in sections:
            if section_id not in visited_sections:
                section_tag = soup.find('section', id=section_id)
                if section_tag:
                    h4_tag = section_tag.find('h4')
                    p_tags = section_tag.find_all('p')
                    section_text = " ".join([p.text.strip() for p in p_tags if p.text.strip()])
                    descricao_parts.append(f"{h4_tag.text.strip() if h4_tag else section_id.capitalize()}\n{section_text}\n")
                    visited_sections.add(section_id)
                else:
                    print(f"A seção {section_id} não foi encontrada na página.")
                    salvar_planilha_com_problemas(nome_servico, url, f"Seção {section_id} não encontrada")  # Registra o erro
        
        # Evitar repetição da palavra "Etapas"
        etapas_tag = soup.find('section', id='etapas')
        if etapas_tag and 'etapas' not in visited_sections:
            # Captura o título "Etapas" que está no parágrafo <p> (não deve ser repetido)
            etapas_title = etapas_tag.find('p').text.strip()  # A palavra "Etapas" está no parágrafo <p> no início da seção
            etapas_text = []  # Listar as etapas sem o título repetido
            h5_tags = etapas_tag.find_all('h5')  # Captura as etapas numeradas
            
            for h5_tag in h5_tags:
                etapa_text = h5_tag.text.strip()  # O texto da etapa (1, 2, 3...)
                p_tags = h5_tag.find_next('div').find_all('p')  # Pegando os <p> após cada <h5> para descrever a etapa
                etapa_detalhada = " ".join([p.text.strip() for p in p_tags if p.text.strip()])  # Combina os textos
                etapas_text.append(f"{etapa_text}\n{etapa_detalhada}\n")
            
            if etapas_text:
                # Adiciona "Etapas" uma única vez, seguido pelas etapas detalhadas
                descricao_parts.append(f"{etapas_title}\n{''.join(etapas_text)}")
            visited_sections.add('etapas')
        
        # Capturar a seção "Outras Informações" sem repetir
        outras_informacoes_tag = soup.find('section', id='outrasinformacoes')
        if outras_informacoes_tag and 'outrasinformacoes' not in visited_sections:
            h4_tag = outras_informacoes_tag.find('h4')
            p_tags = outras_informacoes_tag.find_all('p')
            outras_informacoes_text = " ".join([p.text.strip() for p in p_tags if p.text.strip()])
            descricao_parts.append(f"{h4_tag.text.strip() if h4_tag else 'Outras Informações'}\n{outras_informacoes_text}\n")
            visited_sections.add('outrasinformacoes')
        
        # Juntar todas as partes para formar a descrição completa
        sobre_servico = "\n".join(descricao_parts)
        
        # Verificar se algum conteúdo foi encontrado
        if not sobre_servico:
            print(f"Nenhum conteúdo extraído para o serviço: {nome_servico}")
            salvar_planilha_com_problemas(nome_servico, url, "Conteúdo não encontrado")  # Registra o erro
            sobre_servico = "Conteúdo não encontrado"

        return nome_servico, sobre_servico
    
    except Exception as e:
        # Caso ocorra algum erro inesperado
        erro_message = f"Erro inesperado: {str(e)}\n{traceback.format_exc()}"
        print(erro_message)
        salvar_planilha_com_problemas(nome_servico, url, erro_message)  # Registra o erro na planilha
        return nome_servico, "Erro ao processar o serviço"
    
    finally:
        driver.quit()  # Fechar o navegador


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from carregar import salvar_planilha_com_problemas
import traceback

def extrair_oquee(soup):
    """Função específica para extrair a seção 'O que é este serviço' com quebras de linha adequadas"""
    section_tag = soup.find('section', id='oquee')
    if section_tag:
        h4_tag = section_tag.find('h4')
        p_tags = section_tag.find_all('p')

        # Variável para armazenar o texto da seção sem duplicações
        section_text = []

        for p in p_tags:
            # Extrair texto do parágrafo, removendo espaços em branco e links
            text = p.get_text(strip=True)
            if text:
                # Verificar se o parágrafo já foi adicionado (evita repetições)
                if text not in section_text:
                    section_text.append(text)

        # Concatenar os parágrafos com quebras de linha entre eles
        if section_text:
            return f"{h4_tag.text.strip() if h4_tag else 'O que é este serviço'}\n" + "\n".join(section_text) + "\n"
    
    return ""


def extrair_exigencias(soup, visited_sections):
    """Função específica para extrair a seção 'Exigências'"""
    section_tag = soup.find('section', id='exigencias')
    if section_tag and 'exigencias' not in visited_sections:
        h4_tag = section_tag.find('h4')
        p_tags = section_tag.find_all('p')
        
        # Variável para armazenar o texto da seção sem duplicações
        section_text = []
        
        # Para cada parágrafo, verificamos se ele não está vazio
        for p in p_tags:
            text = p.get_text(strip=True)
            
            # Evitar parágrafos duplicados
            if text and text not in section_text:
                section_text.append(text)

        # Concatenar todos os parágrafos filtrados
        if section_text:
            visited_sections.add('exigencias')
            return f"{h4_tag.text.strip() if h4_tag else 'Exigências'}\n" + "\n".join(section_text) + "\n"
    
    return ""


def extrair_quempodeutilizar(soup, visited_sections):
    """Função específica para extrair a seção 'Quem pode utilizar'"""
    section_tag = soup.find('section', id='quempodeutilizar')
    if section_tag and 'quempodeutilizar' not in visited_sections:
        h4_tag = section_tag.find('h4')
        p_tags = section_tag.find_all('p')
        
        # Variável para armazenar o texto da seção sem duplicações
        section_text = []
        
        # Para cada parágrafo, verificamos se ele não está vazio
        for p in p_tags:
            text = p.get_text(strip=True)
            
            # Evitar parágrafos duplicados
            if text and text not in section_text:
                section_text.append(text)

        # Concatenar todos os parágrafos filtrados
        if section_text:
            visited_sections.add('quempodeutilizar')
            return f"{h4_tag.text.strip() if h4_tag else 'Quem pode utilizar'}\n" + "\n".join(section_text) + "\n"

    return ""


def extrair_prazos(soup):
    """Função específica para extrair a seção 'Prazos'"""
    section_tag = soup.find('section', id='prazo')
    if section_tag:
        h4_tag = section_tag.find('h4')
        p_tags = section_tag.find_all('p')
        section_text = " ".join([p.text.strip() for p in p_tags if p.text.strip()])
        return f"{h4_tag.text.strip() if h4_tag else 'Prazos'}\n{section_text}\n"
    return ""

def extrair_custos(soup):
    """Função específica para extrair a seção 'Custos'"""
    section_tag = soup.find('section', id='custos')
    if section_tag:
        h4_tag = section_tag.find('h4')
        p_tags = section_tag.find_all('p')
        section_text = " ".join([p.text.strip() for p in p_tags if p.text.strip()])
        return f"{h4_tag.text.strip() if h4_tag else 'Custos'}\n{section_text}\n"
    return ""

def extrair_etapas(soup, visited_sections):
    """Função específica para extrair a seção 'Etapas' com regras de negócio para evitar repetição"""
    section_tag = soup.find('section', id='etapas')
    if section_tag and 'etapas' not in visited_sections:
        etapas_text = []
        h5_tags = section_tag.find_all('h5')
        
        # Para cada etapa, extraímos o título e as descrições
        for h5_tag in h5_tags:
            etapa_text = h5_tag.text.strip()
            # Encontrar todos os parágrafos dentro do <div> que segue o <h5>
            p_tags = h5_tag.find_next('div').find_all('p')
            
            etapa_detalhada = []
            # Para cada parágrafo, removemos espaços extras e garantimos que não adicionamos duplicados
            for p in p_tags:
                text = p.text.strip()
                # Evitar adicionar texto duplicado
                if text and text not in etapa_detalhada:
                    etapa_detalhada.append(text)
            
            if etapa_detalhada:
                # Juntar o texto da etapa e das descrições detalhadas
                etapas_text.append(f"{etapa_text}\n" + "\n".join(etapa_detalhada) + "\n")
        
        visited_sections.add('etapas')
        return f"Etapas\n{''.join(etapas_text)}"
    
    return ""


def extrair_outrasinformacoes(soup, visited_sections):
    """Função específica para extrair a seção 'Outras Informações'"""
    section_tag = soup.find('section', id='outrasinformacoes')
    if section_tag and 'outrasinformacoes' not in visited_sections:
        h4_tag = section_tag.find('h4')
        p_tags = section_tag.find_all('p')

        # Variável para armazenar o texto da seção sem duplicações
        outras_informacoes_text = []

        # Para cada parágrafo, verificamos se ele não está vazio
        for p in p_tags:
            # Remover tags <a> de dentro de <p> para evitar duplicação de links
            links = p.find_all('a')
            for link in links:
                link.extract()  # Remove o conteúdo da tag <a> para evitar duplicação

            # Extrair o texto do parágrafo e remover espaços em branco
            text = p.get_text(strip=True)

            # Evitar adição de parágrafos duplicados
            if text and text not in outras_informacoes_text:
                outras_informacoes_text.append(text)

        # Concatenar todos os parágrafos filtrados
        if outras_informacoes_text:
            visited_sections.add('outrasinformacoes')
            return f"{h4_tag.text.strip() if h4_tag else 'Outras Informações'}\n" + "\n".join(outras_informacoes_text) + "\n"

    return ""

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
        visited_sections = set()  # Controlar as seções já processadas
        
        # Extração de seções usando funções específicas
        descricao_parts.append(extrair_oquee(soup))
        descricao_parts.append(extrair_exigencias(soup, visited_sections))  # Passando visited_sections
        descricao_parts.append(extrair_quempodeutilizar(soup, visited_sections))  # Passando visited_sections
        descricao_parts.append(extrair_prazos(soup))
        descricao_parts.append(extrair_custos(soup))
        descricao_parts.append(extrair_etapas(soup, visited_sections))  # Passando visited_sections
        descricao_parts.append(extrair_outrasinformacoes(soup, visited_sections))  # Passando visited_sections

        # Verificar se a seção 'Outras Informações' foi encontrada e registrar se não foi
        if not descricao_parts[-1]:
            salvar_planilha_com_problemas(nome_servico, url, "Seção 'Outras Informações' não encontrada")
        
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

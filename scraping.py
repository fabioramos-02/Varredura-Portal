from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from carregar import salvar_planilha_com_problemas
import traceback

def extrair_texto_unico(p_tags):
    """Função genérica para extrair texto sem repetições, com quebras de linha apropriadas e links removidos"""
    seen = set()  # Usar um set para garantir que o texto não se repita
    section_text = []  # Usar uma lista para preservar a ordem dos parágrafos

    for p in p_tags:
        # Remover links e extrair o texto
        for link in p.find_all('a'):
            link.decompose()  # Remove o conteúdo da tag <a> completamente

        text = p.get_text(strip=True)
        if text and text not in seen:
            section_text.append(text)  # Adicionar o texto ao resultado
            seen.add(text)  # Marcar o texto como já visto
    
    return "\n".join(section_text)

def extrair_oquee(soup):
    """Função específica para extrair a seção 'O que é este serviço' com quebras de linha apropriadas"""
    section_tag = soup.find('section', id='oquee')
    if section_tag:
        h4_tag = section_tag.find('h4')
        p_tags = section_tag.find_all('p')
        section_text = extrair_texto_unico(p_tags)
        if section_text:
            return f"{h4_tag.text.strip() if h4_tag else 'O que é este serviço'}\n{section_text}\n"
    return ""

def extrair_exigencias(soup, visited_sections):
    """Função específica para extrair a seção 'Exigências'"""
    section_tag = soup.find('section', id='exigencias')
    if section_tag and 'exigencias' not in visited_sections:
        h4_tag = section_tag.find('h4')
        p_tags = section_tag.find_all('p')
        section_text = extrair_texto_unico(p_tags)
        if section_text:
            visited_sections.add('exigencias')
            return f"{h4_tag.text.strip() if h4_tag else 'Exigências'}\n{section_text}\n"
    return ""

def extrair_quempodeutilizar(soup, visited_sections):
    """Função específica para extrair a seção 'Quem pode utilizar'"""
    section_tag = soup.find('section', id='quempodeutilizar')
    if section_tag and 'quempodeutilizar' not in visited_sections:
        h4_tag = section_tag.find('h4')
        p_tags = section_tag.find_all('p')
        section_text = extrair_texto_unico(p_tags)
        if section_text:
            visited_sections.add('quempodeutilizar')
            return f"{h4_tag.text.strip() if h4_tag else 'Quem pode utilizar'}\n{section_text}\n"
    return ""

def extrair_prazos(soup):
    """Função específica para extrair a seção 'Prazos'"""
    section_tag = soup.find('section', id='prazo')
    if section_tag:
        h4_tag = section_tag.find('h4')
        p_tags = section_tag.find_all('p')
        section_text = extrair_texto_unico(p_tags)
        return f"{h4_tag.text.strip() if h4_tag else 'Prazos'}\n{section_text}\n"
    return ""

def extrair_custos(soup):
    """Função específica para extrair a seção 'Custos'"""
    section_tag = soup.find('section', id='custos')
    if section_tag:
        h4_tag = section_tag.find('h4')
        p_tags = section_tag.find_all('p')
        section_text = extrair_texto_unico(p_tags)
        return f"{h4_tag.text.strip() if h4_tag else 'Custos'}\n{section_text}\n"
    return ""

def extrair_etapas(soup, visited_sections):
    """Função específica para extrair a seção 'Etapas' com regras de negócio para evitar repetição"""
    section_tag = soup.find('section', id='etapas')
    if section_tag and 'etapas' not in visited_sections:
        etapas_text = []
        h5_tags = section_tag.find_all('h5')

        for h5_tag in h5_tags:
            etapa_text = h5_tag.text.strip()  # Título da etapa
            p_tags = h5_tag.find_next('div').find_all('p')

            etapa_detalhada = []  # Armazenar as descrições detalhadas

            for p in p_tags:
                # Extrair o texto e evitar textos vazios
                text = p.get_text(strip=True)
                if text:
                    etapa_detalhada.append(text)

            # Adicionar a etapa com detalhes
            if etapa_detalhada:
                etapas_text.append(f"{etapa_text}\n{''.join(etapa_detalhada)}")

        visited_sections.add('etapas')
        # Agora, vamos garantir que as etapas sejam separadas por quebras de linha corretamente
        return f"Etapas\n\n{' \n\n'.join(etapas_text)}"  # Adicionando '\n\n' entre as etapas para separá-las claramente
    return ""

def extrair_outrasinformacoes(soup, visited_sections):
    """Função específica para extrair a seção 'Outras Informações'"""
    section_tag = soup.find('section', id='outrasinformacoes')
    if section_tag and 'outrasinformacoes' not in visited_sections:
        h4_tag = section_tag.find('h4')
        p_tags = section_tag.find_all('p')

        # Remover links dentro de parágrafos para evitar duplicação
        for p in p_tags:
            for link in p.find_all('a'):
                link.decompose()  # Remove os links completamente

        section_text = extrair_texto_unico(p_tags)
        if section_text:
            visited_sections.add('outrasinformacoes')
            return f"{h4_tag.text.strip() if h4_tag else 'Outras Informações'}\n{section_text}\n"
    return ""

def obter_info_servico_com_selenium(url, nome_servico):
    """
    Usa o Selenium para acessar a página e obter a descrição do serviço.
    """
    print(f"Buscando o serviço: {nome_servico} na URL: {url}")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Para rodar sem abrir a janela do navegador
    chrome_options.add_argument("--disable-gpu")  # Opcional para evitar problemas com gráficos

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

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

        # Verificar se as seções foram encontradas e registrar se não foram
        secoes = ['O que é este serviço', 'Exigências', 'Quem pode utilizar', 'Prazos', 'Custos', 'Etapas', 'Outras Informações']
        for i, secao in enumerate(secoes):
            if not descricao_parts[i]:
                salvar_planilha_com_problemas(nome_servico, url, f"Seção '{secao}' não encontrada")

        # Juntar todas as partes para formar a descrição completa
        sobre_servico = "\n".join(descricao_parts)  # Adicionando uma linha em branco entre as seções

        # Verificar se algum conteúdo foi encontrado
        if not sobre_servico:
            print(f"Nenhum conteúdo extraído para o serviço: {nome_servico}")
            salvar_planilha_com_problemas(nome_servico, url, "Conteúdo não encontrado")  # Registra o erro
            sobre_servico = "Conteúdo não encontrado"

        return nome_servico, sobre_servico

    except Exception as e:
        erro_message = f"Erro inesperado: {str(e)}\n{traceback.format_exc()}"
        print(erro_message)
        salvar_planilha_com_problemas(nome_servico, url, erro_message)  # Registra o erro na planilha
        return nome_servico, "Erro ao processar o serviço"

    finally:
        driver.quit()  # Fechar o navegador

import os
import pandas as pd
import unicodedata
import re

# Função para remover as tags < e > do texto
def remover_tags_etapa(etapa_texto):
    """
    Remove qualquer conteúdo entre as tags < e > e retorna o texto limpo.
    """
    # Expressão regular para capturar o conteúdo entre < e >
    etapa_texto = re.sub(r'<.*?>', '', etapa_texto)  # Remove qualquer tag
    return etapa_texto.strip()

# Função para gerar o texto conforme o formato esperado
def gerar_texto_servico(row):
    texto = f"{row['titulo']}\n\n"
    texto += f"O que é este serviço?\n{row['descricao']}\n\n"
    texto += f"Exigências para realizar o serviço\n{row['requisitos']}\n\n"
    texto += f"Quem pode utilizar este serviço?\n{row['publico']}\n\n"
    
    # Verificar se há etapas e removê-las corretamente
    if pd.isna(row['etapa']) or row['etapa'].strip() == "":
        texto += "Etapas\n\n"
    else:
        texto += f"Etapas\n {remover_tags_etapa(row['etapa'])}\n\n"
    
    if int(row['tempo_total']) == 0:
        texto += f"Prazos\n{row['tipo_tempo']} \n\n"
    else:
        texto += f"Prazos\n{int(row['tempo_total'])} {row['tipo_tempo']} \n\n"
    texto += f"Quais os custos?\n{row['custo']}\n\n"
    texto += f"Outras informações\n{row['informacoes_extra']}\n\n"
    texto += f"Link para o serviço: {row['endereco']}"
    return texto

# Função para limpar caracteres indesejados do texto
def limpar_texto(texto):
    """
    Limpa caracteres indesejados do texto.
    """
    return texto.replace('_x000D_', '').replace('\xa0', ' ').replace('_x0009_', '').strip()

# Função para limpar e normalizar os nomes dos arquivos
def limpar_nome_arquivo(nome_arquivo, limite_tamanho=100):
    """
    Limpa caracteres inválidos de nomes de arquivos e normaliza caracteres especiais.
    """
    nome_arquivo = unicodedata.normalize('NFKD', nome_arquivo).encode('ASCII', 'ignore').decode('ASCII')
    caracteres_invalidos = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '(', ')', '{', '}', '[', ']', ',', ';', '.', '#', '+', '=', '@']
    
    for char in caracteres_invalidos:
        nome_arquivo = nome_arquivo.replace(char, ' ')
    
    nome_arquivo = re.sub(r'\s+', ' ', nome_arquivo).strip()
    nome_arquivo = nome_arquivo.replace(" ", "_")
    
    if len(nome_arquivo) > limite_tamanho:
        nome_arquivo = nome_arquivo[:limite_tamanho]
    
    return nome_arquivo

# Função para salvar o arquivo com sufixo numérico em caso de conflito
def salvar_arquivo_servico(nome_servico, texto):
    """
    Salva o texto gerado para o serviço em um arquivo .txt com sufixo numérico se necessário.
    """
    pasta_servicos = 'Servicos'
    if not os.path.exists(pasta_servicos):
        os.makedirs(pasta_servicos)

    # Limpar e normalizar o nome do arquivo
    nome_servico_limpo = limpar_nome_arquivo(nome_servico)

    # Verificar se já existe um arquivo com o nome limpo
    caminho_arquivo = os.path.join(pasta_servicos, f"{nome_servico_limpo}.txt")
    
    if os.path.exists(caminho_arquivo):
        # Se o arquivo já existir, adicionar um sufixo numérico
        contador = 1
        while os.path.exists(caminho_arquivo):
            caminho_arquivo = os.path.join(pasta_servicos, f"{nome_servico_limpo}_{contador}.txt")
            contador += 1

    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as file:
            file.write(texto)
        return True, None  # Sucesso
    except Exception as e:
        return False, str(e)  # Falha com o erro
# Função para processar os serviços de forma paralela
def processar_servico(row):
    try:
        texto_servico = gerar_texto_servico(row)
        texto_limpo = limpar_texto(texto_servico)
        nome_servico = row['titulo']
        
        sucesso, erro = salvar_arquivo_servico(nome_servico, texto_limpo)
        
        if not sucesso:
            print(f"Erro ao salvar o serviço: {nome_servico}. Erro: {erro}")
            return nome_servico, False, erro  # Falhou
        return nome_servico, True, None  # Sucesso
    except Exception as e:
        print(f"Erro geral no serviço: {row['titulo']}. Erro: {str(e)}")
        return row['titulo'], False, str(e)  # Captura exceções gerais e retorna o erro

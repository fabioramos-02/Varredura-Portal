import os
import pandas as pd
import unicodedata
from carregar import carregar_planilha



# Função para normalizar e limpar o título do serviço
def limpar_nome_arquivo(nome_arquivo):
    """
    Limpa e normaliza o nome do arquivo para comparação.
    """
    # Normaliza os caracteres especiais para seus equivalentes ASCII
    nome_arquivo = unicodedata.normalize('NFKD', nome_arquivo).encode('ASCII', 'ignore').decode('ASCII')

    # Substitui os espaços por underscores
    nome_arquivo = nome_arquivo.replace(' ', '_')

    # Retorna o nome do arquivo limpo
    return nome_arquivo

# Função para comparar os nomes dos arquivos gerados com os títulos na planilha
def comparar_arquivos_e_planilha(caminho_arquivo_planilha, pasta_servicos):
    # Carregar dados da planilha
    planilha = carregar_planilha(caminho_arquivo_planilha)
    
    # Listar todos os arquivos .txt gerados na pasta 'Servicos'
    arquivos_gerados = [f.replace('.txt', '') for f in os.listdir(pasta_servicos) if f.endswith('.txt')]
    
    # Normalizar os arquivos gerados
    arquivos_gerados = [limpar_nome_arquivo(f) for f in arquivos_gerados]
    
    # Verificar quais serviços não geraram arquivos
    faltando_arquivos = []

    # Verificar cada título da planilha
    for index, row in planilha.iterrows():
        titulo_servico = row['titulo']
        
        # Limpar o título do serviço da planilha para comparação
        titulo_servico_limpo = limpar_nome_arquivo(titulo_servico)

        # Comparar o nome do serviço com os arquivos gerados
        if titulo_servico_limpo not in arquivos_gerados:
            faltando_arquivos.append({
                'titulo': titulo_servico,
                'erro': f"Arquivo não gerado: {titulo_servico_limpo}.txt"
            })
    
    # Gerar o relatório de faltando arquivos
    if faltando_arquivos:
        faltando_df = pd.DataFrame(faltando_arquivos)
        if not os.path.exists('Planilhas'):
            os.makedirs('Planilhas')
        faltando_df.to_excel(os.path.join('Planilhas', 'faltando_arquivos.xlsx'), index=False)
        faltando_df.to_excel('faltando_arquivos.xlsx', index=False)
        print(f"{len(faltando_arquivos)} arquivos não foram gerados. Relatório gerado em 'faltando_arquivos.xlsx'.")
    else:
        print("Todos os arquivos foram gerados corretamente.")
    
# Caminho para a planilha e pasta de arquivos gerados
caminho_arquivo_planilha = "Planilhas/servicos.xlsx"  # Alterar para o caminho correto da planilha
pasta_servicos = 'Servicos'  # Caminho da pasta onde os arquivos .txt são gerados

# Comparar os arquivos gerados com os dados da planilha
comparar_arquivos_e_planilha(caminho_arquivo_planilha, pasta_servicos)

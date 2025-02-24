import os

def salvar_arquivo(nome_servico, sobre_servico, pasta_destino='Servicos'):
    """
    Cria ou substitui um arquivo .txt com o nome do serviço e descrição.
    """
    # Sanitizar o nome do serviço para ser usado no nome do arquivo
    nome_arquivo = f"{nome_servico}.txt".replace("/", "_").replace(" ", "_").replace(":", "_")
    
    # Garantir que a pasta destino exista
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    
    # Caminho completo para salvar o arquivo
    caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)
    
    try:
        # Substituir o arquivo existente, se houver
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(f"{nome_servico}\n{sobre_servico}\n")
        print(f"Arquivo {nome_arquivo} substituído com sucesso em {pasta_destino}!")
    except Exception as e:
        print(f"Erro ao substituir o arquivo {nome_arquivo}: {e}")

import pandas as pd
import os
def carregar_planilha(caminho_arquivo):
    """
    Carrega a planilha do Excel e retorna as URLs e títulos de forma estruturada.
    """
    # Carregar o arquivo Excel
    df = pd.read_excel(caminho_arquivo)

    # Certificar-se de que as colunas estão presentes e retornar como lista de dicionários
    if 'titulo' in df.columns and 'endereco' in df.columns:
        return df[['titulo', 'endereco']].to_dict(orient='records')
    else:
        print("As colunas 'titulo' e 'endereco' não foram encontradas na planilha.")
        return []


def salvar_planilha_com_problemas(nome_servico, url, erro_message):
    # Carregar o DataFrame existente ou criar um novo
    try:
        df = pd.read_excel('problemas.xlsx')
    except FileNotFoundError:
        # Se o arquivo não existir, criar um novo DataFrame
        df = pd.DataFrame(columns=["Nome do Serviço", "URL", "Erro"])

    # Adicionar o novo erro
    problema = {"Nome do Serviço": nome_servico, "URL": url, "Erro": erro_message}
    
    # Usar _append() para adicionar o problema
    df = df._append(problema, ignore_index=True)

    # Salvar novamente no Excel
    df.to_excel('problemas.xlsx', index=False)
import pandas as pd

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

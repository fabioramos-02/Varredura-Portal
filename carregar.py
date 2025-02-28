import pandas as pd

# Função para carregar a planilha
def carregar_planilha(caminho_arquivo):
    """
    Carrega a planilha do Excel e retorna os dados de forma estruturada.
    """
    df = pd.read_excel(caminho_arquivo)

    # Verificar se as colunas necessárias existem
    colunas_esperadas = ['titulo', 'descricao', 'requisitos', 'publico', 'tempo_total', 'tipo_tempo', 'custo', 'etapa', 'informacoes_extra', 'endereco']
    
    # print("Colunas encontradas na planilha:", df.columns.tolist())

    if all(col in df.columns for col in colunas_esperadas):
        return df
    else:
        missing_cols = [col for col in colunas_esperadas if col not in df.columns]
        raise ValueError(f"Colunas ausentes na planilha: {', '.join(missing_cols)}")

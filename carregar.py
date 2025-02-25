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

def salvar_planilha_com_problemas(nome_servico, url_servico, erro, arquivo_saida='servicos_com_problemas.xlsx'):
    """
    Salva os serviços com problemas em uma planilha Excel.
    """
    problema = {
        'Nome do Serviço': nome_servico,
        'URL': url_servico,
        'Erro': erro
    }

    # Verifica se o arquivo já existe, se não, cria um novo
    if os.path.exists(arquivo_saida):
        df = pd.read_excel(arquivo_saida)
        df = df.append(problema, ignore_index=True)
    else:
        df = pd.DataFrame([problema])

    df.to_excel(arquivo_saida, index=False)
    print(f"Planilha atualizada com erro em {nome_servico}.")

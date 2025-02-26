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



def salvar_planilha_com_problemas(nome_servico, url_servico, erro):
    global planilha_problemas
    
    # Inicialize a variável planilha_problemas se ela não estiver definida
    if 'planilha_problemas' not in globals():
        planilha_problemas = pd.DataFrame(columns=['Título', 'URL', 'Erro'])
    
    # Adiciona o erro à planilha
    novo_registro = pd.DataFrame([[nome_servico, url_servico, erro]], columns=['Título', 'URL', 'Erro'])
    planilha_problemas = pd.concat([planilha_problemas, novo_registro], ignore_index=True)
    
    # Salva novamente no arquivo Excel
    planilha_problemas.to_excel('problemas.xlsx', index=False)
    print(f"Erro registrado para o serviço {nome_servico}: {erro}")


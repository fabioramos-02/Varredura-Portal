from carregar import carregar_planilha
from concurrent.futures import ThreadPoolExecutor
from gerar_txt import processar_servico
import pandas as pd

# Função para orquestrar o processamento de todos os serviços
def orquestrar_processamento_servicos(caminho_arquivo):
    """
    Orquestra o processamento de todos os serviços.
    """
    print("Carregando dados da planilha...")
    planilha = carregar_planilha(caminho_arquivo)

    falhas = []
    total_processados = 0
    total_falhas = 0

    # Usando paralelização para processar os serviços
    with ThreadPoolExecutor() as executor:
        resultados = executor.map(processar_servico, [row for _, row in planilha.iterrows()])

        # Coletando os resultados de falhas
        for nome_servico, sucesso, erro in resultados:
            if not sucesso:
                falhas.append({'titulo': nome_servico, 'erro': erro})
                total_falhas += 1
            total_processados += 1

    # Gerar o arquivo de falhas
    if falhas:
        falhas_df = pd.DataFrame(falhas)
        falhas_df.to_excel('falhas.xlsx', index=False)
        print(f"{total_falhas} serviços falharam e foram registrados em 'falhas.xlsx'.")
    else:
        print("Todos os serviços foram processados com sucesso!")

    # Relatório de quantos arquivos foram processados com sucesso e os que falharam
    print(f"Total de serviços processados: {total_processados}")
    print(f"Total de serviços gerados com sucesso: {total_processados - total_falhas}")
    print(f"Total de falhas: {total_falhas}")

# Executando a orquestração
if __name__ == "__main__":
    caminho_arquivo = "servicos.xlsx"  # Caminho para o arquivo da planilha
    orquestrar_processamento_servicos(caminho_arquivo)

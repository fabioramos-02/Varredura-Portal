from concurrent.futures import ThreadPoolExecutor
from carregar import carregar_planilha, salvar_planilha_com_problemas
from scraping import obter_info_servico_com_selenium
from gerar_txt import salvar_arquivo
import os

# Definir o número de serviços a serem processados (use None para processar todos)
num_servicos_para_processar = 3  # Ajuste este valor para 3 ou outro número, ou use None para processar todos

# Carregar os links dos serviços e os títulos da planilha
links = carregar_planilha("servicos.xlsx")

# Função para processar um serviço
def processar_servico(link):
    nome_servico = link['titulo']  # Nome do serviço na coluna 'titulo'
    url_servico = link['endereco']  # URL do serviço na coluna 'endereco'

    print(f"Processando serviço: {nome_servico} - URL: {url_servico}")

    try:
        # Obter a descrição do serviço usando o nome da planilha
        nome_servico, sobre_servico = obter_info_servico_com_selenium(url_servico, nome_servico)

        # Salvar arquivo na pasta 'Servicos'
        pasta_servicos = 'Servicos'
        salvar_arquivo(nome_servico, sobre_servico, pasta_destino=pasta_servicos)

    except Exception as e:
        print(f"Erro ao processar o serviço {nome_servico}: {e}")
        # Se houver erro, salvamos as informações na planilha
        salvar_planilha_com_problemas(nome_servico, url_servico, str(e))

# Usar ThreadPoolExecutor para paralelizar a execução dos serviços
with ThreadPoolExecutor() as executor:
    # Se num_servicos_para_processar não for None, limitar a quantidade de serviços processados
    if num_servicos_para_processar is not None:
        links = links[:num_servicos_para_processar]
    
    # Executar a função de processamento em paralelo para todos os serviços
    executor.map(processar_servico, links)

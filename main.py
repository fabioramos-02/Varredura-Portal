from carregar import carregar_planilha
from scraping import obter_info_servico_com_selenium
from gerar_txt import salvar_arquivo
import os

# Definir o número de serviços a serem processados (use None para processar todos)
num_servicos_para_processar = None  # Ajuste este valor para 3 ou outro número, ou use None para processar todos

# Carregar os links dos serviços e os títulos da planilha
links = carregar_planilha("servicos.xlsx")



# Iteração sobre os links e extração dos serviços
for i, link in enumerate(links):
    # Se num_servicos_para_processar for diferente de None e o número de iterações atingir o limite, pare
    if num_servicos_para_processar is not None and i >= num_servicos_para_processar:
        break

    nome_servico = link['titulo']  # Nome do serviço na coluna 'titulo'
    url_servico = link['endereco']  # URL do serviço na coluna 'endereco'

    # Verificar se a URL está correta antes de processar
    if not url_servico.startswith(('http://', 'https://')):
        print(f"URL inválida para o serviço {nome_servico}: {url_servico}")
        continue

    print(f"Processando serviço: {nome_servico} - URL: {url_servico}")
    
    # Obter a descrição do serviço usando o nome da planilha
    nome_servico, sobre_servico = obter_info_servico_com_selenium(url_servico, nome_servico)
    
    # Salvar arquivo na pasta 'Servicos'
    pasta_servicos = 'Servicos'
    salvar_arquivo(nome_servico, sobre_servico, pasta_destino=pasta_servicos)

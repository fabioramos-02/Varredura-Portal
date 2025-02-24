import os
import pandas as pd
from carregar import carregar_planilha
from scraping import obter_info_servico_com_selenium
from gerar_txt import salvar_arquivo
from concurrent.futures import ThreadPoolExecutor

def verificar_servico(link):
    """
    Verifica se o serviço gerou o arquivo .txt corretamente ou se está com dados incompletos.
    Retorna o serviço e o problema encontrado, caso exista.
    """
    nome_servico = link['titulo']  # Nome do serviço na coluna 'titulo'
    url_servico = link['endereco']  # URL do serviço na coluna 'endereco'

    # Obter a descrição do serviço usando o nome da planilha
    nome_servico, sobre_servico = obter_info_servico_com_selenium(url_servico, nome_servico)

    # Verificar se o arquivo foi gerado corretamente ou se está faltando algo
    if sobre_servico == "Conteúdo não encontrado":
        return {
            'Nome do Serviço': nome_servico,
            'URL': url_servico,
            'O que está faltando': 'Conteúdo não encontrado'
        }
    elif 'O que é este serviço?' not in sobre_servico:
        return {
            'Nome do Serviço': nome_servico,
            'URL': url_servico,
            'O que está faltando': 'Seção "O que é este serviço?" ausente'
        }
    else:
        # Salvar arquivo caso o conteúdo esteja completo
        pasta_servicos = 'Servicos'
        salvar_arquivo(nome_servico, sobre_servico, pasta_destino=pasta_servicos)
        return None

def verificar_servicos(links):
    """
    Verifica os serviços com problemas utilizando paralelismo para aumentar a eficiência.
    """
    # Lista para armazenar os serviços com problemas
    servicos_com_problemas = []

    # Usar ThreadPoolExecutor para paralelizar o processamento
    with ThreadPoolExecutor() as executor:
        resultados = executor.map(verificar_servico, links)

        for resultado in resultados:
            if resultado:
                servicos_com_problemas.append(resultado)

    return servicos_com_problemas

def salvar_servicos_com_problemas(servicos_com_problemas, arquivo_saida='servicos_com_problemas.xlsx'):
    """
    Salva os serviços com problemas em uma planilha Excel.
    """
    if servicos_com_problemas:
        df = pd.DataFrame(servicos_com_problemas)
        df.to_excel(arquivo_saida, index=False)
        print(f"Planilha gerada com sucesso em {arquivo_saida}")
    else:
        print("Nenhum serviço com problema encontrado.")

if __name__ == '__main__':
    # Carregar os links dos serviços e os títulos da planilha
    links = carregar_planilha("servicos.xlsx")

    # Verificar serviços que não geraram o arquivo ou com dados incompletos
    servicos_com_problemas = verificar_servicos(links)

    # Salvar os serviços com problemas em uma planilha Excel
    salvar_servicos_com_problemas(servicos_com_problemas)

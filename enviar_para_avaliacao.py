# Fluxo do codigo

"""
Fluxo do código
Processamento em Lotes de Arquivos (Batch Processing):

Divida os arquivos TXT em lotes de 8 por vez (o número de arquivos pode ser configurado).
Acessar o Site de Avaliação:

Acesse a URL https://linguagem-simples.ligo.go.gov.br/avaliararquivos.
Envio de Arquivos:

Faça o upload de cada lote de arquivos TXT.
Após o upload, clique em "Enviar para avaliação" para submeter os arquivos.
Aguarde o Processo de Avaliação:

Espere o tempo necessário até que o sistema retorne os resultados da avaliação.
Adote uma estratégia de timeout otimizada com retries para lidar com sites lentos ou indisponíveis temporariamente.
Captura dos Resultados:

Após a conclusão da avaliação, capture a tabela de resultados da página.
Salvamento e Mesclagem de Resultados:

Salve os resultados em um arquivo Excel chamado resultado_avaliacao.xlsx.
Mescle os resultados com os dados presentes na planilha servicos.xlsx, associando o nome do arquivo às suas respectivas notas.
Tratamento de Falhas:

Caso algum arquivo falhe durante o processo (por exemplo, não conseguir realizar o upload ou o arquivo não for avaliado corretamente), registre o nome do arquivo e o motivo da falha em uma planilha separada chamada falhas.xlsx.
Repetir o Processo:

Continue enviando os lotes de arquivos até que todos tenham sido avaliados.
O número de arquivos por vez pode ser ajustado conforme necessário.
Eficiência:
Otimização do tempo de espera: Utilize espera explícita para garantir que a avaliação seja concluída antes de seguir para a próxima etapa.
Evitar sobrecarga de recursos: Abra o driver uma única vez e use a mesma sessão para enviar múltiplos lotes de arquivos, minimizando o overhead.
Falhas e retry: Implemente lógica para lidar com falhas, como tentativas automáticas de reenvio e registro das falhas com informações detalhadas.
Desempenho com Excel: Caso o número de arquivos seja grande, considere usar uma base de dados em vez de trabalhar com arquivos Excel, caso o tempo de processamento aumente significativamente.
"""
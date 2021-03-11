import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from bs4 import BeautifulSoup
import requests
from datetime import date, datetime, timedelta
import re

# O link n'onde os dados podem ser obtidos
link = 'http://www.rondonopolis.mt.gov.br/covid-19/boletins/'

# Obtendo as datas relevantes e as convertendo para o formato adequado 
hoje = date.today()
data_final = hoje
ontem = hoje - timedelta(days=1)

# Formatando o link dos boletins
if datetime.now().hour > 19:
    link = link + 'boletim-epidemiologico-' + str(data_final.strftime('%d-%m-%y')) + '/'
else: link = link + 'boletim-epidemiologico-' + str(ontem.strftime('%d-%m-%y')) + '/'; data_final = ontem

# Requisitando acesso ao site
req = requests.get(link)

if req.status_code != 200:
    status_code = req.status_code
    print(f"Erro {status_code} ao requisitar o arquivo HTML")

# Parsing do DOM
sopa = BeautifulSoup(req.content, 'html.parser')

# No site, o script desejado é a décima tag <script> do DOM
conteudo = str(sopa.find_all('script')[11])

# Padrão dos dados na tag <script> que seguem a forma 'data: [n, m, k, ...]'
padrao = re.compile(r'data: \[.+\]')

# Encontrando a ocorrência dos padrões
dados = padrao.findall(conteudo)

# O range de datas
data_final = data_final.strftime('%Y%m%d')
datas = pd.date_range(start = "20200514", end = data_final, freq = "D")

# Finalmente, os dados através de list comprehensions
# O formato usado separa os dados encontrandos em ',' e mapeia cada entrada da lista separada a um inteiro
# Os índices 0 a 2 e 7 a (len(dados)-2) simplesmente ignora as entradas desnecessárias dos dados encontrados ('data:', '[' e ']')
casosTotais = [int(s) for s in dados[0][7:len(dados[0])-1].split(',')]
casosRec = [int(s) for s in dados[1][7:len(dados[1])-1].split(',')]
obitos = [int(s) for s in dados[2][7:len(dados[2])-1].split(',')]

# A função a seguir faz subtração entre arrays do mesmo tamanho
def util(listA, listB):

    listaSubtraida = list()

    if len(listA) != len(listB):
        print("Tamanho incompatível")
    i = 0
    while i < len(listA):
        listaSubtraida.append(listA[i] - listB[i])
        i += 1
    return listaSubtraida

# Para calcular o número de casos ativos de um período t, é necessário subtrair dos casos totais acumulados
# os casos recuperados e os óbitos até então.
casosAtivos = util(casosTotais, casosRec)
casosAtivos = util(casosAtivos, obitos)

# Inicializa as séries temporais
serieObitos = pd.Series(data = obitos, index = datas)
serieCasos = pd.Series(data = casosAtivos, index = datas)

# Inicializa as legendas
legenda0 = mp.Patch(color = 'orange', label = 'Casos ativos')
legenda1 = mp.Patch(color = 'red', label = 'Óbitos')

# Dá os títulos, legendas, plota e salva o plot num arquivo .png
plt.title("COVID-19 em Rondonópolis - MT")
plt.legend(handles = [legenda0, legenda1])
plt.ylabel("Número de casos ativos")
plt.xlabel("Data")
plt.plot(serieObitos, color = 'red')
plt.plot(serieCasos, color = 'orange')
plt.show()
plt.savefig("covid.png")
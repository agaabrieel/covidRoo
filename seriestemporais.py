import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import matplotlib.dates as mdates
from bs4 import BeautifulSoup
import requests
from datetime import date, datetime, timedelta
import re
from statsmodels.tsa.stattools import adfuller, kpss, levinson_durbin_pacf

# O link n'onde os dados podem ser obtidos
link = 'http://www.rondonopolis.mt.gov.br/covid-19/boletins/'

# Obtendo as datas relevantes e as convertendo para o formato adequado 
hoje = date.today()
data_final = hoje
ontem = hoje - timedelta(days=1)

# Formatando o link dos boletins
if datetime.now().hour > 18:
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

def util2(listA, listB, dif = 1):

    listaSubtraida = list()

    if len(listA) != len(listB):
        print("Tamanho incompatível")
    i = 0
    while i < len(listA):
        if i >= dif:
            listaSubtraida.append(listA[i] - listB[i-dif])
            i += 1
        else: listaSubtraida.append(0); i+= 1
    return listaSubtraida

def util3(listA, n):
    
    listaFinal = list()

    i = 0
    while i < len(listA):
        listaFinal.append(listA[i]*n)
        i += 1
    
    return listaFinal

def util4(listA, n):

    listaFinal = list()

    i = 0
    while i < len(listA):
        listaFinal.append(n)
        i += 1

    return listaFinal

def util5(listA, n):

    listaFinal = list()

    k = int()
    i = 0
    while i < len(listA):
        k = n/listA[i]
        listaFinal.append(k)
        i += 1

    return listaFinal

def util6(listA, listB):
    
    listaFinal = list()

    i = 0
    while i < len(listA):
        listaFinal.append(listA[i]*listB[i])
        i += 1
    
    return listaFinal

def estacionarSerie(serie, dif):

    serieEstacionaria = list()
    resultados = adfuller(serie, autolag = 'AIC')
    while resultados[1] < 0.05:
        serieEstacionaria = util2(serie, dif = dif + 1)
        resultados = adfuller(serieEstacionaria, autolag = 'AIC')
        dif += 1
    return serieEstacionaria

# Para calcular o número de casos ativos de um período t, é necessário subtrair dos casos totais acumulados
# os casos recuperados e os óbitos até então.
casosAtivos = util(casosTotais, casosRec)
casosAtivos = util(casosAtivos, obitos)
obitosDiarios = util2(obitos, obitos)
internações = util3(casosAtivos, 0.135)
internaçõesUTI = util3(casosAtivos, 0.054)
internaçõesEnfermaria = util3(casosAtivos, 0.081)
leitosEnfermaria = util4(list(datas), 110)
leitosUTI = util4(list(datas), 31)

# Inicializa as séries temporais
serieObitos = pd.Series(data = obitos, index = datas)
serieCasos = pd.Series(data = casosAtivos, index = datas)
serieInternações = pd.Series(data = internações, index = datas)
serieInternaçõesUTI = pd.Series(data = internaçõesUTI, index = datas)
serieInternaçõesEnfermaria = pd.Series(data = internaçõesEnfermaria, index = datas)
seriesLeitosEnfermaria = pd.Series(data = leitosEnfermaria, index = datas)
seriesLeitosUTI = pd.Series(data = leitosUTI, index = datas)
# dados = estacionarSerie(casosAtivos, dif = 1)
# serieCasosEst = pd.Series(dados, index = datas)


# Testa se as séries são estacionárias ou se as trends são
# testeObitos = adfuller(serieObitos, autolag = 'AIC')
# testeCasos = adfuller(serieCasos, autolag = 'AIC')
# testeTrendObitos = kpss(serieObitos, regression='c')
# testeTrendCasos = kpss(serieCasos, regression='c')

# Printa os resultados

# print('Teste ADF\n')
# print('Óbitos:')
# print(f'{testeObitos[0]}')
# print(f'{testeObitos[1]}')
# for key, value in testeObitos[4].items():
#     print(f'{key}, {value}')

# print('Casos:\n')
# print(f'{testeCasos[0]}')
# print(f'{testeCasos[1]}')
# for key, value in testeCasos[4].items():
#     print(f'{key}, {value}')

# print('Teste KPSS\n')
# print('Óbitos:')
# print(f'{testeTrendObitos[0]}')
# print(f'{testeTrendObitos[1]}')
# for key, value in testeTrendObitos[3].items():
#     print(f'{key}, {value}')

# print('Casos:\n')
# print(f'{testeTrendCasos[0]}')
# print(f'{testeTrendCasos[1]}')
# for key, value in testeTrendCasos[3].items():
#     print(f'{key}, {value}')

# print('Obitos diários:\n')
# print(f'{testeTrendObitosDiarios[0]}')
# print(f'{testeTrendObitosDiarios[1]}')
# for key, value in testeTrendObitosDiarios[3].items():
#     print(f'{key}, {value}')

# Inicializa as legendas
legenda0 = mp.Patch(color = 'orange', label = 'Casos ativos')
legenda1 = mp.Patch(color = 'red', label = 'Óbitos')
legenda2 = mp.Patch(color = 'black', label = 'Leitos UTI')
legenda3 = mp.Patch(color = 'red', label = 'Internações em UTI')
legenda4 = mp.Patch(color = 'orange', label = 'Internações em enfermaria')
legenda5 = mp.Patch(color = 'blue', label = 'Leitos enfermaria')
legenda6 = mp.Patch(color = 'blue', label = 'Internações totais')

# legenda3 = mp.Patch(color = 'blue', label = 'Série de casos estacionada')

# Inicia duas figuras, formata a forma do eixo x e inicia um subplot contendo um axe para cada figura
fig1 = plt.figure(1, figsize = (10, 8))
plot1 = fig1.add_subplot(111)
fig1.autofmt_xdate(rotation=30)

# Dá os títulos, legendas e plota
plot1.set_title("Casos ao longo do tempo")
plot1.legend(handles = [legenda0, legenda1, legenda6], loc = 0)
plot1.set_ylabel("Pessoas")
plot1.set_xlabel("Data")
plot1.fmt_xdata = mdates.DateFormatter('%d-%m-%y')
plot1.plot(serieObitos, color = 'red')
plot1.plot(serieCasos, color = 'orange')
plot1.plot(serieInternações, color = 'blue')
fig1.savefig('covidroo.jpg')

# Inicia uma figura com um subplot
fig2 = plt.figure(2, figsize = (10, 8))
plot2 = fig2.add_subplot(111)
fig2.autofmt_xdate(rotation=30)

# Dá os títulos, legendas e plota
plot2.set_title('Internações vs. Leitos')
plot2.legend(handles = [legenda2, legenda3, legenda4, legenda5], loc = 0)
plot2.set_ylabel('Pessoas/vagas')
plot2.set_xlabel("Data")
plot2.fmt_xdata = mdates.DateFormatter('%d-%m-%y')
plot2.plot(serieInternações*0.4, '-', color = 'red')
plot2.plot(serieInternações*0.6, '-', color = 'orange')
plot2.plot(serieInternações*util5(internações, 31), '--', color = 'black')
plot2.plot(serieInternações*util5(internações, 110), '--', color = 'blue')
fig2.savefig('internações.jpg')

# Exibe os gráficos
plt.show()
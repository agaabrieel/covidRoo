import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import matplotlib.dates as mdates
from bs4 import BeautifulSoup
from pandas.core.indexing import IndexingError
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
if datetime.now().hour > 17:
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

# As funções a seguir são utilitárias usadas para tratar os dados
def util(listA, listB):

    listaSubtraida = list()

    if len(listA) != len(listB):
        print("Tamanho incompatível")
    i = 0
    while i < len(listA):
        listaSubtraida.append(listA[i] - listB[i])
        i += 1
    return listaSubtraida

def somaListas(listA, listB):

    listaSomada = list()

    if len(listA) != len(listB):
        print("Tamanho incompatível")
    i = 0
    while i < len(listA):
        listaSomada.append(listA[i] + listB[i])
        i += 1
    return listaSomada

def util2(listA, listB, dif = 1):

    listaFinal = list()

    if len(listA) != len(listB):
        print("Tamanho incompatível")
    i = 0
    while i < len(listA):
        if (i - dif) >= 0:
            listaFinal.append(listA[i] - listB[i-dif])
            i += 1
        else: listaFinal.append(0); i+= 1
    return listaFinal

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

def util6(serie, dif):

    serieEstacionaria = list()
    resultados = adfuller(serie, autolag = 'AIC')
    while resultados[1] < 0.05:
        serieEstacionaria = util2(serie, dif = dif + 1)
        resultados = adfuller(serieEstacionaria, autolag = 'AIC')
        dif += 1
    return serieEstacionaria

def util7(serie, n):

    listaFinal = list()
    media = int()

    i = 0
    while i < len(serie):
        j = 0
        media = 0
        while j < n:
            if i - j >= 0:
                media += serie[i-j]
                j += 1
            else: j+=1; continue
        if i > 0:
            media /= j
        listaFinal.append(media)
        i += 1
    return listaFinal

# Finalmente, os dados através de list comprehensions
# O formato usado separa os dados encontrandos em ',' e mapeia cada entrada da lista separada a um inteiro
# Os índices 0 a 2 e 7 a (len(dados)-2) simplesmente ignora as entradas desnecessárias dos dados encontrados ('data:', '[' e ']')
casosTotais = [int(s) for s in dados[0][7:len(dados[0])-1].split(',')]
casosRec = [int(s) for s in dados[1][7:len(dados[1])-1].split(',')]
obitos = [int(s) for s in dados[2][7:len(dados[2])-1].split(',')]

# Para calcular o número de casos ativos de um período t, é necessário subtrair dos casos totais acumulados
# os casos recuperados e os óbitos até então.
casosAtivos = util(casosTotais, casosRec)
casosAtivos = util(casosAtivos, obitos)
novosCasos = util2(casosTotais, casosTotais)
mediaCasosAtivos = util7(casosAtivos, 5)
obitosDiarios = util2(obitos, obitos)
internações = util3(casosAtivos, 0.135)
internaçõesUTI = util3(casosAtivos, 0.054)
internaçõesEnfermaria = util3(casosAtivos, 0.081)
leitosEnfermaria = util4(list(datas), 110)
leitosUTI = util4(list(datas), 31)
leitosTotais = somaListas(leitosEnfermaria, leitosUTI)

# Inicializa as séries temporais
serieObitos = pd.Series(data = obitos, index = datas)
serieObitosDiarios = pd.Series(data = obitosDiarios, index = datas)
serieCasos = pd.Series(data = casosAtivos, index = datas)
serieNovosCasos = pd.Series(data = novosCasos, index = datas)
serieMediaCasosAtivos = pd.Series(data = mediaCasosAtivos, index = datas)
serieInternações = pd.Series(data = internações, index = datas)
serieInternaçõesUTI = pd.Series(data = internaçõesUTI, index = datas)
serieInternaçõesEnfermaria = pd.Series(data = internaçõesEnfermaria, index = datas)
seriesLeitosEnfermaria = pd.Series(data = leitosEnfermaria, index = datas)
seriesLeitosUTI = pd.Series(data = leitosUTI, index = datas)
serieLeitosTotais = pd.Series(data = leitosTotais, index = datas)
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
legenda7 = mp.Patch(color = 'green', label = 'Média de Casos Ativos (7 dias)')
legenda8 = mp.Patch(color = 'black', label = 'Vagas totais de leitos')
legenda9 = mp.Patch(color = 'green', label = 'Novos casos')
legenda10 = mp.Patch(color = 'red', label = 'Óbitos diários')

# legenda3 = mp.Patch(color = 'blue', label = 'Série de casos estacionada')

# Inicia uma figura, formata a forma do eixo x e inicia um subplot contendo um axe
fig1 = plt.figure(1, figsize = (10, 8))
plot1 = fig1.add_subplot(111)
fig1.autofmt_xdate(rotation=30)

# Dá os títulos, legendas, plota e salva
plot1.set_title("Casos ao longo do tempo")
plot1.legend(handles = [legenda0, legenda1, legenda6, legenda7, legenda8], loc = 0)
plot1.set_ylabel("Pessoas")
plot1.set_xlabel("Data")
plot1.fmt_xdata = mdates.DateFormatter('%d-%m-%y')
plot1.plot(serieObitos, color = 'red')
plot1.plot(serieCasos, color = 'orange')
plot1.plot(serieInternações, color = 'blue')
plot1.plot(serieMediaCasosAtivos, color = 'green')
plot1.plot(serieLeitosTotais, '--', color = 'black')
fig1.savefig('covidroo.jpg')

# Inicia uma figura com um subplot
fig2 = plt.figure(2, figsize = (10, 8))
plot2 = fig2.add_subplot(111)
fig2.autofmt_xdate(rotation=30)

# Dá os títulos, legendas, plota e salva
plot2.set_title('Internações vs. Leitos')
plot2.legend(handles = [legenda2, legenda3, legenda4, legenda5, legenda9], loc = 0)
plot2.set_ylabel('Pessoas/vagas')
plot2.set_xlabel("Data")
plot2.fmt_xdata = mdates.DateFormatter('%d-%m-%y')
plot2.plot(serieInternações*0.4, '-', color = 'red')
plot2.plot(serieInternações*0.6, '-', color = 'orange')
plot2.plot(serieInternações*util5(internações, 31), '--', color = 'black')
plot2.plot(serieInternações*util5(internações, 110), '--', color = 'blue')
fig2.savefig('internações.jpg')

# Inicia uma figura com um subplot
fig3 = plt.figure(3, figsize = (10, 8))
plot3 = fig3.add_subplot(111)
fig3.autofmt_xdate(rotation=30)

# Dá os títulos, legendas, plota e salva
plot3.set_title("Novos Casos e Óbitos diários")
plot3.legend(handles = [legenda9, legenda10], loc = 0)
plot3.set_ylabel("Pessoas")
plot3.set_xlabel("Data")
plot3.fmt_xdata = mdates.DateFormatter('%d-%m-%y')
plot3.plot(serieNovosCasos, color = 'green')
plot3.plot(serieObitosDiarios, color = 'red')
fig3.savefig('novosCasos.jpg')

# Exibe os gráficos
plt.show()
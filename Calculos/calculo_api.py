from flask import Flask, request, jsonify, make_response, template_rendered
from flask_cors import CORS
import pandas as pd
import numpy_financial as np
import csv
from datetime import date
from dateutil.relativedelta import relativedelta
import math

data_atual = date.today()

app = Flask(__name__)
CORS(app)

class Linha:
    def __init__(self, parcela, saldo_devedor, juros, amortizacao, parcela_normal,  seguros_taxa, parcela_final):
        self.parcela = parcela,
        self.saldo_devedor = saldo_devedor,
        self.juros = juros,
        self.amortizacao = amortizacao,
        self.parcela_normal = parcela_normal,
        self.seguros_taxa = seguros_taxa,
        self.parcela_final = parcela_final,
    
    def to_dict(self):
        return {
            "parcela": self.parcela,
            "saldo_devedor": self.saldo_devedor,
            "juros": self.juros,
            "amortizacao": self.amortizacao,
            "parcela_normal": self.parcela_normal,
            "seguros_taxa": self.seguros_taxa,
            "parcela_final": self.parcela_final
        }

def truncar(valor, casas_decimais):
    fator = 10 ** casas_decimais
    return math.trunc(valor * fator) / fator

def form_infos(dias, amortizacao, juros):
    return {
        "dias": dias,
        "amortizacao": amortizacao,
        "juros" : juros
    }

def infos_IOF(parcelas_input, amortizacao, array, juros):
    parcela = 0

    indice_inverso = parcelas_input - 1 # aqui irei decrementar o indice para adiconar inversamento a amoritzação no array.
    
    for i in range(parcelas_input):
        
        parcela =  parcela + 1

        data_atual_mais_um_mes = data_atual + relativedelta(months=parcela)

        dif = data_atual_mais_um_mes - data_atual

        dif_days = 365 if dif.days > 365 else dif.days

        dados = form_infos(dif_days, amortizacao[indice_inverso], juros)

        indice_inverso = indice_inverso - 1

        array.append(dados)

def calculando_juros(valor_financiado, juros, parcelas):

    valor_calculado = (np.pmt(juros, parcelas, -valor_financiado)) / 100
    valor_calculado = round(valor_calculado, 4)

    return valor_calculado 

def pgto(valor_financiado, juros, parcelas):

    juros = juros / 100 
    pgto = np.pmt(juros, parcelas, -valor_financiado)

    # pgto = (112327.39 * 1.09) / (1 - ( 1 + 0.0109)**-180) Calculo usado
    pgto = round(pgto,4)

    return pgto

def amortizacao(parcela, juros):
    amortizacao_01 = parcela - juros

    return round(amortizacao_01, 4)

def subtraindo_total(amortizacao, valor_subtraido):
    saldo_devedor = round((valor_subtraido - amortizacao), 4)
    return saldo_devedor

def seguro_prestamista(porcentagem, saldo_devedor):
    retorno = (saldo_devedor * porcentagem) / 100
    retorno = round(retorno, 4)
    return retorno

# Usada para calcular somente da PRICE
def calculando_financiamento(valor_imovel, valor_solicitado, IOF):

        iof_calculado = IOF
        Tarifa_de_cadastro =  316.00
        Taxa_de_Engenharia =  518.43
        Taxa_de_analise_juridica =  19.84
        Custo_certidao =  71.37
        Taxa_estruturacao = 0.06 * valor_solicitado

        # Custas_cartorio
        valor_fixo_custas = 295.90
        valor_consultado_antes = 0
        valor_consultado_depois = 0

        # valor_financiado_final = iof_calculado + Tarifa_de_cadastro + Taxa_de_Engenharia + Taxa_de_analise_juridica + Taxa_estruturacao + Custo_certidao + valor_solicitado

        valor_antes_cartorio = iof_calculado + Tarifa_de_cadastro + Taxa_de_Engenharia + Taxa_de_analise_juridica + Taxa_estruturacao + Custo_certidao + valor_solicitado

        # Fazendo consulta antes do cartorio.
        with open('nova_tabela.csv', newline='') as csvfile:
            csvfile_list = csv.reader(csvfile)
            for row in csvfile_list:
                if 'A' in row[2]:
                    continue
                else:
                    valor_min = float(row[1])
                    valor_max = float(row[2])
                    if(valor_antes_cartorio > valor_min and valor_antes_cartorio < valor_max):
                        valor_consultado_antes = float(row[-1])
                        break

        Custas_cartorio = valor_fixo_custas + (1+0.11) * valor_consultado_antes

        valor_financiado_final = iof_calculado + Tarifa_de_cadastro + Taxa_de_Engenharia + Taxa_de_analise_juridica + Taxa_estruturacao + Custas_cartorio + Custo_certidao + valor_solicitado
        
        valor_apos_cartorio = valor_financiado_final

        # Fazendo consulta depois do cartorio para validar se o valor não irá mudar de faixa.
        with open('nova_tabela.csv', newline='') as csvfile:
            csvfile_list = csv.reader(csvfile)
            for row in csvfile_list:
                if 'A' in row[2]:
                    continue
                else:
                    valor_min = float(row[1])
                    valor_max = float(row[2])
                    if(valor_apos_cartorio > valor_min and valor_apos_cartorio < valor_max):
                        valor_consultado_depois = float(row[-1])
                        break

        if(valor_consultado_antes != valor_consultado_depois and valor_consultado_depois != 0):
            extraindo_diferenca = valor_consultado_depois - valor_consultado_antes

            valor_financiado_final = valor_financiado_final + extraindo_diferenca

        valor_financiado_final = round(valor_financiado_final, 4)

        return valor_financiado_final

# Usada para calcular somente o IOF da PRICE
def calculando_IOF_loop(vlr_calculado, juros, num_parcelas):   

    pgto_01 = pgto(vlr_calculado, juros, num_parcelas) # Valor fixo da parcela no modelo PRICE, ele não se altera.
    saldo_devedor = vlr_calculado # O saldo devedor sempre irá receber o valor calculado.

    num_parcelas_clientes = 0 # Numero de parcelas solicitada pelo cliente.

    array_amortizacao = [] # Este array irá receber a amortização, pois irei usar ela para realizar o cálculo.
    array_infos = [] # Este array irá armazenar as informações dos dados, para asism realizar o seu cálculo.

    while True:
        juros_calculado = calculando_juros(saldo_devedor,juros, num_parcelas) # Calculando o juros do "empréstimo"
        amortizacao_calculo = amortizacao(pgto_01, juros_calculado) # Realizando o calculo da amortização.
        subtracao_calculo = subtraindo_total(amortizacao_calculo, saldo_devedor) # subtraindo o valor amortizado do saldo devedor.

        saldo_devedor = subtracao_calculo # o Saldo devedor agora irá receber essa subtração.

        num_parcelas_clientes = num_parcelas_clientes + 1 # Aqui começo a contagem das parcelas a partir do 0, por tanto irei incrementa-la até ser igual ao que o cliente solicitou.

        array_amortizacao.append(amortizacao_calculo) # armazeno a amortização no array.

        if(num_parcelas_clientes >= num_parcelas): # condição para o break do loop.
            break
    
    infos_IOF(num_parcelas, array_amortizacao, array_infos, juros) # Aqui eu monto a tabela para realizar o calculo do IOF.

    IOF_calculado = 0

    # Aqui de fato estou calculando o IOF da operação, a amortização eu realizo o calculo com ela invertida, assim como está na planilha de Excel.
    for value in array_infos:
        realizando_calculo = (value['dias'] * value['amortizacao'] * 0.0008219) / 10 # Realizando o Calulo e multiplicando pela Aliquota.
        realizando_calculo = truncar(realizando_calculo, 2) # Trunco o valor.
        IOF_calculado = IOF_calculado + realizando_calculo # incremento o IOF calculado.
 
    calculando_iof_adicional = (0.38 * vlr_calculado) / 100 # Calculo do IOF adicional
 
    return IOF_calculado + calculando_iof_adicional # Retorno o calculo do IOF diário e o Adicional somados.

def calcular_vp_vf_carencia(taxa, n_periodos, valor_futuro):
    taxa = taxa / 100
    vp = valor_futuro / (1 + taxa) ** n_periodos
    vp = round(vp, 2)
    return vp

def calculando_financiamento_carencia_primeiro_valor(vlr_imovel, valor_solicitado, IOF, carencia, juros):

        iof_calculado = IOF
        Tarifa_de_cadastro =  316.00
        Taxa_de_Engenharia =  518.43
        Taxa_de_analise_juridica =  19.84
        Custo_certidao =  71.37
        Taxa_estruturacao = 0.06 * valor_solicitado

        # Custas_cartorio
        valor_fixo_custas = 295.90
        valor_consultado_antes = 0
        valor_consultado_depois = 0

        # valor_financiado_final = iof_calculado + Tarifa_de_cadastro + Taxa_de_Engenharia + Taxa_de_analise_juridica + Taxa_estruturacao + Custo_certidao + valor_solicitado

        valor_antes_cartorio = iof_calculado + Tarifa_de_cadastro + Taxa_de_Engenharia + Taxa_de_analise_juridica + Taxa_estruturacao + Custo_certidao + valor_solicitado

        # Fazendo consulta antes do cartorio.
        with open('nova_tabela.csv', newline='') as csvfile:
            csvfile_list = csv.reader(csvfile)
            for row in csvfile_list:
                if 'A' in row[2]:
                    continue
                else:
                    valor_min = float(row[1])
                    valor_max = float(row[2])
                    if(valor_antes_cartorio > valor_min and valor_antes_cartorio < valor_max):
                        valor_consultado_antes = float(row[-1]) 

        Custas_cartorio = valor_fixo_custas + (1+0.11) * valor_consultado_antes
        valor_financiado_final = iof_calculado + Tarifa_de_cadastro + Taxa_de_Engenharia + Taxa_de_analise_juridica + Taxa_estruturacao + Custas_cartorio + Custo_certidao + valor_solicitado
        valor_apos_cartorio = valor_financiado_final
        
        valor_financiado_final = iof_calculado + Tarifa_de_cadastro + Taxa_de_Engenharia + Taxa_de_analise_juridica + Taxa_estruturacao + Custas_cartorio + Custo_certidao + valor_solicitado

        # o juros é calculado em cima do valor financiado final e somado, para assim então tirar as taxas da operação, por tanto sendo necessáiro, armazenar o valor antes do cálculo.
        valor_financiado_final_variado = valor_financiado_final

        if carencia == 3:
            seguro_dfi = (vlr_imovel*14) / 100000 
            Taxa_administracao =  40.00
            Taxa_prestamista = 0.035 

            for i in range(2):
                seguro_prestamista_calculado = seguro_prestamista(Taxa_prestamista, valor_financiado_final_variado)

                valor_financiado_final_variado = calculando_juros_carencia_separado(valor_financiado_final, juros, 0)

                valor_financiado_final = valor_financiado_final + seguro_prestamista_calculado + seguro_dfi + Taxa_administracao
        
        if carencia == 2:
            seguro_dfi = (vlr_imovel*14) / 100000 
            Taxa_administracao =  40.00
            Taxa_prestamista = 0.035 

            seguro_prestamista_calculado = seguro_prestamista(Taxa_prestamista, valor_financiado_final)


            valor_financiado_final = valor_financiado_final + seguro_prestamista_calculado + seguro_dfi + Taxa_administracao
            
        # Fazendo consulta depois do cartorio para validar se o valor não irá mudar de faixa.
        with open('nova_tabela.csv', newline='') as csvfile:
            csvfile_list = csv.reader(csvfile)
            for row in csvfile_list:
                if 'A' in row[2]:
                    continue
                else:
                    valor_min = float(row[1])
                    valor_max = float(row[2])
                    if(valor_apos_cartorio > valor_min and valor_apos_cartorio < valor_max):
                        valor_consultado_depois = float(row[-1]) 

        if(valor_consultado_antes != valor_consultado_depois and valor_consultado_depois != 0):
            extraindo_diferenca = valor_consultado_depois - valor_consultado_antes

            valor_financiado_final = valor_financiado_final + extraindo_diferenca

        valor_financiado_final = round(valor_financiado_final, 4)

        return valor_financiado_final

def calculando_juros_carencia_separado(saldo_devedor, juros, carencia):

    juros = juros / 100
    
    # salvando o saldo incial pois o valor somado não muda.
    saldo_inicial = saldo_devedor
    valor_retorno = saldo_devedor*juros
    somando_juros = 0

    valor_retorno = saldo_devedor*juros
    saldo_devedor+=valor_retorno
    somando_juros+=valor_retorno
    
    return saldo_inicial + somando_juros

def infos_IOF_carencia(parcelas_input, amortizacao, array, juros):
    parcela = 0

    for i in range(parcelas_input):

        parcela =  parcela + 1

        data_atual_mais_um_mes = data_atual + relativedelta(months=parcela)

        dif = data_atual_mais_um_mes - data_atual

        dif_days = 365 if dif.days > 365 else dif.days

        dados = form_infos(dif_days, amortizacao[i], juros)

        array.append(dados)

def calculando_juros_carencia(saldo_devedor, juros, carencia):

    juros = juros / 100
    
    # salvando o saldo incial pois o valor somado não muda.
    saldo_inicial = saldo_devedor
    valor_retorno = saldo_devedor*juros
    somando_juros = 0

    if carencia == 3:
        for i in range(2):
            valor_retorno = saldo_devedor*juros
            saldo_devedor+=valor_retorno
            somando_juros+=valor_retorno
    
    if carencia == 2:
        valor_retorno = saldo_devedor*juros
        saldo_devedor+=valor_retorno
        somando_juros+=valor_retorno
        
    return saldo_inicial + somando_juros

def calculando_iof_carencia(vlr_calculado_inicial, vlr_calculado_proximo, juros, num_parcelas, carencia):
        
        pgto_01 = pgto(vlr_calculado_inicial, juros, num_parcelas) # Valor fixo da parcela no modelo PRICE, ele não se altera.

        saldo_devedor = vlr_calculado_inicial # O saldo devedor sempre irá receber o valor calculado.

        num_parcelas_clientes = 1 # Numero de parcelas solicitada pelo cliente.

        array_amortizacao = [] # Este array irá receber a amortização, pois irei usar ela para realizar o cálculo.
        array_infos = [] # Este array irá armazenar as informações dos dados, para asism realizar o seu cálculo.

        num_parcelas = num_parcelas + carencia - 1

        while True:
            if num_parcelas_clientes < carencia:
                array_amortizacao.append(0)
                num_parcelas_clientes = num_parcelas_clientes + 1
            else:
                
                calculo = calcular_vp_vf_carencia(juros, num_parcelas_clientes, pgto_01)

                array_amortizacao.append(calculo)

                num_parcelas_clientes =  num_parcelas_clientes + 1

                if num_parcelas_clientes > num_parcelas:
                    break
            
        infos_IOF_carencia(num_parcelas, array_amortizacao, array_infos, juros) # Aqui eu monto a tabela para realizar o calculo do IOF.

        IOF_calculado = 0

        # Aqui de fato estou calculando o IOF da operação, a amortização eu realizo o calculo com ela invertida, assim como está na planilha de Excel.
        for value in array_infos:
            realizando_calculo = (value['dias'] * value['amortizacao'] * 0.0008219) / 10 # Realizando o Calulo e multiplicando pela Aliquota.
            # print(f'Dias -> {value['dias']}, calculo -> {value['amortizacao']}, calculo -> {realizando_calculo}')
            realizando_calculo = truncar(realizando_calculo, 2) # Trunco o valor.
            IOF_calculado = IOF_calculado + realizando_calculo # incremento o IOF calculado.

        calculando_iof_adicional = (0.38 * vlr_calculado_proximo) / 100 # Calculo do IOF adicional

        return IOF_calculado + calculando_iof_adicional # Retorno o calculo do IOF diário e o Adicional somados.

# IOF Final.
def calculando_emprestimo_final(vlr_imovel, vlr_solicitado, juros, num_parcelas, carencia):
    seguro_dfi = (vlr_imovel*14) / 100000 
    Taxa_administracao =  40.00
    Taxa_prestamista = 0.035 

    # Valores antes do cartório
    valor_antes_cartorio = 0
    valor_apos_cartorio = 0

    if carencia == 0:
        valor_financiado = calculando_financiamento(vlr_imovel, vlr_solicitado, 0)

        # Calculando primeiro IOF
        x1 = calculando_IOF_loop(valor_financiado, juros, num_parcelas)
        x2 = calculando_IOF_loop(x1, juros, num_parcelas)
        x3 = calculando_IOF_loop(x2, juros, num_parcelas)
        x4 = calculando_IOF_loop(x3, juros, num_parcelas)
        x5 = calculando_IOF_loop(x4, juros, num_parcelas)

        somando_x = x1+x2+x3+x4+x5

        iof_final = calculando_IOF_loop(valor_financiado + somando_x, juros, num_parcelas) # Aqui estou calculando o IOF já usando toda a soma dos valores de X.

        valor_financiado_02 = calculando_financiamento(vlr_imovel, vlr_solicitado, iof_final)  # Após isso faco a conta de todo o valor somado ao IOF.

        iof_final_again = calculando_IOF_loop(valor_financiado_02, juros, num_parcelas) # Como acontece das custas de cartório se alterarem de acordo com cada roda de cálculo de IOF, eu recalculo o valor denovo.

        valor_financiado_03 = calculando_financiamento(valor_financiado_02, vlr_solicitado, iof_final_again) # E uso esse novo IOF em um novo cálculo, se caso o valor for diferente ele irá pegar, se não ele irá se manter desde a primeira chamada.

        saldo_devedor = valor_financiado_03
        num_parcelas_clientes = 0

        pgto_01 = pgto(saldo_devedor, juros, num_parcelas) # não muda

        dados_retorno = []
        dados_datas = []
        dados_amortizacao = []

        while True:
            juros_cliente = calculando_juros(saldo_devedor, juros, num_parcelas)
            amortizacao_cliente = amortizacao(pgto_01, juros_cliente)
            calculando_subtracao = subtraindo_total(amortizacao_cliente, saldo_devedor)
            seguro_prestamista_calculado = seguro_prestamista(0.035, saldo_devedor)

            saldo_devedor = calculando_subtracao
            
            parcela_final = seguro_prestamista_calculado + Taxa_administracao + seguro_dfi + pgto_01

            parcela_normal = pgto_01

            somando_taxas = seguro_prestamista_calculado + Taxa_administracao + seguro_dfi

            exibicao_saldo_devedor = round(saldo_devedor, 2)
            exibicao_amortizacao = round(amortizacao_cliente, 2)

            exibicao_juros = round(juros_cliente, 2)
            exibicao_prestamista = round(seguro_prestamista_calculado, 2)
            exibicao_parcela = round(parcela_final, 2)
            exibicao_parcela_normal = round(parcela_normal, 2)
            exibicao_taxas = round(somando_taxas, 2)


            rowValue = Linha(num_parcelas_clientes, exibicao_saldo_devedor, exibicao_juros, exibicao_amortizacao, exibicao_parcela_normal, exibicao_taxas, exibicao_parcela)
            dados_amortizacao.append(exibicao_amortizacao)

            dados_retorno.append(rowValue.to_dict())
            parcela_final = 0

            num_parcelas_clientes = num_parcelas_clientes + 1

            if(num_parcelas_clientes >= num_parcelas):
                break
                
        # infos_IOF(num_parcelas, dados_amortizacao, dados_datas, juros)
    else:
        saldo_inicial = calculando_financiamento_carencia_primeiro_valor(vlr_imovel, vlr_solicitado, 0, carencia, juros)

        valor_variavel = saldo_inicial
        saldo_calculado_com_juros = 0
        calculo_iof_carencia = 0
        
        for i in range(4):
            # calculando o juros do valor inicial
            saldo_calculado_com_juros = calculando_juros_carencia(valor_variavel, juros, carencia)

            # calculando o IOF da operação com os valores após o recalculo.
            calculo_iof_carencia = calculando_iof_carencia(saldo_calculado_com_juros, valor_variavel, juros, num_parcelas, carencia)

            valor_variavel = saldo_inicial + calculo_iof_carencia

        saldo_devedor_operacao = calculo_iof_carencia + saldo_inicial

        saldo_calculado_com_juros = calculando_juros_carencia(saldo_devedor_operacao, juros, carencia)

        pgto_01 = pgto(saldo_calculado_com_juros, juros, num_parcelas) # não muda

        dados_retorno = []
        dados_datas = []
        dados_amortizacao = []
        
        num_parcelas_clientes = 0
        indice = 0
        indice_um = 0

        primeira_iteracao = True
        primeira_iteracao_dois = True
        juros_cliente = 0  # Inicializa o valor dos juros para a primeira linha

        while True:
            if num_parcelas_clientes < carencia:
                # Exibe a linha atual com saldo e juros calculados anteriormente

                if primeira_iteracao:
                    primeira_iteracao = False
                    exibicao_saldo_devedor_operacao = round(saldo_devedor_operacao, 2)
                    rowValue = Linha(num_parcelas_clientes, exibicao_saldo_devedor_operacao, 0, 0, 0 , 0, 0)
                    dados_amortizacao.append(0)
                    dados_retorno.append(rowValue.to_dict())

                else:
                    exibicao_saldo_devedor_operacao = round(saldo_devedor_operacao, 2)
                    exibicao_juros = round(juros_cliente, 2)

                    rowValue = Linha(num_parcelas_clientes, exibicao_saldo_devedor_operacao, exibicao_juros, 0, 0 , 0, 0)
                    dados_retorno.append(rowValue.to_dict())
                    dados_amortizacao.append(0)

                    # print(f"{saldo_devedor_operacao:.2f}", f"{juros_cliente:.2f}", 0, 0, 0, 0, 0)

                # Calcula os juros para o saldo atual (que será exibido na próxima linha)
                juros_cliente = calculando_juros(saldo_devedor_operacao, juros, num_parcelas)
                
                # Atualiza o saldo para a próxima iteração
                saldo_devedor_operacao += juros_cliente
                num_parcelas_clientes += 1
                indice += 1

            else:
                
                # corrigindo erro de incrementação de um juros a mais na operação.
                if indice_um == 0:
                    saldo_devedor_operacao -= juros_cliente
                    indice_um += 1

                juros_cliente = calculando_juros(saldo_devedor_operacao, juros, num_parcelas)
                amortizacao_cliente = amortizacao(pgto_01, juros_cliente)
                calculando_subtracao = subtraindo_total(amortizacao_cliente, saldo_devedor_operacao)
                seguro_prestamista_calculado = seguro_prestamista(0.035, saldo_devedor_operacao)

                saldo_devedor_operacao = calculando_subtracao
        
                parcela_final = seguro_prestamista_calculado + Taxa_administracao + seguro_dfi + pgto_01

                parcela_normal = pgto_01

                somando_taxas = seguro_prestamista_calculado + Taxa_administracao + seguro_dfi

                exibicao_saldo_devedor_operacao = round(saldo_devedor_operacao, 2)
                exibicao_amortizacao = round(amortizacao_cliente, 2)

                exibicao_juros = round(juros_cliente, 2)
                exibicao_prestamista = round(seguro_prestamista_calculado, 2)
                exibicao_parcela = round(parcela_final, 2)
                exibicao_parcela_normal = round(parcela_normal, 2)
                exibicao_taxas = round(somando_taxas, 2)

                rowValue = Linha(num_parcelas_clientes, exibicao_saldo_devedor_operacao, exibicao_juros, exibicao_amortizacao, exibicao_parcela_normal, exibicao_taxas, exibicao_parcela)
                dados_amortizacao.append(exibicao_amortizacao)

                dados_retorno.append(rowValue.to_dict())

                num_parcelas_clientes = num_parcelas_clientes + 1

                if(num_parcelas_clientes >= num_parcelas + carencia):
                    break

    return dados_retorno

def calcular_tir(fluxo_de_caixa, guess=0.1, max_iteracoes=1000, precisao=0.00001):
    tir = guess
    n = len(fluxo_de_caixa)
    
    for _ in range(max_iteracoes):
        vpl = 0
        derivada_vpl = 0
        
        # Calcula o VPL e a derivada do VPL
        for j in range(n):
            valor = fluxo_de_caixa[j]
            vpl += valor / (1 + tir) ** j
            derivada_vpl -= j * valor / (1 + tir) ** (j + 1)
        
        if derivada_vpl == 0:
            return None  # Evita divisão por zero
        
        delta = vpl / derivada_vpl
        tir -= delta
        
        if abs(delta) < precisao:
            return tir  # Retorna a TIR encontrada
    
    return None  # Não convergiu

def montando_tabela_CET(saldo_inicial, carencia, parcelas_array):

    valor_inicial = -saldo_inicial

    carencia_array = []

    # Valor inicial desembolsado (negativo no fluxo de caixa)
    if carencia == 3:
        carencia_array = [0.00, 0.00]
    if carencia == 2:
        carencia_array = [0.00]

    fluxo_de_caixa = [valor_inicial] + carencia_array + parcelas_array

    tir_mensal = calcular_tir(fluxo_de_caixa, guess=0.1)

    if tir_mensal is not None:
        cet_anual = (1 + tir_mensal) ** 12 - 1
        dados_cet = {
            "tir_mensal_CET" : f'{tir_mensal * 100:.2f}',
            "CET_Anual" : f'{cet_anual * 100:.2f}'
        }
        return dados_cet
    else:
        print("O cálculo da TIR não convergiu.")

def juros_a_a(juros):
    taxa_mensal = juros
    taxa_anual = (1+(juros / 100))**12-1

    obj = {
        'taxa_mensal': taxa_mensal,
        'taxa_anual': round((taxa_anual * 100), 2)
    }

    return obj



def calcular_vp_vf(taxa, n_periodos, valor_futuro):
    taxa = taxa / 100
  
    vp = valor_futuro / (1 + taxa) ** n_periodos
    return vp

def calculando_iof_carencia_SAC(vlr_calculado_inicial, vlr_calculado_proximo, juros, num_parcelas, carencia):

    amortizacao = vlr_calculado_inicial / num_parcelas

    num_parcelas_clientes = 1 # Numero de parcelas solicitada pelo cliente.

    saldo_inicial = vlr_calculado_inicial

    num_parcelas = num_parcelas + carencia - 1

    array_amortizacao = [] # Este array irá receber a amortização, pois irei usar ela para realizar o cálculo.
    array_infos = [] # Este array irá armazenar as informações dos dados, para asism realizar o seu cálculo.

    while True:
        if num_parcelas_clientes < carencia:
            array_amortizacao.append(0)
            num_parcelas_clientes+=1
            continue
        else:
            juros_calculado = calculando_juros(saldo_inicial, juros, 180)

            parcela = juros_calculado + amortizacao

            saldo_inicial = saldo_inicial - amortizacao

            array_amortizacao.append(parcela)

            num_parcelas_clientes =  num_parcelas_clientes + 1

            if num_parcelas_clientes > num_parcelas:
                break
    
    iof_diario = infos_iof_SAC(num_parcelas, array_amortizacao, array_infos, juros)

    calculando_iof_adicional = (0.38 * vlr_calculado_proximo) / 100 # Calculo do IOF adicional

    return iof_diario + calculando_iof_adicional # Retorno o calculo do IOF diário e o Adicional somados.

def infos_iof_SAC(num_parcelas, array_parcelas, array_infos, juros):

    iof_diario = 0.008219 / 100

    parcelas = 0
    iof_calculado = 0

    for value in array_parcelas:
        parcelas += 1

        data_atual_mais_um_mes = data_atual + relativedelta(months=parcelas)

        dif = data_atual_mais_um_mes - data_atual

        dif_days = 365 if dif.days > 365 else dif.days

        iof_diario_calculo = calcular_vp_vf_carencia(juros, parcelas, value)

        calculo_geral = dif_days * iof_diario_calculo * iof_diario

        iof_calculado += calculo_geral

    return iof_calculado

def calculando_IOF_loop_SAC(vlr_calculado, juros, num_parcelas):   

    saldo_devedor = vlr_calculado # O saldo devedor sempre irá receber o valor calculado.
    amortizacao_calculo = vlr_calculado / num_parcelas

    num_parcelas_clientes = 0 # Numero de parcelas solicitada pelo cliente.

    array_parcelas = [] # Este array irá receber a amortização, pois irei usar ela para realizar o cálculo.
    array_infos = [] # Este array irá armazenar as informações dos dados, para asism realizar o seu cálculo.

    while True:
        juros_calculado = calculando_juros(saldo_devedor,juros, num_parcelas) # Calculando o juros do "empréstimo"
        subtracao_calculo = subtraindo_total(amortizacao_calculo, saldo_devedor) # subtraindo o valor amortizado do saldo devedor.

        saldo_devedor = subtracao_calculo # o Saldo devedor agora irá receber essa subtração.

        num_parcelas_clientes = num_parcelas_clientes + 1 # Aqui começo a contagem das parcelas a partir do 0, por tanto irei incrementa-la até ser igual ao que o cliente solicitou.
        
        parcela_calculada = juros_calculado + amortizacao_calculo

        array_parcelas.append(parcela_calculada)

        if(num_parcelas_clientes >= num_parcelas): # condição para o break do loop.
            break
    
    IOF_calculado = infos_iof_SAC(num_parcelas, array_parcelas, array_infos, juros) # Aqui eu monto a tabela para realizar o calculo do IOF.

    calculando_iof_adicional = (0.38 * vlr_calculado) / 100 # Calculo do IOF adicional
 
    return IOF_calculado + calculando_iof_adicional # Retorno o calculo do IOF diário e o Adicional somados.

def calculando_emprestimo_final_SAC(vlr_imovel, vlr_solicitado, juros, num_parcelas, carencia):
    seguro_dfi = (vlr_imovel*14) / 100000 
    Taxa_administracao =  40.00
    Taxa_prestamista = 0.035 

    # Valores antes do cartório
    valor_antes_cartorio = 0
    valor_apos_cartorio = 0

    dados_retorno = []
    dados_amortizacao = []

    if carencia == 0:
        valor_financiado_sac = calculando_financiamento(vlr_imovel, vlr_solicitado, 0)

        dados_datas = []

        # Calculando primeiro IOF
        x1 = calculando_IOF_loop_SAC(valor_financiado_sac, juros, num_parcelas)
        x2 = calculando_IOF_loop_SAC(x1, juros, num_parcelas)
        x3 = calculando_IOF_loop_SAC(x2, juros, num_parcelas)
        x4 = calculando_IOF_loop_SAC(x3, juros, num_parcelas)
        x5 = calculando_IOF_loop_SAC(x4, juros, num_parcelas)

        somando_x = x1+x2+x3+x4+x5

        iof_final = calculando_IOF_loop_SAC(valor_financiado_sac + somando_x, juros, num_parcelas) # Aqui estou calculando o IOF já usando toda a soma dos valores de X.

        valor_financiado_02 = calculando_financiamento(vlr_imovel, vlr_solicitado, iof_final)  # Após isso faco a conta de todo o valor somado ao IOF.

        iof_final_again = calculando_IOF_loop_SAC(valor_financiado_02, juros, num_parcelas) # Como acontece das custas de cartório se alterarem de acordo com cada roda de cálculo de IOF, eu recalculo o valor denovo.

        valor_financiado_03 = calculando_financiamento(valor_financiado_02, vlr_solicitado, iof_final_again) # E uso esse novo IOF em um novo cálculo, se caso o valor for diferente ele irá pegar, se não ele irá se manter desde a primeira chamada.

        saldo_devedor = valor_financiado_03
        num_parcelas_clientes = 0

        amortizacao_calculo = saldo_devedor / num_parcelas

        while True:
            print(num_parcelas_clientes)
            juros_calculado = calculando_juros(saldo_devedor,juros, num_parcelas) # Calculando o juros do "empréstimo"
            subtracao_calculo = subtraindo_total(amortizacao_calculo, saldo_devedor) # subtraindo o valor amortizado do saldo devedor.
            seguro_prestamista_calculado = seguro_prestamista(0.035, saldo_devedor)

            saldo_devedor = subtracao_calculo # o Saldo devedor agora irá receber essa subtração.
            
            parcela_normal = juros_calculado + amortizacao_calculo

            somando_taxas = seguro_prestamista_calculado + Taxa_administracao + seguro_dfi

            parcela_final = seguro_prestamista_calculado + Taxa_administracao + seguro_dfi + parcela_normal

            exibicao_saldo_devedor = round(saldo_devedor, 2)
            exibicao_amortizacao = round(amortizacao_calculo, 2)

            exibicao_juros = round(juros_calculado, 2)
            exibicao_prestamista = round(seguro_prestamista_calculado, 2)
            exibicao_parcela = round(parcela_final, 2)
            exibicao_parcela_normal = round(parcela_normal, 2)
            exibicao_taxas = round(somando_taxas, 2)

            rowValue = Linha(num_parcelas_clientes, exibicao_saldo_devedor, exibicao_juros, exibicao_amortizacao, exibicao_parcela_normal, exibicao_taxas, exibicao_parcela)
            dados_amortizacao.append(exibicao_amortizacao)

            dados_retorno.append(rowValue.to_dict())
            parcela_final = 0

            num_parcelas_clientes = num_parcelas_clientes + 1 # Aqui começo a contagem das parcelas a partir do 0, por tanto irei incrementa-la até ser igual ao que o cliente solicitou.

            if(num_parcelas_clientes >= num_parcelas): # condição para o break do loop.
                break

    else:
        saldo_inicial = calculando_financiamento_carencia_primeiro_valor(vlr_imovel, vlr_solicitado, 0, carencia, juros)

        valor_variavel =  saldo_inicial

        saldo_calculado_com_juros = 0
        calculo_iof_carencia = 0
        
        for i in range(4):

            saldo_calculado_com_juros = calculando_juros_carencia(valor_variavel, juros, carencia)

            # calculando o IOF da operação com os valores após o recalculo.
            calculo_iof_carencia = calculando_iof_carencia_SAC(saldo_calculado_com_juros, valor_variavel ,juros, num_parcelas, carencia)

            valor_variavel = saldo_inicial + calculo_iof_carencia
        
        saldo_devedor_operacao = calculo_iof_carencia + saldo_inicial

        saldo_calculado_com_juros = calculando_juros_carencia(saldo_devedor_operacao, juros, carencia)

        saldo_devedor = saldo_calculado_com_juros
        num_parcelas_clientes = 0

        amortizacao_calculo = saldo_devedor / num_parcelas

        num_parcelas_clientes = 0
        indice = 0
        indice_um = 0

        primeira_iteracao = True
        primeira_iteracao_dois = True
        juros_cliente = 0  # Inicializa o valor dos juros para a primeira linha

        while True:
            if num_parcelas_clientes < carencia:
                # Exibe a linha atual com saldo e juros calculados anteriormente

                if primeira_iteracao:
                    primeira_iteracao = False
                    exibicao_saldo_devedor_operacao = round(saldo_devedor_operacao, 2)
                    rowValue = Linha(num_parcelas_clientes, exibicao_saldo_devedor_operacao, 0, 0, 0 , 0, 0)
                    dados_amortizacao.append(0)
                    dados_retorno.append(rowValue.to_dict())

                else:
                    exibicao_saldo_devedor_operacao = round(saldo_devedor_operacao, 2)
                    exibicao_juros = round(juros_cliente, 2)

                    rowValue = Linha(num_parcelas_clientes, exibicao_saldo_devedor_operacao, exibicao_juros, 0, 0 , 0, 0)
                    dados_retorno.append(rowValue.to_dict())
                    dados_amortizacao.append(0)

                    # print(f"{saldo_devedor_operacao:.2f}", f"{juros_cliente:.2f}", 0, 0, 0, 0, 0)

                # Calcula os juros para o saldo atual (que será exibido na próxima linha)
                juros_cliente = calculando_juros(saldo_devedor_operacao, juros, num_parcelas)
                
                # Atualiza o saldo para a próxima iteração
                saldo_devedor_operacao += juros_cliente
                num_parcelas_clientes += 1
                indice += 1
            else:
                juros_calculado = calculando_juros(saldo_devedor,juros, num_parcelas) # Calculando o juros do "empréstimo"
                subtracao_calculo = subtraindo_total(amortizacao_calculo, saldo_devedor) # subtraindo o valor amortizado do saldo devedor.
                seguro_prestamista_calculado = seguro_prestamista(0.035, saldo_devedor)

                saldo_devedor = subtracao_calculo # o Saldo devedor agora irá receber essa subtração.
                
                parcela_normal = juros_calculado + amortizacao_calculo

                somando_taxas = seguro_prestamista_calculado + Taxa_administracao + seguro_dfi

                parcela_final = seguro_prestamista_calculado + Taxa_administracao + seguro_dfi + parcela_normal

                exibicao_saldo_devedor = round(saldo_devedor, 2)
                exibicao_amortizacao = round(amortizacao_calculo, 2)

                exibicao_juros = round(juros_calculado, 2)
                exibicao_prestamista = round(seguro_prestamista_calculado, 2)
                exibicao_parcela = round(parcela_final, 2)
                exibicao_parcela_normal = round(parcela_normal, 2)
                exibicao_taxas = round(somando_taxas, 2)

                rowValue = Linha(num_parcelas_clientes, exibicao_saldo_devedor, exibicao_juros, exibicao_amortizacao, exibicao_parcela_normal, exibicao_taxas, exibicao_parcela)
                dados_amortizacao.append(exibicao_amortizacao)

                dados_retorno.append(rowValue.to_dict())
                parcela_final = 0

                num_parcelas_clientes = num_parcelas_clientes + 1 # Aqui começo a contagem das parcelas a partir do 0, por tanto irei incrementa-la até ser igual ao que o cliente solicitou.

                if(num_parcelas_clientes >= num_parcelas + carencia): # condição para o break do loop.
                    break

    return dados_retorno


@app.route('/simulacao', methods=['POST'])
def simulador():

    data = request.json # acessando o corpo.

    dados_retorno = []

    vlr_imovel = float(data.get('vlr_imovel'))
    vlr_solicitado = float(data.get('valor_solicitado'))
    juros = float(data.get('juros'))
    num_parcelas = int(data.get('numero_parcelas'))
    carencia = int(data.get('carencia'))
    tipo_amortizacao = data.get('amortizacao')

    if not all([vlr_imovel, vlr_solicitado, juros, num_parcelas, carencia]):
        return jsonify({"message": "Dados incompletos recebidos"}), 400

    if tipo_amortizacao == 'SAC':
        dados_retorno = calculando_emprestimo_final_SAC(vlr_imovel, vlr_solicitado, juros, num_parcelas, carencia)
    if tipo_amortizacao == 'PRICE':
        dados_retorno = calculando_emprestimo_final(vlr_imovel, vlr_solicitado, juros, num_parcelas, carencia)

    parcelas = []

    saldo_inicial = 0

    for value in dados_retorno:
        if value['parcela'][0] == 0:
            saldo_inicial = value['saldo_devedor'][0]
        if value['parcela_final'][0] != 0:
            parcelas.append(value['parcela_final'][0])
        else:
            continue
    
    # calculando CET 
    dados_CET =  montando_tabela_CET(saldo_inicial, carencia, parcelas)
    # calculando juros a.a
    dados_juros = juros_a_a(juros)

    infos_emprestimo = {
        'Valor_do_credito' : saldo_inicial,
        'Valor_liberado' : vlr_solicitado,
        'Prazo' : num_parcelas,
        'Carencia' : f'0{carencia}',
        'Valor_garantia' : vlr_imovel,
        'infos_juros' : dados_juros,
        'ipca': 'IPCA retroativo 2 meses',
        'Seguro_prestamista': '0,035%',
        'Seguro_DFI' : '0,014%',
        'infos_CET': dados_CET
    }

    return jsonify({
        "parcelas": dados_retorno,
        "tamanho" : num_parcelas + carencia,
        "infos_gerais" : infos_emprestimo
    }), 200

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=4223, debug=True)

if __name__ == '__main__':
    app.run(debug=True)

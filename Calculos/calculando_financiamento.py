
import csv # Usada para abrir o csv e capturar os valores dentro do arquivo.
from datetime import date # uso ela para capturar a data atual.
from dateutil.relativedelta import relativedelta # Uso essa função cujo o objetivo é facilitar o calculos de data, para assim calcular o IOF diário da operação.
import numpy_financial as np # Framewokr que ajuda em cálculos financeiros.


data_atual = date.today()

# Função que irá gerar o cálculo somando o valor solicitado, mais todas as custas da opração.
# levando em consideração o valor padrão praticado de 400.000 de imóvel, e 105.000 solicitando, independente da amortização/carência, ele irá resultar em 114.056,40 por exemplo.
def calculando_financiamento(valor_imovel, valor_solicitado, IOF):

        # Aqui é onde iremos levar o IOF da operação em consideração, como o loop é chamado mais vezes, na primeira instância do IOF ele é sempre 0
        iof_calculado = IOF
        Tarifa_de_cadastro =  316.00 # Valor padrão
        Taxa_de_Engenharia =  518.43 # Valor padrão
        Taxa_de_analise_juridica =  19.84 # Valor padrão
        Custo_certidao =  71.37 # Valor padrão
        Taxa_estruturacao = 0.06 * valor_solicitado # Valor padrão levando em considerção o valor_solicitado.

        # Custas_cartorio
        valor_fixo_custas = 295.90 # Valor fixo levado em consideração das custas Cartório.
        valor_consultado_antes = 0 # Irá receber o valor das custas de cartório depois da primeira consulta
        valor_consultado_depois = 0 # Após smar a primeira consulta com a segunda, eu irei somar valor_consultado_antes + valor_antes_cartorio, e verificar se o valor irá mudar de faixa.

        # Aqui realizo a soma de todos os custo da operação, sem somar o valor calculado no cartório.
        valor_antes_cartorio = iof_calculado + Tarifa_de_cadastro + Taxa_de_Engenharia + Taxa_de_analise_juridica + Taxa_estruturacao + Custo_certidao + valor_solicitado

        # Fazendo consulta antes do cartorio.
        with open('nova_tabela.csv', newline='') as csvfile:
            csvfile_list = csv.reader(csvfile) # abrindo o arquivo CSV que contém os valores referentes as custas cartório.
            for row in csvfile_list:
                if 'A' in row[2]: # Aqui sempre encontro valores que não são números, por conta da estrutura do CSV, sendo assim eu coloco uma condição para evitar o erro.
                    continue
                else: 
                    valor_min = float(row[1]) # Pego o valor mínimo, do documento, pois assim irei comparar os valores.
                    valor_max = float(row[2]) # pego o valor máximo, do documento, pois assim irei comparar os valores.
                    if(valor_antes_cartorio > valor_min and valor_antes_cartorio < valor_max): # Aqui faço a verificação se caso o valor calculando antes do cartório está dentro deste range, faço isso até encontrar onde irá está inserido o valor calculando antes do cartório dentro desta faixa.
                        valor_consultado_antes = float(row[-1])  # Quando eu encontrar a faixa do valor, iré pegar a última linha referente a esta faixa e usa-la no cálculo
                        break;

        Custas_cartorio = valor_fixo_custas + (1+0.11) * valor_consultado_antes # Definindo as custas cartório usando o valor capturado da consulta

        # Somando os valores das custa de cartório no valor financiado final.
        valor_financiado_final = iof_calculado + Tarifa_de_cadastro + Taxa_de_Engenharia + Taxa_de_analise_juridica + Taxa_estruturacao + Custas_cartorio + Custo_certidao + valor_solicitado
        
        # Atribuindo o valor pós cartório, na variável para realizar a comparação com o valor de antes do cartório.
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
        
        # Caso ele encontrar o valor e o mesmo for diferente da primeira consulta, ele irá somar a diferença desses valores.
        if(valor_consultado_antes != valor_consultado_depois and valor_consultado_depois != 0):
            extraindo_diferenca = valor_consultado_depois - valor_consultado_antes # pegando a diferença entre as duas consultas realizadas.

            valor_financiado_final = valor_financiado_final + extraindo_diferenca # Somando os valores.

        valor_financiado_final = round(valor_financiado_final, 4)

        return valor_financiado_final # Após toda essa validação, irei retornar o valor do empréstimo final, o qual será usado para calcular a carência e etc...

# Função usada para calcular o IOF da operação.
def calculando_IOF_loop_SAC(vlr_calculado, juros, num_parcelas):   
    
    saldo_devedor = vlr_calculado # O saldo devedor sempre irá receber o valor calculado.
    amortizacao_calculo = vlr_calculado / num_parcelas # Calculando a Amortização da SAC, onde simplesmente divido o vlr_calculado ( saldo devedor ) pelo numero de parcelas.

    # Crio uma variável para realizar a sua incrementação, com o objetivo de controlar o loop lá em baixo.
    num_parcelas_clientes = 0 # Numero de parcelas solicitada pelo cliente.

    array_parcelas = [] # Este array irá receber as parcelas calculadas da operação, pois com elas irei usar para se retirar a amortização.
    array_infos = [] # Este array irá armazenar as informações dos dados, para asism realizar o seu cálculo.

    while True:
        juros_calculado = calculando_juros(saldo_devedor,juros, num_parcelas) # Calculando o juros do "empréstimo"
        subtracao_calculo = subtraindo_total(amortizacao_calculo, saldo_devedor) # subtraindo o valor amortizado do saldo devedor.

        saldo_devedor = subtracao_calculo # Atribuindo a subtração realizada na função logo a cima.

        num_parcelas_clientes = num_parcelas_clientes + 1 # Aqui começo a contagem das parcelas a partir do 0, por tanto irei incrementa-la até ser igual ao que o cliente solicitou.
        
        parcela_calculada = juros_calculado + amortizacao_calculo # A parcela calculada da SAC ( ainda não é a parcela final ) sempre será o juros calculado + amortização da operação calculada.

        array_parcelas.append(parcela_calculada) # Adicionando a parcela no array, pois com essas parcelas irei realizar a conta que irá me entregar o juros diario da operação sobre cada parcela calculada.

        if(num_parcelas_clientes >= num_parcelas): # condição para o break do loop.
            break
    
    IOF_calculado = infos_iof_SAC(num_parcelas, array_parcelas, array_infos, juros) # Aqui eu monto a tabela para realizar o calculo do IOF e retornar esse valor.

    calculando_iof_adicional = (0.38 * vlr_calculado) / 100 # Calculo do IOF adicional
 
    return IOF_calculado + calculando_iof_adicional # Retorno o calculo do IOF diário e o Adicional somados.

# Realizando o calulo do juros de qualquer oepração, levando em consideração cada parcela, onde ele é chamada em todas.
def calculando_juros(valor_financiado, juros, parcelas):

    valor_calculado = (np.pmt(juros, parcelas, -valor_financiado)) / 100 # com o auxilio da biblioteca np.pmt, eu realizo o calculo de juros padrão.
    valor_calculado = round(valor_calculado, 4) # defino 4 casas decimais para uma maior precisão nos cálculos.

    return valor_calculado # retorno o valor com o juros calculado.

# função de auxilio para se realizar a subtracao total dos valores, onde no caso da SAC/PRICE o subtrator se refere sempre a Amortização.
def subtraindo_total(amortizacao, valor_subtraido):
    saldo_devedor = round((valor_subtraido - amortizacao), 4) # realizando a subtração de forma simples, com 4 casas decimais de precisão.
    return saldo_devedor

# Passando como parametro a matriz que irá receber todas as parcelas calculadas com a amortização da operação especificado na função calculando_IOF_loop_SAC(), sua função é sempre retornar o IOF diário de toda operação ( sem o adicional ainda )
def infos_iof_SAC(num_parcelas, array_parcelas, array_infos, juros):

    # IOF diário da operação que é 0,008219%
    iof_diario = 0.008219 / 100

    parcelas = 0 # Usado para realizar a controle das parcelas do cliente.
    iof_calculado = 0 # Irá receber o IOF da operação calculado.

    # Aqui realizo a multiplicação de cada parcela do array, onde no fim irei somar todos os valores resultantes.
    for value in array_parcelas:
        parcelas += 1 # Incrementando a Parcela antes de realizar a primeira/posteriores calculos.

        data_atual_mais_um_mes = data_atual + relativedelta(months=parcelas) # Aqui estou usando a biblioteca de auxilio para realizar a captura data após 1 mês, sempre levando em considerção a parcela atual do loop.

        dif = data_atual_mais_um_mes - data_atual # Calculando a diferença de dias entre a data atual e a data definida no loop.

        # Regra padrão para calculo do IOF diário de qualquer operação.
        dif_days = 365 if dif.days > 365 else dif.days # Caso a diferencia calculada for maior que 365, ele irá receber 365, caso contrário irá receber o valor definido da subtração mesmo.

        # calculando o VP de cada parcela atual do loop, levando em consideração a parcela, o juros da operação e a qtd de parcela incrementada.
        iof_diario_calculo = calcular_vp_vf_carencia(juros, parcelas, value)

        # Realizo a multiplicação da operação, usando os dias calculados, o iof calculado usando a formula de VP, e a porcentagem do IOF diário da operação.
        calculo_geral = dif_days * iof_diario_calculo * iof_diario

        iof_calculado += calculo_geral # somando todos os valores.

    return iof_calculado

# Usada para realizar o calculo VP padrão presente no excel.
def calcular_vp_vf_carencia(taxa, n_periodos, valor_futuro):
    # Aqui realizo o VP padrão usado pelo excel, assim como usado na planilha de simulação.
    taxa = taxa / 100 # divisão da taxa.
    vp = valor_futuro / (1 + taxa) ** n_periodos # Calculando o VP, levando em consideração todos os parametros.
    vp = round(vp, 2) # fixo duas casas decimais de precisão.
    return vp









# Calculando o financiamento da operação levando em consideração a carência.
def calculando_financiamento_carencia_primeiro_valor(vlr_imovel, valor_solicitado, IOF, carencia, juros):

        # Aqui é onde iremos levar o IOF da operação em consideração, como o loop é chamado mais vezes, na primeira instância da função do IOF ele é sempre 0
        iof_calculado = IOF
        Tarifa_de_cadastro =  316.00 # Valor padrão
        Taxa_de_Engenharia =  518.43 # Valor padrão
        Taxa_de_analise_juridica =  19.84 # Valor padrão
        Custo_certidao =  71.37 # Valor padrão
        Taxa_estruturacao = 0.06 * valor_solicitado # Valor padrão levando em considerção o valor_solicitado.

        # Custas_cartorio
        valor_fixo_custas = 295.90 # Valor fixo levado em consideração das custas Cartório.
        valor_consultado_antes = 0 # Irá receber o valor das custas de cartório depois da primeira consulta
        valor_consultado_depois = 0 # Após smar a primeira consulta com a segunda, eu irei somar valor_consultado_antes + valor_antes_cartorio, e verificar se o valor irá mudar de faixa.

        # Aqui realizo a soma de todos os custo da operação, sem somar o valor calculado no cartório.
        valor_antes_cartorio = iof_calculado + Tarifa_de_cadastro + Taxa_de_Engenharia + Taxa_de_analise_juridica + Taxa_estruturacao + Custo_certidao + valor_solicitado

         # Fazendo consulta antes do cartorio.
        with open('nova_tabela.csv', newline='') as csvfile:
            csvfile_list = csv.reader(csvfile) # abrindo o arquivo CSV que contém os valores referentes as custas cartório.
            for row in csvfile_list:
                if 'A' in row[2]: # Aqui sempre encontro valores que não são números, por conta da estrutura do CSV, sendo assim eu coloco uma condição para evitar o erro.
                    continue
                else: 
                    valor_min = float(row[1]) # Pego o valor mínimo, do documento, pois assim irei comparar os valores.
                    valor_max = float(row[2]) # pego o valor máximo, do documento, pois assim irei comparar os valores.
                    if(valor_antes_cartorio > valor_min and valor_antes_cartorio < valor_max): # Aqui faço a verificação se caso o valor calculando antes do cartório está dentro deste range, faço isso até encontrar onde irá está inserido o valor calculando antes do cartório dentro desta faixa.
                        valor_consultado_antes = float(row[-1])  # Quando eu encontrar a faixa do valor, iré pegar a última linha referente a esta faixa e usa-la no cálculo
                        break   
        
        # Fazendo o calculo da custas do cartorio da operação de acordo com o valor capturado do CSV.
        Custas_cartorio = valor_fixo_custas + (1+0.11) * valor_consultado_antes
        # Somando as custas de cartório no valor do valor financiado final da operação.
        valor_financiado_final = iof_calculado + Tarifa_de_cadastro + Taxa_de_Engenharia + Taxa_de_analise_juridica + Taxa_estruturacao + Custas_cartorio + Custo_certidao + valor_solicitado
        # Atribuindo o valor pós cartório, na variável para realizar a comparação com o valor de antes do cartório.
        valor_apos_cartorio = valor_financiado_final

        # Armazenando o valor financiado da operação antes de realizar a extração do seguro DFI e as taxas durante o periodo de carência,
        # exemplo, caso uma operação dê: 114056,42, eu irei armazenar esse valor na variavel abaixo
        # assim irei alterar esse valor abaixo, sendo assim calculando o seguro DFI + taxas da operação em cima de cada loop.
        # por fim irei somar esse valor das taxas + 114056,42, sendo esse o valor financiado final da operação.
        valor_financiado_final_variado = valor_financiado_final
        
        # Objetivo dessas duas condições é simplesmente pegar o calculo do valor das taxas da operação enquanto ela estiver em carência.
        if carencia == 3:
            seguro_dfi = (vlr_imovel*14) / 100000  # Calculo do seguro DFi
            Taxa_administracao =  40.00 # valor padrão
            Taxa_prestamista = 0.035 # valor padrão.

            # Aqui eu pego as taxas simuladas em cima do valor financiado final.
            for i in range(2):
                # calculando o seguro prestamista.
                seguro_prestamista_calculado = seguro_prestamista(Taxa_prestamista, valor_financiado_final_variado)

                # incrementando a variavel de auxilio para pegar a próxima sequencia de calculos de taxas.
                valor_financiado_final_variado = calculando_juros_carencia_separado(valor_financiado_final, juros, 0)
                
                # Realizo a incrementação de toda o valor no valor_financiado_final.
                valor_financiado_final = valor_financiado_final + seguro_prestamista_calculado + seguro_dfi + Taxa_administracao
        
        if carencia == 2:
            seguro_dfi = (vlr_imovel*14) / 100000 # Calculo do seguro DFi
            Taxa_administracao =  40.00 # valor padrão
            Taxa_prestamista = 0.035 # valor padrão.

            # Aqui eu pego as taxas simuladas em cima do valor financiado final.
            seguro_prestamista_calculado = seguro_prestamista(Taxa_prestamista, valor_financiado_final)

            # Realizo a incrementação de toda o valor no valor_financiado_final.
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

        # Caso ele encontrar o valor e o mesmo for diferente da primeira consulta, ele irá somar a diferença desses valores.
        if(valor_consultado_antes != valor_consultado_depois and valor_consultado_depois != 0):
            extraindo_diferenca = valor_consultado_depois - valor_consultado_antes

            valor_financiado_final = valor_financiado_final + extraindo_diferenca

        valor_financiado_final = round(valor_financiado_final, 4) # retornando o valor financiado de fato de toda a operação.

        return valor_financiado_final

# Nesta função eu uso para tirar o calculo da operação com juros, sua finalidade é simular o valor incrementado com o juros para fazer o calculo das taxas do meses em carência.
def calculando_juros_carencia_separado(saldo_devedor, juros, carencia):

    juros = juros / 100 # pegando o juros.
    
    # salvando o saldo incial pois o valor somado não muda.
    saldo_inicial = saldo_devedor # Armazenando o saldo devedor para usar depois.

    valor_retorno = saldo_devedor*juros # calculando o juros da operação de forma simples e direta.
    
    return saldo_inicial + valor_retorno

# Seguro prestamista é sempre multiplicado usando o saldo devedor presente de toda a operação.
def seguro_prestamista(porcentagem, saldo_devedor):
    retorno = (saldo_devedor * porcentagem) / 100 # realizando calculo padrão.
    retorno = round(retorno, 4)
    return retorno

juros = 1.09
num_parcelas = 180
vlr_imovel = 400000
vlr_solicitado = 105000
carencia = 3

saldo_inicial = calculando_financiamento_carencia_primeiro_valor(vlr_imovel, vlr_solicitado, 0, carencia, juros)

print(saldo_inicial)

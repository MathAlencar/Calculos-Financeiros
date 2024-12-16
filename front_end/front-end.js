const table_infos = document.querySelector('#table_infos')
const calculando = document.querySelector('#calculando')

const form_info_display = document.querySelector('.content-main-block')
const table_info_display = document.querySelector('.content-main-table')
const button_new_simulation = document.querySelector('#new_simulation')

// infos gerias

function procedimentoFormatandoInputs(){
    const inputs = document.querySelectorAll('input'); // Seleciona todos os inputs do tipo text

    inputs.forEach(input => {
    // Adiciona um listener para o evento 'input' (quando o usuário digita)
    input.addEventListener('input', function() {
        if(input.id.match("juros")){
            if(!this.value){
                this.value = `% 0.00`;
            }
            let valor = this.value.replace(/[^0-9]/g, '');
            valor = parseFloat(valor) / 100; // Converte para número decimal (divisão por 100)
            this.value = `${valor.toFixed(2)}`; // Formata o valor para R$ 0,00
        }
        if(!input.id.match("juros") && !input.id.match("nmr_parcelas") && !input.id.match("nmr_carencia")){
            
            if(!this.value){
                this.value = `R$ 0.00`;
            }

            let valor = this.value.replace(/[^0-9]/g, '');
            // valor = parseFloat(valor) / 100; // Converte para número decimal (divisão por 100)
            // this.value = `R$ ${valor.toFixed(2)}`; // Formata o valor para R$ 0,00

            if(valor){
                const valorNumerico = parseFloat(valor) / 100;
                this.value = `R$ ${new Intl.NumberFormat('pt-BR', {
                    style: 'decimal',
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                }).format(valorNumerico)}`
            }
        }
    });
    });

}

function criando_linha(parcelas, saldo_devedor, juros, Amortizacao, parcela_normal, seguros_taxas, parcela_final){
    
    const tr = document.createElement('tr')
    const th = document.createElement('td')
    const td_01_parcelas = document.createElement('td')
    const td_02_saldo_devedor = document.createElement('td')
    const td_03_juros = document.createElement('td')
    const td_04_amortizacao = document.createElement('td')
    const td_05_seguros_taxa = document.createElement('td')
    const td_06_parcelas_final = document.createElement('td')

    th.innerHTML = parcelas
    td_02_saldo_devedor.innerHTML = saldo_devedor
    td_03_juros.innerHTML = juros
    td_04_amortizacao.innerHTML = Amortizacao
    td_01_parcelas.innerHTML = parcela_normal 
    td_05_seguros_taxa.innerHTML = seguros_taxas
    td_06_parcelas_final.innerHTML = parcela_final

    tr.appendChild(th)
    tr.appendChild(td_02_saldo_devedor)
    tr.appendChild(td_03_juros)
    tr.appendChild(td_04_amortizacao)
    tr.appendChild(td_01_parcelas)
    tr.appendChild(td_05_seguros_taxa)
    tr.appendChild(td_06_parcelas_final)

    table_infos.appendChild(tr)
}

function formatandoValores(value){
    const formatandoValor = new Intl.NumberFormat('pt-BR', {
        style: 'decimal',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(value)

    return formatandoValor
}

calculando.addEventListener('click', (e) => {
    e.preventDefault()

    const form = document.querySelector('#formularioValores')
    const formatandoDados = new FormData(form)

    let vlr_imovel = formatandoDados.get('vlr_imovel')
    let vlr_solicitado = formatandoDados.get('vlr_solicitado')
    const juros = formatandoDados.get('juros')
    const nmr_parcelas = formatandoDados.get('nmr_parcelas')
    const nmr_carencia = formatandoDados.get('nmr_carencia')
    const opt_amortizacao = formatandoDados.get('select-option')

    vlr_imovel = ((vlr_imovel.replaceAll('.','')).replaceAll(',','.')).replace(/[^0-9.]/g, '')
    vlr_solicitado = ((vlr_solicitado.replaceAll('.','')).replaceAll(',','.')).replace(/[^0-9.]/g, '')

    // validações

    if(opt_amortizacao == 'Amortização'){
        mostrarAlertaError("Escolha um tipo de amortização.")
        return
    }

    if(nmr_carencia > 3 || nmr_carencia < 1){
        mostrarAlertaError("Escolha entre 1 e 3 no campo carência!")
        return
    }

    if(!vlr_imovel || !vlr_solicitado || !juros || !nmr_carencia || !nmr_parcelas){
        mostrarAlertaError("Por favor preencha todos os campos.")
        return
    }


    const dados = {
        vlr_imovel : vlr_imovel,
        valor_solicitado : vlr_solicitado,
        juros : juros,
        numero_parcelas : nmr_parcelas,
        carencia: nmr_carencia,
        amortizacao: opt_amortizacao
    }

    fetch('http://127.0.0.1:5000/simulacao', {
        method : 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body : JSON.stringify(dados)
    })
    .then ( response => {
        if(!response.ok){
            throw new Error('Erro no envio de dados')
        }

        return response.json()
    })
    .then(data => {

        console.log(data)

        form_info_display.style.display = 'none'
        table_info_display.style.display = 'grid'

        table_infos.innerHTML = ''

        console.log(data.infos_gerais)

        let Valor_do_credito = document.querySelector('#Valor_do_credito')
        let valor_liberado = document.querySelector('#valor_liberado')
        let prazo = document.querySelector('#prazo')
        let value_garantia = document.querySelector('#Valor_garantia')
        let cet = document.querySelector('#CET')
        let Seguro_prestamista = document.querySelector('#Seguro_prestamista')
        let Seguro_DFI = document.querySelector('#Seguro_DFI')
        let infos_juros = document.querySelector('#infos_juros')
        let IPCA = document.querySelector('#IPCA')

        console.log(value_garantia)

        Valor_do_credito.innerHTML = ''
        valor_liberado.innerHTML = ''
        prazo.innerHTML = ''
        value_garantia.innerHTML = ''
        cet.innerHTML = ''
        Seguro_prestamista.innerHTML = ''
        Seguro_DFI.innerHTML = ''
        infos_juros.innerHTML = ''
        IPCA.innerHTML = ''

        let valor_credito = formatandoValores(data.infos_gerais.Valor_do_credito)
        let valor_libera = formatandoValores(data.infos_gerais.Valor_liberado)
        let meses = data.infos_gerais.Prazo
        let carencia = data.infos_gerais.Carencia
        let valor_imovel = formatandoValores(data.infos_gerais.Valor_garantia)
        let juros_mensal = data.infos_gerais.infos_juros.taxa_mensal
        let juros_anual = data.infos_gerais.infos_juros.taxa_anual
        let ipca = data.infos_gerais.ipca
        let prestamista = data.infos_gerais.Seguro_prestamista
        let dfi = data.infos_gerais.Seguro_DFI

        let CET_anual = data.infos_gerais.infos_CET.CET_Anual
        let CET_mensal = data.infos_gerais.infos_CET.tir_mensal_CET

        Valor_do_credito.innerHTML = `R$ ${valor_credito}`
        valor_liberado.innerHTML = `R$ ${valor_libera}`
        prazo.innerHTML = `${meses} meses | carência : ${carencia} meses`
        value_garantia.innerHTML = `R$ ${valor_imovel}`
        Seguro_prestamista.innerHTML = `${prestamista}`
        Seguro_DFI.innerHTML = `${dfi}`
        infos_juros.innerHTML = `${juros_mensal}% a.m | ${juros_anual}% a.a`
        IPCA.innerHTML = ipca

        cet.innerHTML = `${CET_mensal}% a.m | ${CET_anual}% a.a`

        for(let i=0; i<data.tamanho; i++){
            // parcelas, saldo_devedor, juros, Amortizacao, parcela_normal, seguros_taxas, parcela_final
            
            let saldo_devedor = formatandoValores(data.parcelas[i].saldo_devedor[0])
            let juros = formatandoValores(data.parcelas[i].juros[0])
            let amortizacao = formatandoValores(data.parcelas[i].amortizacao[0])
            let parcela_normal = formatandoValores(data.parcelas[i].parcela_normal[0])
            let seguros_taxa = formatandoValores(data.parcelas[i].seguros_taxa[0])
            let parcela_final = formatandoValores(data.parcelas[i].parcela_final[0])
            
            if(parcela_final == '0,00'){ 
                criando_linha(data.parcelas[i].parcela[0], `R$ ${saldo_devedor}`, `R$ ${juros}`, `R$ ${amortizacao}`, `R$ ${parcela_normal}`, `R$ ${seguros_taxa}`  , `R$ ${ parcela_final}`)
            }else{
                criando_linha(data.parcelas[i].parcela[0], `R$ ${saldo_devedor}`, `R$ ${juros}`, `R$ ${amortizacao}`, `R$ ${parcela_normal}`, `R$ ${seguros_taxa}`  , `R$ ${ parcela_final} + <p id="ipca">IPCA</p>`)
            }

            console.log(data.parcelas[i].parcela[0], saldo_devedor, juros, amortizacao, parcela_normal, seguros_taxa  , parcela_final)

        }

    })  
    .catch(error => {
        console.log(error)
    })
})

button_new_simulation.addEventListener('click', (e) => {
    e.preventDefault();

    form_info_display.style.display = 'grid'
    table_info_display.style.display = 'none'
})

function mostrarAlertaSucesso(mensagem) {
    alertify.success(mensagem);
}

function mostrarAlertaError(mensagem) {
    alertify.error(mensagem);
}

procedimentoFormatandoInputs()

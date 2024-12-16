# Calculos-Financeiros
O código está parcialmente comentando
Separei ele em duas sessões, a primeira se chama: calculos_api.py
Nele está a API que ao ligada, irá realizar o retorno de dados da simulação enviada no front-end.
Esse será o link padrão de chamada: http://127.0.0.1:5000/simulacao
Já no arquivo, calculo_exibicao_simples.py
Lá eu iniciei a documentação do código e todos os cálculos, ainda não está finalizado até o momento pois a documentação dele iniciei somente
no domingo. ainda preciso documentar os cálculos referentes a PRICE com e sem carência.

No momento está documentado apenas a SAC e parcialmente a SAC com carência.

Deixei o cálculo da CET separado dos demais, por ser um cálculo padrão matemático, tive que buscar na internet um exemplo de código que o realizasse e reescreve-lo em python.

Para iniciar os testes em ambos os códigos, é necessário executar este comando no terminal:
pip install flask flask-cors pandas numpy-financial python-dateutil
Assim ele irá instalar todas as bibliotecas necessárias para se realizar o cálculo.


Caso tenha interesse de ver o front-end, ele está disponível no seguinte link de acesso interno: http://192.168.1.224:6565/
Na infranet da Construtora Stefani.

Ou preferir visualizar ele de forma direta, onde será necessário inicializar o projeto
npm init -y
e após isso executar esse comando para instalar uma única bilbioteca que uso: npm install alertifyjs

Lembre-se de ligar a API, executando esse comando no terminal:

python calculo_api.py




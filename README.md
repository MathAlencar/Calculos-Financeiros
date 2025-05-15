Funcionalidades Principais
Cálculo detalhado do cronograma de pagamento com base nos parâmetros informados (valor, prazo, taxa de juros, tipo de sistema).

Geração de tabelas de amortização mês a mês.

Exportação de dados em formatos estruturados (CSV, JSON).

API construída com Flask, possibilitando fácil integração com sistemas web ou aplicações frontend.

Suporte a requisições cross-origin com Flask-CORS.

Principais Bibliotecas Utilizadas

Flask – Framework para criação da API RESTful.
Flask-CORS – Suporte a CORS para integrações com aplicações externas.
pandas – Manipulação e organização de dados em tabelas.
numpy_financial – Realização de cálculos financeiros como PMT (prestação fixa), juros compostos, entre outros.
csv – Exportação dos dados em arquivos tabulares.
dateutil.relativedelta – Cálculo preciso de datas em intervalos mensais.
math – Cálculos matemáticos adicionais para apoio aos algoritmos.

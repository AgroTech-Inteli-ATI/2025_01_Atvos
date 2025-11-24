1. Visão Geral

  O Agro-Server é um backend construído com Django, projetado para gerenciar e processar dados de viagens. Seu principal componente é um pipeline de ETL (Extração, Transformação e
  Carga) que coleta dados do ambiente local, os processa e os carrega no Google BigQuery para análise.

  Este documento serve como um guia completo para configurar, executar e entender a arquitetura do projeto.

  2. Estrutura do Projeto

  Entender a organização dos arquivos é fundamental para trabalhar no projeto:

    1 /
    2 ├── api/                  # App Django principal
    3 │   ├── migrations/       # Migrações do banco de dados
    4 │   ├── management/       # Comandos de gerenciamento customizados
    5 │   │   └── commands/
    6 │   │       └── run_etl.py  # Orquestrador do pipeline ETL
    7 │   ├── models.py         # Modelos de dados do Django (ex: Viagem)
    8 │   ├── settings.py       # Configurações do Django
    9 │   └── urls.py           # Rotas da API
   10 ├── clients/              # Clientes para serviços externos
   11 │   ├── __init__.py       # Inicializa e exporta os clientes
   12 │   ├── bigquery_client.py# Cliente para interagir com o Google BigQuery
   13 │   ├── storage_client.py # Cliente para interagir com o Google Cloud Storage
   14 │   └── etl/              # Módulos específicos do ETL
   15 │       ├── extractor.py    # Lógica de extração de dados
   16 │       ├── transformer.py  # Lógica de transformação de dados
   17 │       ├── loader.py       # Lógica de carregamento de dados
   18 │       └── auditor.py      # Lógica de auditoria dos dados
   19 ├── logs/                 # Diretório para arquivos de log
   20 │   └── etl.log           # Log das execuções do ETL
   21 ├── .env                  # Arquivo para variáveis de ambiente (NÃO versionado)
   22 ├── manage.py             # Utilitário de linha de comando do Django
   23 └── requirements.txt      # Lista de dependências Python

  3. Configuração do Ambiente de Desenvolvimento

  Siga estes passos para configurar o ambiente localmente.

  3.1. Pré-requisitos

   - Python 3.10 ou superior.
   - Acesso a um projeto no Google Cloud com BigQuery e Cloud Storage ativados.
   - Uma conta de serviço do Google Cloud com permissões de acesso (BigQuery Data Editor, Storage Object Admin) e o arquivo de credenciais JSON.

  3.2. Ambiente Virtual (venv)

  É uma boa prática isolar as dependências do projeto.

   1. Crie o ambiente virtual:
      No diretório raiz do projeto, execute:
   1     python3 -m venv .venv

   2. Ative o ambiente virtual:
       - No Linux/macOS:
   1         source .venv/bin/activate
       - No Windows:
   1         .venv\Scripts\activate
      Após a ativação, seu terminal deve exibir (.venv) no início da linha.

  3.3. Instalação de Dependências

  Com o ambiente virtual ativado, instale todas as bibliotecas necessárias:

   1 pip install -r requirements.txt

  3.4. Variáveis de Ambiente (.env)

  Crie um arquivo chamado .env na raiz do projeto. Este arquivo armazena configurações sensíveis e específicas do seu ambiente.

  Conteúdo do arquivo `.env`:

    1 # Credenciais do Google Cloud
    2 # Caminho absoluto para o arquivo JSON da sua conta de serviço.
    3 GOOGLE_APPLICATION_CREDENTIALS="/caminho/completo/para/seu/arquivo-de-credenciais.json"
    4 
    5 # Configurações do Django
    6 SECRET_KEY="gere-uma-chave-aleatoria-e-forte-aqui"
    7 DEBUG=True
    8 
    9 # Configurações do Google Cloud
   10 BIGQUERY_PROJECT_ID="seu-id-de-projeto-no-gcp"
   11 BIGQUERY_DATASET_NAME="nome_do_seu_dataset_no_bigquery"
   12 CLOUD_STORAGE_BUCKET="nome_do_seu_bucket_no_gcs"

  Detalhes das variáveis:

   - GOOGLE_APPLICATION_CREDENTIALS: O caminho absoluto para o arquivo JSON que você baixou ao criar uma conta de serviço no Google Cloud.
   - SECRET_KEY: Uma chave secreta para segurança do Django. Você pode gerar uma online ou usar uma string longa e aleatória.
   - DEBUG: True para ambiente de desenvolvimento (mostra erros detalhados) e False para produção.
   - BIGQUERY_PROJECT_ID: O ID do seu projeto no Google Cloud Platform.
   - BIGQUERY_DATASET_NAME: O nome do dataset (conjunto de dados) no BigQuery onde a tabela viagens_cleaned será criada.
   - CLOUD_STORAGE_BUCKET: O nome do bucket no Google Cloud Storage que será usado como área de preparação (staging) para os arquivos CSV.

  3.5. Migrações do Banco de Dados

  O projeto usa um banco de dados SQLite local para armazenar os dados antes do ETL. Para criar as tabelas necessárias, execute:

   1 # Cria os arquivos de migração a partir dos modelos
   2 python3 manage.py makemigrations api
   3 
   4 # Aplica as migrações ao banco de dados
   5 python3 manage.py migrate

  4. Executando o Pipeline ETL

  O coração do projeto é o comando run_etl.

  4.1. Como Executar

  Para iniciar o pipeline completo, execute o seguinte comando no seu terminal (com o venv ativado):

   1 python3 manage.py run_etl

  O comando irá executar todas as etapas do ETL em sequência e registrará o progresso no terminal e no arquivo logs/etl.log.

  4.2. Funcionamento Detalhado do ETL

  O pipeline é orquestrado pelo arquivo api/management/commands/run_etl.py e dividido em quatro etapas principais:

  Etapa 1: Extração (`clients/etl/extractor.py`)

   - O que faz? Coleta todos os registros do modelo Viagem do banco de dados local (SQLite).
   - Como faz? Usa a função apps.get_model('api', 'Viagem') do Django para acessar o modelo dinamicamente e, em seguida, converte o QuerySet de viagens em um DataFrame do pandas.
   - Saída: Um DataFrame contendo os dados brutos das viagens.

  Etapa 2: Transformação (`clients/etl/transformer.py`)

   - O que faz? Limpa, enriquece e prepara os dados para análise.
   - Como faz? Recebe o DataFrame da etapa de extração e aplica as seguintes transformações:
       1. Remove registros duplicados baseados no id.
       2. Converte as colunas de odômetro para formato numérico.
       3. Calcula a coluna km_variavel (odometro_fim - odometro_inicio).
       4. Calcula a coluna km_esperado (uma estimativa usada para auditoria).
       5. Calcula a coluna custos_consolidados (custos_fixos + custos_variaveis).
       6. Tratamento de Erro: Se o DataFrame de entrada estiver vazio, a função retorna imediatamente para evitar erros nas etapas seguintes.
   - Saída: Um DataFrame transformado e pronto para ser carregado.

  Etapa 3: Carga (`clients/etl/loader.py`)

   - O que faz? Carrega os dados transformados no Google BigQuery.
   - Como faz? O processo é feito em duas fases para otimização:
       1. Upload para o Cloud Storage: O DataFrame transformado é primeiro salvo como um arquivo CSV em um diretório temporário local. Em seguida, esse arquivo é enviado para um bucket no
          Google Cloud Storage. Isso serve como uma área de preparação (staging area).
       2. Carga no BigQuery: A função instrui o BigQuery a importar os dados diretamente do arquivo CSV no Cloud Storage para a tabela viagens_cleaned. A tabela é configurada com
          WRITE_TRUNCATE, o que significa que a cada execução do ETL, a tabela é apagada e recriada com os novos dados.
   - Saída: O URI (caminho) do arquivo CSV no Google Cloud Storage.

  Etapa 4: Auditoria (`clients/etl/auditor.py`)

   - O que faz? Analisa os dados transformados em busca de inconsistências.
   - Como faz?
       1. Calcula a coluna flag_divergencia, que sinaliza (True) se a quilometragem real (km_variavel) diverge mais de 10% da esperada (km_esperado).
       2. Calcula um score de conformidade para cada registro.
       3. Tratamento de Erro: Assim como o transformador, esta função também verifica se o DataFrame está vazio antes de prosseguir.
   - Saída: O DataFrame final, enriquecido com as colunas de auditoria.

  Ao final, o comando run_etl exibe um resumo da execução, incluindo o número de registros processados, inconsistências encontradas e o tempo total. o Servidor Backend

  Embora o foco seja o ETL, o projeto também é um backend Django. Para iniciar o servidor de desenvolvimento:

   1 python3 manage.py runserver

  O servidor estará acessível em http://127.0.0.1:8000/.

  ---
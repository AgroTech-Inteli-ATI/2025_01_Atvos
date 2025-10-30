# 🧩 **Documentação da API – Agro-Server**

## 📘 **Visão Geral**

O **Agro-Server** é uma API desenvolvida em **Django** com o objetivo de oferecer uma interface modularizada para manipulação de dados no **Google BigQuery** e no **Google Cloud Storage**.
A API implementa métodos padronizados para:

* **Inserir** registros
* **Atualizar** registros
* **Remover** registros
* **Fazer download** de arquivos

Essas funcionalidades permitem integrar sistemas agrícolas com infraestrutura em nuvem de forma escalável e segura.

---

## ⚙️ **Arquitetura e Estrutura de Pastas**

```
Agro-Server/
│
├── api/
│   ├── bigquery_views.py      # Endpoints relacionados ao BigQuery
│   ├── storage_views.py       # Endpoints relacionados ao Cloud Storage
│   ├── settings.py            # Configurações do Django (importa variáveis do .env)
│   ├── urls.py                # Definição das rotas da API
│   └── wsgi.py                # Ponto de entrada do servidor Django
│
├── clients/
│   ├── bigquery_client.py     # Cliente responsável por se conectar e manipular dados no BigQuery
│   ├── storage_client.py      # Cliente responsável por se conectar ao Cloud Storage
│   └── key.json               # Credenciais de acesso do Google Cloud
│
├── manage.py                  # Comando administrativo do Django
├── .env                       # Variáveis de ambiente (configurações e chaves)
├── db.sqlite3                 # Banco de dados local do Django
├── requirements.txt           # Dependências do projeto
└── venv/                      # Ambiente virtual Python
```

---

## ☁️ **Serviços Utilizados**

### 🟢 **Google BigQuery**

O **BigQuery** é o *Data Warehouse* do Google Cloud voltado para análises em larga escala.
Ele permite **armazenar e consultar grandes volumes de dados usando SQL**, com alta performance e escalabilidade.

Nesta API, o BigQuery é utilizado para:

* Inserir novos registros em tabelas específicas
* Atualizar registros existentes
* Remover registros
* Executar consultas e retornar dados para o cliente

> O módulo responsável é `clients/bigquery_client.py`
> As rotas estão em `api/bigquery_views.py`

---

### 🟣 **Google Cloud Storage**

O **Cloud Storage** é o serviço de **armazenamento de objetos** (blobs) do Google Cloud.
Permite salvar e gerenciar arquivos como imagens, documentos e dados de backup.

Nesta API, o Cloud Storage é utilizado para:

* Fazer **upload** de arquivos locais para buckets na nuvem
* Fazer **download** de arquivos armazenados
* **Remover** arquivos de buckets

> O módulo responsável é `clients/storage_client.py`
> As rotas estão em `api/storage_views.py`

---

## 🧠 **Rotas Disponíveis**

### 📊 **BigQuery**

| Método HTTP | Endpoint               | Função                            |
| ----------- | ---------------------- | --------------------------------- |
| `POST`      | `/bigquery/inserir/`   | Insere um novo registro na tabela |
| `PUT`       | `/bigquery/atualizar/` | Atualiza dados existentes         |
| `DELETE`    | `/bigquery/remover/`   | Remove um registro da tabela      |
| `GET`       | `/bigquery/download/`  | Exporta dados do BigQuery         |

---

### 📦 **Cloud Storage**

| Método HTTP | Endpoint             | Função                                |
| ----------- | -------------------- | ------------------------------------- |
| `POST`      | `/storage/inserir/`  | Faz upload de um arquivo local        |
| `DELETE`    | `/storage/remover/`  | Remove um arquivo de um bucket        |
| `GET`       | `/storage/download/` | Faz o download de um arquivo da nuvem |

---

## 🔐 **Configurações e Credenciais**

As credenciais de acesso (`key.json`) e as variáveis de ambiente (`.env`) estão disponíveis **no grupo do WhatsApp da ATVOS**.
Esses arquivos devem ser colocados nas seguintes localizações:

```
/Agro-Server/clients/key.json
/Agro-Server/.env
```

O arquivo `.env` contém informações como:

```
GOOGLE_APPLICATION_CREDENTIALS=clients/key.json
BIGQUERY_PROJECT_ID=nome-do-projeto
STORAGE_BUCKET_NAME=nome-do-bucket
DJANGO_SECRET_KEY=chave_django
DEBUG=True
```

---

## 🧩 **Ambiente Virtual (venv)**

O uso do **venv** garante que todas as dependências do projeto fiquem isoladas do sistema operacional.

### 1️⃣ Criar o ambiente virtual

```bash
python -m venv venv
```

### 2️⃣ Ativar o ambiente

* **Linux/macOS:**

  ```bash
  source venv/bin/activate
  ```
* **Windows:**

  ```bash
  venv\Scripts\activate
  ```

### 3️⃣ Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4️⃣ Rodar o servidor Django

```bash
python manage.py runserver
```

---

## 🧠 **Fluxo de Funcionamento**

1. O usuário envia uma requisição HTTP para uma das rotas (`/bigquery/...` ou `/storage/...`).
2. A view correspondente (`bigquery_views.py` ou `storage_views.py`) valida os dados recebidos.
3. A view utiliza o cliente apropriado (`bigquery_client.py` ou `storage_client.py`) para interagir com o Google Cloud.
4. O cliente usa as credenciais em `key.json` e as variáveis do `.env` para autenticar a operação.
5. A resposta (sucesso ou erro) é retornada em formato JSON para o usuário.

---

## 🧾 **Requisitos do Sistema**

* **Python 3.10+**
* **Django 5+**
* **google-cloud-bigquery**
* **google-cloud-storage**
* **python-dotenv**

> Todas as dependências estão listadas no arquivo `requirements.txt`.

---

## ✉️ **Contato**

Em caso de dúvidas sobre configuração ou chaves de acesso, entre em contato pelo grupo da **ATVOS no WhatsApp**, onde estão disponíveis o `.env` e o `key.json`.

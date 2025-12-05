---
sidebar_position: 1
slug: /guia/como-usar
description: "Guia prático para utilizar a solução"
---

# Como Usar a solução

Este guia detalha o processo passo a passo para configurar e executar todos os componentes do projeto em um ambiente de desenvolvimento local.

## 1. Configuração Inicial do Projeto

Siga estes passos para preparar o ambiente e o código-fonte.

### 1.1. Clonagem do Repositório

Abra o terminal e clone o projeto:

```bash
git clone <https://github.com/AgroTech-Inteli-ATI/2025_01_Atvos.git>
cd Agro-Server
```

### 1.2. Configuração das Credenciais

Coloque os arquivos de credenciais nas pastas corretas dentro do diretório `Agro-Server/`:

```
Agro-Server/
├── clients/
│   └── key.json          
└── .env                  
```

**Verificação do `.env`:**

O arquivo `.env` deve conter as variáveis de ambiente necessárias para a conexão com os serviços do Google Cloud e a configuração do Django.

```env
GOOGLE_APPLICATION_CREDENTIALS=clients/key.json
BIGQUERY_PROJECT_ID=seu-projeto-id
STORAGE_BUCKET_NAME=seu-bucket
DJANGO_SECRET_KEY=sua-chave-secreta
DEBUG=True
```

### 1.3. Configuração do Ambiente Python

Crie e ative um ambiente virtual para isolar as dependências do projeto.

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 1.4. Instalação das Dependências Python

Com o ambiente virtual ativado, instale todas as bibliotecas Python necessárias:

```bash
pip install -r requirements.txt
```

## 2. Componente 1: API Django (Backend)

O Django serve como o backend da aplicação, fornecendo a API REST para acesso aos dados do BigQuery e manipulação do Cloud Storage.

### 2.2. Inicialização do Servidor

Inicie o servidor de desenvolvimento do Django:

```bash
python manage.py runserver
```

### 2.3. Teste Rápido da API

Para verificar se a API está respondendo, você pode usar o `curl` em outro terminal:

```bash
curl http://localhost:8000/bigquery/
```

## 3. Componente 2: Streamlit 

O Streamlit é a interface visual para dashboards.

### 3.1. Navegação e Configuração

Navegue até o diretório do Streamlit:

```bash
cd streamlit_app
```

### 3.2. Inicialização do Dashboard

Execute o aplicativo Streamlit:

```bash
streamlit run app.py
```

## 4. Componente 3: Docusaurus (Documentação Técnica)

O Docusaurus hospeda a documentação técnica do projeto.

### 4.1. Navegação e Instalação de Dependências

Navegue até o diretório da documentação e instale as dependências do Node.js:

```bash
cd ../docs
npm install
```

### 4.2. Inicialização da Documentação

Inicie o servidor de desenvolvimento do Docusaurus:

```bash
npm start
```

## 5. Resumo de Comandos para Inicialização

Para iniciar todos os componentes, abra três terminais separados na raiz do projeto (`Agro-Server/`) e execute:

| Terminal | Componente | Comandos |
| :--- | :--- | :--- |
| **Terminal 1** | **API Django** | `source venv/bin/activate` `python manage.py runserver`|
| **Terminal 2** | **Streamlit** | `source venv/bin/activate` `cd streamlit_app` `streamlit run app.py`|
| **Terminal 3** | **Docusaurus** | `cd docusaurus` `npm start`|

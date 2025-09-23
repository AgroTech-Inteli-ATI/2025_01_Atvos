---
sidebar_position: 3
slug: /sprint-1/arquitetura/backend
description: "Especificação da arquitetura do backend"
---

# Arquitetura do Backend

&ensp; Este documento descreve a arquitetura do backend da aplicação, detalhando a tecnologia escolhida, a estrutura do projeto, os processos de processamento de dados e os serviços internos. O objetivo é apresentar como o backend foi projetado para garantir robustez, modularidade, segurança e integração eficiente com bancos de dados, APIs externas e o frontend, assegurando operações consistentes e escaláveis.

## Tecnologia Escolhida

* **Python 3.11+** como linguagem principal.
* **Django Framework** como base do backend, escolhida por sua maturidade, robustez, facilidade de integração com bancos de dados relacionais e suporte a arquitetura em camadas.
* Benefícios do Django:

  * ORM robusto para PostgreSQL (Supabase).
  * Suporte a middlewares e modularidade em apps.
  * Integração com Celery para tarefas assíncronas, caso necessário.
  * Suporte a autenticação, permissões e segurança nativa.


## Estrutura do Projeto

### Organização de Módulos

Arquitetura em camadas para separar responsabilidades:

```
/backend
├─ /apps
│   ├─ /core           # Configurações globais, utilitários e base do projeto
│   ├─ /telemetry      # Consumo de dados de telemetria e processamento
│   ├─ /auditing       # Lógica de auditoria e flags de divergência
│   ├─ /reports        # Geração de relatórios operacionais e financeiros
│   └─ /users          # Autenticação, autorização e perfis de usuários
├─ /config             # Configurações do Django, settings.py, urls.py
├─ /docs               # Documentação automática Swagger/OpenAPI
├─ /scripts            # Scripts auxiliares (migrações, seeds, jobs)
└─ Dockerfile          # Configuração de container para desenvolvimento e produção
```

### Configurações

* **.env** para armazenar credenciais, tokens de API, URLs de bancos e chaves secretas.
* **Settings por ambiente**:

  * `settings/base.py` – configurações comuns.
  * `settings/dev.py` – desenvolvimento.
  * `settings/prod.py` – produção.
* Suporte a **log e monitoramento** para análise de falhas e performance.

### Documentação Automática

* Integração com **drf-yasg** ou **Django REST Framework + OpenAPI/Swagger**.
* Gera documentação interativa e testável das APIs internas e endpoints consumidos pelo frontend.
* Facilita comunicação com equipes de produto e analistas de dados.

### Versionamento

* Controle de versão via **Git**, com branch principal (`main`) e ramificações para funcionalidades (`feature/*`).
* Docker garante consistência do ambiente de desenvolvimento e produção.


## Processamento de Dados

### APIs Externas

* Consumo de **dados de telemetria** via API REST.
* Autenticação com **Bearer Token** ou credenciais seguras armazenadas em `.env`.
* Tratamento de falhas e logs de ingestão.
* Conversão de JSON para **DataFrames pandas** para cálculos e auditoria.

### Bancos de Dados

* **PostgreSQL** hospedado no **Supabase**.
* Estrutura relacional para:

  * Veículos, motoristas, tarifas, turnos, PoIs.
  * Viagens processadas e auditorias.
  * Consolidação de custos fixos e variáveis.
* Django ORM garante migrações consistentes e integridade referencial.

### Serviços

* **Serviços internos em camadas**:

  * `IngestionService` – consumo de APIs e CSV fallback.
  * `CalculationService` – cálculo de km variável, custos e score de auditoria.
  * `ReportingService` – geração de relatórios diários (D-1) e mensais.
* Armazenamento intermediário de DataFrames em **Parquet** no S3 para análise histórica.


## Conclusões
&ensp; A arquitetura do backend, baseada em Django e Python, proporciona uma estrutura modular, segura e escalável, capaz de lidar com ingestão de dados, processamento e geração de relatórios de forma confiável. Com versionamento controlado, documentação automática e serviços internos bem definidos, a solução oferece uma base sólida para desenvolvimento contínuo, manutenção e expansão futura da aplicação.
---
sidebar\_position: 5
slug: /sprint-1/arquitetura/fluxo-ingestao
description: "Especificação do fluxo de ingestão de dados"
---

# Fluxo de Ingestão de Dados

## Introdução

&ensp; Este documento apresenta a especificação do fluxo de ingestão de dados da plataforma, detalhando os mecanismos de aquisição, validação e armazenamento de informações provenientes de APIs externas e uploads manuais. O objetivo é demonstrar como os dados são coletados, tratados e preparados para processamento, garantindo confiabilidade, consistência e disponibilidade para análises operacionais e financeiras.

## Ingestão via API

### Protocolo e Formato

* A plataforma consome dados de telemetria via **API REST** da transportadora.
* Os dados são entregues no formato **JSON**, contendo informações de deslocamento, horários, veículos e motoristas.
* O backend, implementado em Django, faz requisições periódicas para a API, parseando os JSON em **DataFrames pandas** para processamento posterior.

### Autenticação

* A API exige autenticação via **token Bearer**, armazenado de forma segura em variáveis de ambiente do Django.
* O Django utiliza a biblioteca `requests` para incluir o token em cada requisição, garantindo acesso autorizado.

### Rate Limiting

* Como o volume de dados é baixo, a aplicação implementa **intervalos controlados entre requisições** (ex.: polling a cada X minutos) para não exceder limites da API.
* Possível utilização de bibliotecas como `django-ratelimit` para prevenir excesso de chamadas, caso haja múltiplos consumidores ou jobs concorrentes.

### Tratamento de Erros

* O Django registra logs detalhados de falhas de conexão, autenticação ou inconsistência de dados.
* Implementação de **retry automático** para falhas temporárias e alertas via logs ou notificações.

---

## Fallback CSV

### Upload Manual

* Caso a API esteja indisponível, o sistema permite **upload manual de boletins** em CSV ou Excel pela interface web.
* O upload é tratado pelo Django através de **Formulários ou APIs REST internas**, com salvamento temporário para processamento.

### Validação de Formato

* O Django realiza validação do **schema do CSV**, verificando colunas obrigatórias, tipos de dados e consistência.
* Arquivos inválidos são rejeitados e o usuário recebe feedback detalhado sobre erros.

### Processamento

* Dados válidos são convertidos em **DataFrames pandas** para cálculo de km variável, auditoria e consolidação de custos.
* Os DataFrames processados são armazenados em **arquivos Parquet** para análise posterior, mantendo performance e compatibilidade com consultas futuras.

---

## Qualidade dos Dados

### Validações

* Verificação de **valores nulos ou ausentes**, formatos de datas, IDs de veículos e motoristas consistentes.
* Flag de divergência quando os dados da API e CSV diferem do esperado.

### Limpeza

* Remoção de registros duplicados.
* Normalização de campos de texto (ex.: nomes de motoristas, placas de veículos).

---

## Escalabilidade

### Volume de Dados

* Atualmente, o fluxo é **baixo**, mas o Django suporta escalabilidade horizontal e integração com filas (Celery + RabbitMQ/Redis) caso seja necessário processar volumes maiores no futuro.
* Armazenamento em **S3** dos arquivos Parquet garante persistência, versionamento e compatibilidade com ferramentas de análise e BI.
* Django, combinado com **boto3**, permite upload, download e gerenciamento de buckets de forma programática.

---

## Conclusões
&ensp; O fluxo de ingestão foi projetado para assegurar qualidade, integridade e escalabilidade dos dados, combinando automação via API e flexibilidade para uploads manuais. Com validações rigorosas, tratamento de erros e armazenamento eficiente em Parquet no S3, a solução oferece uma base robusta para análises confiáveis, mantendo a capacidade de expansão frente a aumentos de volume ou novos consumidores de dados.

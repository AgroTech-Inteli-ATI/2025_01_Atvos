---
sidebar_position: 1
slug: /sprint-1/arquitetura/visao-geral
description: "Visão geral da arquitetura da solução"
---

# Visão Geral da Arquitetura

&ensp; Este documento apresenta a visão geral da arquitetura da solução desenvolvida, detalhando seus componentes, fluxos de dados, tecnologias adotadas e princípios arquiteturais que orientaram as decisões técnicas. O objetivo é fornecer uma compreensão clara da estrutura do sistema, suas funcionalidades e justificativas para escolhas estratégicas, evidenciando como simplicidade, escalabilidade, manutenibilidade e segurança foram contempladas desde o planejamento.

<p style={{textAlign: 'center'}}>Figura 1 - Visão Geral da Arquitetura</p>

<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("../../../static/img/backend.png").default} style={{width: 800}} alt="Visão Geral da Arquitetura" />
        <br />
    </div>
</div>

<p style={{textAlign: 'center'}}>Fonte: Os autores (2025)</p>

## Arquitetura de Alto Nível

* **Frontend:** Streamlit para dashboards, intereações com os documentos gerados e upload de novos arquivos.
* **Backend:** Django, arquitetura em camadas (apps separados para telemetria, auditoria, relatórios e usuários).
* **Banco de Dados:** PostgreSQL hospedado no Supabase, armazenando dados de veículos, viagens, auditorias e custos.
* **Armazenamento de Arquivos:** S3 para DataFrames Parquet e históricos de dados intermediários.
* **Serviços Auxiliares:** Proxy reverso, processamento e auditoria, monitorados via Prometheus e Grafana.

### Fluxo de Dados

1. Dados de telemetria via API externa são ingeridos pelo backend.
2. CSV/Excel pode ser usado como fallback, enviado manualmente pelo frontend.
3. Dados passam por validação, limpeza, cálculo de km variável e auditoria.
4. Resultados armazenados no PostgreSQL e Parquet no S3.
5. Dashboards Streamlit consomem os dados processados para relatórios D-1 e mensais.

### Tecnologias Escolhidas

* **Python + Django** para backend.
* **Python + Streamlit** para frontend.
* **PostgreSQL (Supabase)** para banco de dados.
* **S3** para armazenamento de arquivos Parquet.
* **Docker / Docker Compose** para consistência de ambiente.
* **Prometheus + Grafana** para monitoramento.
* **Vercel** para deploy com CI/CD integrado ao GitHub.


## Princípios Arquiteturais

### Simplicidade

* Uso de ferramentas que aceleram desenvolvimento (Streamlit, Django).
* Arquitetura em camadas, modular e fácil de compreender.

### Escalabilidade

* Backend e jobs em containers Docker permitem escalabilidade horizontal.
* Armazenamento em S3 facilita volume crescente de dados históricos.
* Pipeline de ingestão pode ser expandido para múltiplas APIs sem mudanças estruturais.

### Manutenibilidade

* Separação de responsabilidades por apps (telemetria, auditoria, relatórios).
* Configurações centralizadas em `.env`.
* Documentação automática Swagger/OpenAPI para APIs.

### Segurança

* Proxy reverso para proteção de containers e portas.
* Variáveis de ambiente para credenciais e tokens.
* Banco e arquivos hospedados em provedores confiáveis (Supabase, AWS S3).


## Decisões Técnicas

### Justificativas

* **Streamlit** escolhido pela simplicidade e foco em dashboards de dados.
* **Django** permite arquitetura estruturada e integração nativa com PostgreSQL.
* **Docker + Docker Compose** garante consistência entre ambientes.
* **Vercel + GitHub CI/CD** simplifica deploy contínuo.

### Trade-offs

* Streamlit limita personalização avançada de frontend, mas reduz complexidade e tempo de desenvolvimento.
* Django é robusto, mas mais pesado que microframeworks simples.

### Alternativas Consideradas

* **Frontend:** React ou Angular, descartados devido à necessidade de maior complexidade e tempo de desenvolvimento.
* **Banco de Dados:** MongoDB ou MySQL, descartados pela necessidade de relações complexas e suporte transacional.
* **Deploy:** AWS ECS ou EC2 para backend, descartados em favor do Vercel para simplicidade no CI/CD e gestão de infraestrutura mínima.

## Conclusões
&ensp; A arquitetura proposta equilibra eficiência, modularidade e segurança, garantindo que a solução seja escalável, fácil de manter e capaz de evoluir conforme novas demandas surgirem. As decisões técnicas adotadas refletem um compromisso com produtividade, consistência de ambiente e integração contínua, proporcionando uma base sólida para desenvolvimento e operação confiável da aplicação.
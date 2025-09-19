---
sidebar_position: 6
slug: /sprint-1/arquitetura/deploy-logs
description: "Estratégia de deploy e sistema de logs"
---

# Deploy e Sistema de Logs

&ensp; Este documento detalha a estratégia de deploy da aplicação e o sistema de logs associado, apresentando práticas de containerização, integração contínua, monitoramento e manutenção. O objetivo é garantir que o ambiente de produção seja seguro, consistente e resiliente, permitindo que a aplicação opere de forma confiável e com mínima intervenção manual.

<p style={{textAlign: 'center'}}>Figura 1 - Arquitetura de Deploy</p>

<div style={{margin: 25}}>
    <div style={{textAlign: 'center'}}>
        <img src={require("../../../static/img/deploy.png").default} style={{width: 800}} alt="Arquitetura de Deploy" />
        <br />
    </div>
</div>

## Estratégia de Deploy

* O sistema será hospedado no **Vercel**, que oferece suporte nativo para aplicações web e APIs.
* O Vercel já provê **CI/CD integrado ao GitHub**, permitindo deploy automático a cada merge na branch principal.
* Aplicações Streamlit/Django serão empacotadas em **Docker**, garantindo consistência entre ambientes de desenvolvimento e produção.

### Containerização

* Todos os serviços (backend, frontend e jobs) estarão em **containers Docker**, permitindo isolamento e replicabilidade.
* **Docker Compose** será utilizado para facilitar o desenvolvimento local e testes integrados, incluindo backend, banco de dados e serviços auxiliares.
* **Proxy reverso** será aplicado para proteção de containers e portas, garantindo que apenas tráfego autorizado alcance os serviços.

### CI/CD Pipeline

* Integração contínua via **GitHub Actions + Vercel**, realizando:

  * Build de imagens Docker.
  * Deploy automático no Vercel após aprovação em branch principal.


## Configuração de Ambiente

### Variáveis de Ambiente

* Credenciais, tokens de API, URLs de bancos e chaves secretas serão armazenadas em **.env**.
* O Vercel permite configuração segura de variáveis de ambiente, acessíveis apenas para o serviço em execução.
* No desenvolvimento local, `.env` será carregado via **python-dotenv** ou similar.

### Configurações por Ambiente

* **Desenvolvimento:** uso de banco local ou sandbox Supabase, logs detalhados.
* **Staging:** integração com APIs reais em modo de teste, monitoramento básico.
* **Produção:** APIs reais, logging reduzido, segurança reforçada com proxy reverso.

## Monitoramento

### Métricas da Aplicação

* **Prometheus** coletará métricas de backend, jobs e consumo de API (latência, throughput, falhas).
* Métricas de uso do frontend e respostas do backend também serão registradas.
* Dashboards interativos no **Grafana** permitirão análise em tempo real e histórico de performance.

### Saúde do Sistema

* Health checks periódicos para backend e jobs, garantindo que serviços críticos estejam operacionais.
* Alertas configuráveis via Grafana/Prometheus para downtime, falhas de ingestão ou divergências críticas.


## Manutenção

### Atualizações

* Atualizações de dependências Python/Django serão testadas em ambiente de staging antes de produção.
* Frontend atualizado automaticamente via deploy do Vercel.

### Patches de Segurança

* Aplicação de patches em containers e imagens Docker regularmente.
* Uso de proxy reverso e controle de portas para proteção adicional.
* Atualização de bibliotecas críticas e monitoramento de vulnerabilidades.

### Backup de Configurações

* Configurações sensíveis (variáveis de ambiente, settings do Django) versionadas e armazenadas de forma segura.
* Banco PostgreSQL hospedado no Supabase possui backup automático configurado, garantindo persistência e recuperação de dados.
* Parquet armazenados no S3 permitem backup de dados intermediários e históricos para análise futura.


## Conclusões
&ensp; A estratégia adotada combina containerização, CI/CD automatizado e monitoramento robusto, assegurando consistência entre ambientes, observabilidade completa do sistema e capacidade de resposta rápida a falhas. Com processos claros de manutenção, patches de segurança e backup de dados e configurações, a solução mantém alta disponibilidade, confiabilidade e segurança para operações contínuas.
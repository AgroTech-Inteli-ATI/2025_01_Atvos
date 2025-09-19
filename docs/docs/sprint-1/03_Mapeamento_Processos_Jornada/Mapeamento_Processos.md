---
sidebar_position: 3
slug: /sprint-1/processos/mapeamento
description: "Mapeamento detalhado dos processos de negócio"
---

# Mapeamento de Processos

Este documento apresenta o mapeamento dos processos e dados relacionados à locomoção de funcionários da Atvos, atualmente realizada por ônibus e mini-vans terceirizadas. O objetivo é demonstrar como o processo manual de marcação dos motoristas pode ser substituído por registros automáticos integrados à telemetria dos veículos.  



## Contexto do Processo

- **Problema atual:** registros manuais em boletins diários e mensais → suscetíveis a erros e inconsistências.  
- **Solução proposta:** captura automática via telemetria (GPS, odômetro, sensores e identificação do motorista).  
- **Benefício esperado:** confiabilidade, redução de retrabalho e integração entre operação e administração.  



## Processo de Ingestão de Dados
Este processo descreve como as informações das viagens são capturadas automaticamente por meio da telemetria e validadas para garantir consistência e qualidade.

### Recebimento Automático via Telemetria
- Motorista inicia viagem → telemetria registra hora inicial, km inicial e local de saída (GPS).  
- Durante a viagem → telemetria captura rota, km rodado e passageiros (sensor/app).  
- Final da viagem → telemetria registra hora final e km final.  

### Validação e Qualidade
- Garantias automáticas: km final ≥ km inicial, rota válida, passageiros ≥ 0.  
- Redução de inconsistências manuais e lacunas nos registros.  



## Processo de Cálculo de Custos
Aqui são definidos os critérios para apuração dos custos de transporte, considerando tanto os quilômetros rodados quanto os valores fixos previstos em contrato.
### Km Variável
- Calculado automaticamente com base nos registros de odômetro e tipo de contrato (fixo ou por km).  

### Custos Fixos
- Tipo de veículo e valores previstos em contrato integrados ao sistema.  

### Consolidação
- Boletins diários geram consolidação mensal automática para área administrativa.  



## Processo de Geração de Relatórios
Esta etapa transforma os dados coletados em boletins diários e relatórios mensais, permitindo análise comparativa, financeira e estratégica.
### Relatórios Diários (Boletim de Mediação)
- Captura automática de dados: hora, km, local, motorista logado, passageiros.  
- Resultado: boletim diário digital, sem preenchimento manual.  

### Relatórios Mensais
- Consolidação de totais, comparação entre planejamento e trajeto real (GPS), custos, rotas e áreas (agrícola/industrial).  
- Resultado: relatório mensal confiável e auditável.  

### Exportações
- Dashboards e relatórios financeiros gerados automaticamente para análise estratégica e auditoria.  



## Processo de Monitoramento
O monitoramento garante o acompanhamento em tempo real das operações, possibilitando rastreamento, alertas automáticos e respostas rápidas a problemas.
### Acompanhamento Operacional
- Rastreamento em tempo real de veículos, motoristas e passageiros.  

### Alertas e Notificações
- Alertas automáticos para inconsistências ou desvios de rota.  

### Escaladas
- Notificações para supervisores em casos de problemas operacionais ou divergências de registro.  



## Processo de Auditoria
A auditoria assegura a integridade do sistema, mantendo trilhas de dados, logs de acesso e controles que reforçam governança e conformidade.
### Trilha de Dados
- Histórico completo das viagens e alterações registradas.  

### Logs do Sistema
- Controle de acesso por perfil (Operação, Financeiro, Admin).  

### Controles
- Conformidade com governança, auditoria e proteção contra fraudes.  




## Fluxograma Geral
O fluxograma a seguir apresenta uma visão consolidada do processo de transporte, desde o início da viagem até a geração de relatórios administrativos e financeiros. Ele evidencia a sequência das etapas, as interações entre sistemas e os pontos críticos de captura de dados, servindo como referência visual para compreender o fluxo completo de informações.
```mermaid
---
config:
    theme: base
    themeVariables:
        primaryColor: "#5B9E79"
---
flowchart TD
    A[Motorista inicia viagem] --> B[Telemetria registra hora inicial, local e km inicial]
    B --> C[Veículo em movimento]
    C --> D[Telemetria registra rota, km rodado e passageiros]
    D --> E[Motorista finaliza viagem]
    E --> F[Telemetria registra hora final e km final]
    F --> G[Boletim diário gerado automaticamente]
    G --> H[Área administrativa recebe consolidação mensal]
    H --> I[Relatório financeiro e auditoria]
    D -.-> J[Obs.: Passageiros podem ser capturados via sensor ou input em app]
```

O fluxograma ilustra de forma clara a sequência operacional, evidenciando como a automação elimina etapas manuais e garante fluidez no registro das viagens. Além disso, a representação gráfica reforça a rastreabilidade do processo, desde a coleta inicial até a geração dos relatórios administrativos e financeiros, destacando pontos de captura crítica e integrações essenciais para auditoria e gestão.
### Visão End-to-End

A visão end-to-end representa o **fluxo completo de dados e processos**, desde o início da viagem até a consolidação dos relatórios financeiros, permitindo identificar pontos críticos e oportunidades de automação.  

No contexto da Atvos:  
1. **Início da viagem:** o motorista inicia a rota, e a telemetria captura automaticamente hora inicial, localização e km inicial.  
2. **Durante a viagem:** o sistema registra trajeto percorrido, km rodado e, quando aplicável, quantidade de passageiros.  
3. **Término da viagem:** a telemetria registra hora final e km final, consolidando o boletim diário de forma automática.  
4. **Consolidação administrativa:** os dados diários são enviados automaticamente para o módulo administrativo, que calcula custos, compara com o contrato, e gera relatórios mensais confiáveis.  

Essa visão permite acompanhar todo o ciclo de ponta a ponta, garantindo **rastreabilidade, precisão e integração entre operação e área administrativa**.



### Pontos de Controle

Para garantir confiabilidade e integridade dos dados, alguns **pontos de controle** devem ser estabelecidos ao longo do processo:

| Etapa                       | Controle Proposto                                      | Objetivo |
|------------------------------|-------------------------------------------------------|----------|
| Coleta de dados do motorista | Verificação automática de inconsistências entre GPS e odômetro | Garantir que os dados capturados refletem a realidade da viagem |
| Registro diário              | Validação de campos obrigatórios (km, horário, veículo) | Reduzir erros ou lacunas nos boletins |
| Consolidação mensal          | Conferência de totais e alertas para desvios >10% | Evitar inconsistências nos relatórios financeiros |
| Auditoria                    | Histórico de alterações e logs de sistema | Rastreabilidade e compliance interno |
| Discrepâncias                | Notificação automática para gestor ou administrativo | Correção rápida de divergências |

A adoção desses pontos de controle fortalece a confiabilidade do processo ao criar uma camada adicional de verificação em cada etapa crítica. Dessa forma, os dados coletados são não apenas automatizados, mas também auditáveis e rastreáveis, reduzindo riscos de inconsistências e aumentando a segurança das informações utilizadas para cálculos, relatórios e tomadas de decisão.


### Integrações

O sistema proposto se integra com diferentes componentes para automatizar o fluxo de dados:

1. **Telemetria do veículo:** captura km, horários e localização em tempo real.  
2. **Sistema de gestão administrativa:** recebe os dados consolidados e calcula custos, totais acumulados e saldos.  
3. **Banco de dados central:** armazena registros diários e históricos de viagens para auditoria e geração de relatórios.  
4. **Interface do gestor/administrativo:** permite visualizar dados em dashboards, exportar relatórios e monitorar desvios em tempo real.  

Essas integrações permitem que o fluxo de informação seja **contínuo, confiável e auditável**, eliminando a necessidade de processos manuais e aumentando a eficiência operacional.

## Conclusão

O mapeamento apresentado demonstra como a automação, por meio da telemetria e da integração com sistemas administrativos, transforma o processo de transporte em um fluxo mais eficiente, confiável e auditável. Ao substituir registros manuais por capturas automáticas, a organização reduz inconsistências, assegura conformidade e fortalece a rastreabilidade de ponta a ponta.
Com pontos de controle bem definidos, relatórios consolidados e integrações estruturadas, o processo passa a oferecer maior suporte à tomada de decisão estratégica, além de contribuir para a transparência operacional e a otimização dos custos. Dessa forma, estabelece-se uma base sólida para a evolução contínua e para o alinhamento entre operação e gestão administrativa.


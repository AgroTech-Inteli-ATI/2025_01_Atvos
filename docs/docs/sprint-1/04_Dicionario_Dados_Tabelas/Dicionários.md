---
sidebar_position: 1
slug: /sprint-1/dados/dicionarios
description: "Descrição dos dados recebidos"
---

# Dicionários de Dados

O dicionário de dados é um documento que descreve, de forma estruturada e padronizada, todos os campos existentes em uma base de dados, planilha ou sistema. Ele funciona como um guia de referência para desenvolvedores, analistas e demais usuários que precisam compreender a função de cada campo, seu tipo de dado, as regras de preenchimento e observações relevantes.

Cada campo do banco ou planilha é descrito a partir dos seguintes atributos:

- Campo → Nome da coluna ou atributo.
- Tipo de coluna → Indica se é categórica (texto/identificação) ou numérica (valores quantitativos).
- Tipo de dado → Define o formato esperado (VarChar, Char, Int, Float, Date, Time, etc.).
- Descrição → Explicação clara sobre o que o campo representa.
- Observação → Observações adicionais, como restrições, dependências ou exemplos de uso.

Link para a planilha de dicionário de dados: [Link](https://docs.google.com/spreadsheets/d/1b4XjvRSDVachYK0rnB1IOxlrB1ynyLhztk7FL5xbvUg/edit?usp=sharing)

## Sumário dos Dicionários

| Nº | Tabela | Descrição |
|----|--------|-----------|
| 01 | [GESTÃO DIÁRIA - TRANSPORTE DE INTEGRANTES](#gestão-diária---transporte-de-integrantes) | Planilha sobre a gestão diária de ocorrências |
| 02 | [KM CAPTURADO PELA TELEMETRIA](#km-capturado-pela-telemetria) | Resume as métricas de quilometragem capturada pela telemetria |
| 03 | [KM DIÁRIO COMPILADO 100](#km-diário-compilado-100) | Tabela de metragem manual digitalizada |
| 04 | [MEDIÇÃO DE KM POR VEÍCULO - ADMINISTRATIVO - INDUSTRIA 100](#medição-de-km-por-veículo---administrativo---industria-100) | Medição de quilômetros por veículo no contexto administrativo/indústria |
| 05 | [MEDIÇÃO DE KM POR VEÍCULO - AGRICOLA](#medição-de-km-por-veículo---agricola) | Medição de quilômetros por veículo no contexto agrícola |
| 06 | [RESUMO DA OPERAÇÃO](#resumo-da-operação) | Consolidação dos principais indicadores da operação |

## GESTÃO DIÁRIA - TRANSPORTE DE INTEGRANTES

A planilha de gestão diária descreve os processos realizados diariamente para a manutenção do sistema de transporte de colaboradores, como manutenções preventivas e corretivas, bem como incidentes, sinistros e ações tomadas.

<div align="center">
<sub>Imagem 01: Gestão diária - transporte de integrantes.</sub>
<img src={require("../../../static/img/dicionario-dados/Dicionário de dados - Case Atvos - Dicionário - GESTÃO DIÁRIA - TRANSPORTE DE INTEGRANTES.jpg").default} alt="Gestão diária - transporte de integrantes" />
<sup>Fonte: Material produzido pela equipe, 2025.</sup>
</div>

## KM CAPTURADO PELA TELEMETRIA

O dicionário de KM Caputado pela Telemetria resume as métricas presentes em todas as tabelas de dados recebidos via API de telemetria em um só lugar.

<div align="center">
<sub>Imagem 02: KM capturado pela telemetria.</sub>
<img src={require("../../../static/img/dicionario-dados/Dicionário de dados - Case Atvos - Dicionário - KM CAPTURADO PELA TELEMETRIA.jpg").default} alt="KM capturado pela telemetria" />
<sup>Fonte: Material produzido pela equipe, 2025.</sup>
</div>

## KM DIÁRIO COMPILADO 100

A tabela de Km Diário Compilado trata sobre todas as atas de regristro de operação dos veículos da CONLOG entre o período de 16/05/2025 até 15/06/2025, englobando desde placa, turno, rotas e horários de funcionamento.

<div align="center">
<sub>Imagem 03: KM diário compilado (100).</sub>
<img src={require("../../../static/img/dicionario-dados/Dicionário de dados - Case Atvos - Dicionário - KM DIÁRIO COMPILADO 100.jpg").default} alt="KM diário compilado (100)" />
<sup>Fonte: Material produzido pela equipe, 2025.</sup>
</div>

## MEDIÇÃO DE KM POR VEÍCULO - ADMINISTRATIVO - INDUSTRIA 100

A tabela de medição de Km por veículo administratito e industrial detalha a quilometragem, custos fixos e variáveis, rotas administrativas, turnos atendidos e faturamento mensal dos veículos que atuam em industriais e urbanos.

<div align="center">
<sub>Imagem 04: Medição de KM por veículo - administrativo/indústria (100).</sub>
<img src={require("../../../static/img/dicionario-dados/Dicionário de dados - Case Atvos - Dicionário - MEDIÇÃO DE KM POR VEÍCULO - ADMINISTRATIVO - INDUSTRIA 100.jpg").default} alt="Medição de KM por veículo - administrativo/indústria (100)" />
<sup>Fonte: Material produzido pela equipe, 2025.</sup>
</div>

## MEDIÇÃO DE KM POR VEÍCULO - AGRICOLA

A tabela de medição de KM por veículo agricola faz o registro da quilometragem percorrida, rotas agrícolas, custos operacionais e regime de transporte, incluindo parcelas e valores mensais de uso do serviço de transporte nos setores agrícola.

<div align="center">
<sub>Imagem 05: Medição de KM por veículo - agrícola.</sub>
<img src={require("../../../static/img/dicionario-dados/Dicionário de dados - Case Atvos - Dicionário - MEDIÇÃO DE KM POR VEÍCULO - AGRICOLA.jpg").default} alt="Medição de KM por veículo - agrícola" />
<sup>Fonte: Material produzido pela equipe, 2025.</sup>
</div>

## Resumo da Operação

A tabela de resumo da operação contem boa parte dos dados das tabelas anteriores, o incremento é a consolidação em um só lugar de todas as operações por unidade, tipo de frota, custos fixos e variáveis, ocupação, quilometragem média mensal e totais anuais, permitindo um olhar geral sobre o quadro da utilização dos serviços de transporte de colaboradores.

<div align="center">
<sub>Imagem 06: Resumo da operação.</sub>
<img src={require("../../../static/img/dicionario-dados/Dicionário de dados - Case Atvos - Dicionário - Resumo da Operação.jpg").default} alt="Resumo da operação" />
<sup>Fonte: Material produzido pela equipe, 2025.</sup>
</div>

## Conclusão

A análise dos dicionários de dados mostra que foi disponibilizado um conjunto de informações estruturadas para o desenvolvimento da solução. Contudo, em diversos casos, há campos vazios e dados faltantes, evidenciando a necessidade de realizar uma etapa de limpeza dos dados durante o processo de desenvolvimento.

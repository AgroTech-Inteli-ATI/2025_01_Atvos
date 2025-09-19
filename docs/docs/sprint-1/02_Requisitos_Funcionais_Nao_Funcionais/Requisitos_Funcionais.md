---
sidebar_position: 1
slug: /sprint-1/requisitos/funcionais
description: "Especificação dos requisitos funcionais do MVP"
---

# Requisitos Funcionais

Os requisitos funcionais descrevem o que o sistema deve fazer. As capacidades e comportamentos necessários para gerar valor ao usuário e ao negócio. Neste documento, cada requisito é identificado por um código único no formato RFxx (por exemplo, RF01), organizado por áreas (ingestão, processamento, relatórios, interface e gestão de dados). Sempre que pertinente, cada requisito traz uma referência aos requisitos não funcionais (RNxx) que impõem métricas, padrões de segurança, desempenho e qualidade associados, garantindo rastreabilidade entre o que é entregue (RF) e como deve operar (RNF).

## Ingestão de Dados

Esta seção descreve como os dados são coletados e validados desde a origem até a entrada no sistema.

### API de Telemetria

A tabela a seguir especifica os requisitos para consumo seguro e transformação dos eventos de telemetria.

| ID   | Requisito                                   | Descrição                                                                 | RNF Relacionados |
|------|---------------------------------------------|---------------------------------------------------------------------------|------------------|
| RF01 | Ingestão via API de Telemetria              | Acessar os dados da API de telemetria e recebê-los com segurança.        | RN24, RN25, RN32, RN45 |
| RF02 | Transformação de eventos em entidades       | Transformar os requests da API em entidades internas do sistema.         | RN37, RN45, RN51 |

### Fallback para Upload CSV

Aqui estão os requisitos para ingestão alternativa por arquivos em formato CSV e suas validações.

| ID   | Requisito                           | Descrição                                                                                 | RNF Relacionados |
|------|-------------------------------------|-------------------------------------------------------------------------------------------|------------------|
| RF03 | Upload autenticado de CSV           | Upload via interface web com autenticação.                                                | RN11, RN20, RN24 |
| RF04 | Formato de arquivo suportado        | CSV UTF-8 com cabeçalho; separador vírgula.                                               | RN62 |
| RF05 | Campos mínimos                      | deviceId, timestamp, tipoVeiculo, odometroKm, custoVariavel, custoFixo, viagemId.         | RN37 |
| RF06 | Validação de cabeçalho e colunas    | Cabeçalho obrigatório e colunas conhecidas.                                               | RN35, RN37 |
| RF07 | Validação de tipos e formatos       | Datas em ISO 8601; números com ponto decimal.                                             | RN38, RN62 |
| RF08 | Ingestão parcial com relatório      | Linhas inválidas geram relatório e não bloqueiam as válidas.                              | RN35, RN47 |
| RF09 | Limites de upload                   | Tamanho máximo 10 MB e até 50 mil linhas por arquivo.                                     | RN30 |
| RF10 | Confirmação pós-upload              | Exibir resumo de linhas aceitas/rejeitadas e link para log.                               | RN47 |

### Validação de Dados

Define regras de consistência e qualidade que devem ser aplicadas antes do processamento.

| ID   | Requisito                              | Descrição                                                                                                  | RNF Relacionados |
|------|----------------------------------------|------------------------------------------------------------------------------------------------------------|------------------|
| RF11 | Integridade de ativos                  | deviceId deve existir no cadastro de ativos ou entrar em fila de pendência para cadastro posterior.       | RN35, RN37 |
| RF12 | Validação de tempo do evento          | timestamp não pode ser futuro > 5 min; tolerância de fora de ordem até 24h.                               | RN25, RN38 |
| RF13 | Domínio de tipo de veículo            | tipoVeiculo ∈ [urbano, agricola].                                                                          | RN37 |
| RF14 | Não-negatividade de métricas          | odometroKm ≥ 0; custoVariavel ≥ 0; custoFixo ≥ 0.                                                          | RN37 |
| RF15 | Deduplicação de eventos               | Duplicado se (deviceId, timestamp, viagemId) repetir; manter o primeiro e logar os demais.                 | RN36, RN47 |
| RF16 | Sinalização de outliers               | Outliers de odômetro (variação negativa ou salto > 2.000 km/dia) devem ser sinalizados para revisão.       | RN51, RN52 |
| RF17 | Eventos sem viagem                    | Eventos sem viagemId são aceitos e marcados como soltos para conciliação posterior.                        | RN37 |

## Processamento e Cálculos

Reúne as regras de cálculo e agregação que produzem indicadores e custos.

### Cálculo de Km Variável

Requisitos para computar distâncias por dia e por mês a partir de eventos válidos.

| ID   | Requisito                      | Descrição                                                                                                        | RNF Relacionados |
|------|--------------------------------|------------------------------------------------------------------------------------------------------------------|------------------|
| RF18 | kmDia                          | kmDia(deviceId, data) = max(0, odometroMax - odometroMin) com eventos válidos do dia.                            | RN37, RN51 |
| RF19 | kmMes                          | kmMes(deviceId, mês) = soma de kmDia no período.                                                                 | RN37 |
| RF20 | kmPrevistoMes                  | Média diária do mês corrente × dias restantes, com ajuste de sazonalidade configurável.                          | RN51 |
| RF21 | kmPlanejadoMes                 | Valor cadastrado em metas/planejamento.                                                                          | RN47 |
| RF22 | Tratamento de regressões       | Odômetro regressivo no dia resulta em 0 e outlier sinalizado.                                                    | RN51, RN52 |
| RF23 | Dados faltantes                | Ausência de dados no dia: assumir 0 e marcar como dado faltante.                                                | RN37 |

### Consolidação de Custos Fixos

Regras para somar e ratear custos de natureza fixa.

| ID   | Requisito                      | Descrição                                                                                  | RNF Relacionados |
|------|--------------------------------|--------------------------------------------------------------------------------------------|------------------|
| RF24 | custoFixoMes                   | Soma das entradas de custoFixo no mês, ou rateio mensal de contratos fixos.               | RN37 |
| RF25 | custoFixoTotalMes              | Agregado por frota no mês.                                                                | RN37 |
| RF26 | Janela de ajustes              | Atualização D-1 e ajustes retroativos permitidos por até 2 meses.                          | RN26, RN27 |

### Consolidação de Custos Variáveis

Regras para apurar custos com base em uso e projeção.

| ID   | Requisito                           | Descrição                                                                                                      | RNF Relacionados |
|------|-------------------------------------|----------------------------------------------------------------------------------------------------------------|------------------|
| RF27 | custoVarAteAgoraMes                 | Soma de custoVariavel até a data atual.                                                                       | RN37 |
| RF28 | custoVarPrevistoMes                 | Média diária × dias do mês com suavização exponencial (α configurável).                                       | RN51 |
| RF29 | custoTotalPrevistoMes               | Composição: custoFixoTotalMes + soma de custoVarPrevistoMes por frota.                                        | RN51 |

## Geração de Relatórios

Define os produtos de informação entregues pelo sistema para apoio à decisão.

### Relatórios D-1 (Diários)

Requisitos de conteúdo, filtros e prazos para a entrega diária.

| ID   | Requisito                   | Descrição                                                                                     | RNF Relacionados |
|------|-----------------------------|-----------------------------------------------------------------------------------------------|------------------|
| RF30 | Conteúdo D-1                | Gasto total do dia, total de viagens, quilometragem do dia (por veículo e consolidado).       | RN51 |
| RF31 | Filtros D-1                 | Data (padrão: ontem), tipo de veículo, centro de custo.                                       | RN01, RN02 |
| RF32 | Entrega e formato D-1       | Disponível até 08:00 BRT; exportação em PDF/CSV.                                              | RN26, RN62 |

### Relatórios Mensais

Requisitos para relatórios consolidados por mês, com prazos e ajustes.

| ID   | Requisito                      | Descrição                                                                                                   | RNF Relacionados |
|------|--------------------------------|-------------------------------------------------------------------------------------------------------------|------------------|
| RF33 | Conteúdo Mensal                | Gasto médio, custo fixo, variável até o momento e previsto; comparativo planejado vs realizado; agrícola. | RN51 |
| RF34 | Filtros Mensais                | Mês/ano, regional/unidade, tipo de veículo.                                                                 | RN01, RN02 |
| RF35 | Entrega Mensal                 | Disponível em D+1; fechamento com ajustes até D+3.                                                          | RN27 |

### Exportação de Dados

Regras para exportação dos conjuntos de dados com seleção e paginação.

| ID   | Requisito                     | Descrição                                                                                | RNF Relacionados |
|------|--------------------------------|------------------------------------------------------------------------------------------|------------------|
| RF36 | Formatos de exportação         | CSV e XLSX dos datasets base (viagens, telemetria, custos).                              | RN62 |
| RF37 | Seleção e intervalo            | Seleção de colunas e intervalo de datas.                                                 | RN62 |
| RF38 | Paginação e notificação        | Paginação para arquivos grandes e notificação quando pronto para download.               | RN28 |

## Interface do Usuário

Abrange a apresentação de informações e interações do usuário.

### Autenticação e Conta

Especifica como usuários entram, criam contas e recuperam acesso.

| ID   | Requisito                 | Descrição                                                                                         | RNF Relacionados |
|------|---------------------------|---------------------------------------------------------------------------------------------------|------------------|
| RF39 | Login corporativo         | Login com e-mail corporativo e senha.                                                             | RN17, RN18, RN19, RN20 |
| RF40 | Registro de conta         | Registro de conta com e-mail corporativo e senha.                                                 | RN17, RN18 |
| RF41 | Política de senha         | Mín. 8 caracteres; minúscula; maiúscula; número; especial (!@#$%&_); ou política ATVOS.          | RN17 |
| RF42 | Recuperação de senha      | Suportar opções: chamado admin, e-mail com provisória, botão de troca, código de recuperação.    | RN19, RN20 |

### Dashboard Principal

Define os indicadores e listas exibidos na página principal.

| ID   | Requisito                          | Descrição                                                                                                               | RNF Relacionados |
|------|------------------------------------|-------------------------------------------------------------------------------------------------------------------------|------------------|
| RF43 | Indicadores gerais no dashboard    | Gasto do dia, gasto médio mensal, custo fixo mensal, custo variável até agora, custo previsto, total de viagens, ativos.| RN01, RN02, RN51 |
| RF44 | Lista de veículos urbanos          | Exibir km atual/planejado/previsto e custos atual/planejado/previsto por veículo urbano.                                | RN01, RN02 |
| RF45 | Lista de veículos agrícolas        | Exibir km atual/previsto e custos atual/previsto por veículo agrícola.                                                 | RN01, RN02 |


### Visualização de Viagens

Lista e detalha viagens com rotas, eventos e custos.

| ID   | Requisito                 | Descrição                                                                                       | RNF Relacionados |
|------|---------------------------|---------------------------------------------------------------------------------------------------|------------------|
| RF46 | Lista de viagens          | Colunas: viagemId, veículo, início, fim, duração, km, custo variável, status.                    | RN01, RN02 |
| RF47 | Detalhe da viagem         | Rota, eventos de telemetria, custos associados, anomalias.                                       | RN01, RN02 |
| RF48 | Ações em viagens          | Exportar, marcar para revisão, adicionar observação.                                             | RN28, RN47 |

### Filtros e Buscas

Regras para consultar e refinar dados no sistema.

| ID   | Requisito                 | Descrição                                                             | RNF Relacionados |
|------|---------------------------|-----------------------------------------------------------------------|------------------|
| RF49 | Filtros                   | Período, tipoVeiculo, veículo, centro de custo, status da viagem.     | RN02 |
| RF50 | Busca                     | Busca por deviceId, placa, viagemId.                                  | RN02 |
| RF51 | Filtros favoritos         | Salvar filtro como favorito por usuário.                               | RN01 |

### Alertas e Notificações

Define avisos operacionais e preferências de envio.

| ID   | Requisito                 | Descrição                                                                                 | RNF Relacionados |
|------|---------------------------|-------------------------------------------------------------------------------------------|------------------|
| RF52 | Alertas de outliers       | Thresholds configuráveis para odômetro e custos.                                          | RN52, RN53 |
| RF53 | Notificações de falhas    | Falhas de ingestão (CSV com erros, API 5xx recorrentes).                                  | RN51, RN52 |
| RF54 | Preferências de usuário   | Canal (e-mail), frequência (imediato/diário) e severidade configuráveis.                  | RN53 |

## Gestão de Dados

Requisitos administrativos para tarifas e rotas.

### Gestão de Tarifas

CRUD de tarifas com campos, histórico e simulação.

| ID   | Requisito                 | Descrição                                                                                             | RNF Relacionados |
|------|---------------------------|-------------------------------------------------------------------------------------------------------|------------------|
| RF55 | CRUD de tarifas           | Criar, ler, atualizar e excluir tarifas por tipo e por tipo de veículo.                               | RN11, RN48 |
| RF56 | Campos de tarifa          | Nome, tipo, base (km/diária/contrato), valor, vigência (início/fim), centro de custo.                 | RN47 |
| RF57 | Versionamento/auditoria  | Histórico de alterações (quem/quando/o quê).                                                          | RN48, RN50 |
| RF58 | Simulação de impacto      | Visualizar impacto estimado no mês corrente antes de publicar.                                        | RN01 |

### Configuração de Rotas

Cadastro, associação e importação de rotas com validações.

| ID   | Requisito                 | Descrição                                                                                           | RNF Relacionados |
|------|---------------------------|-----------------------------------------------------------------------------------------------------|------------------|
| RF59 | Cadastro de rotas         | Cadastrar rotas com pontos de início/fim e quilometragem esperada.                                  | RN47 |
| RF60 | Associação de rotas       | Associar rotas a veículos e/ou centros de custo (opcional).                                         | RN47 |
| RF61 | Validações de rotas       | Quilometragem esperada > 0; evitar duplicatas (mesmo início/fim) com versão distinta.               | RN37 |
| RF62 | Importação de rotas       | Importação CSV em lote com relatório de inconsistências.                                            | RN30, RN47 |

## Conclusão

Este documento consolida o escopo funcional do MVP, organizado por áreas e com identificação única (RFxx) para facilitar a comunicação, o planejamento e a validação. Cada requisito funcional faz referência direta aos requisitos não funcionais (RNxx) que definem métricas operacionais e critérios de qualidade. Para evoluções futuras, recomenda-se:
* Manter a rastreabilidade RF↔RNF ao incluir novos requisitos ou alterar existentes.
* Validar as dependências entre Ingestão, Processamento e Dashboard para garantir consistência dos indicadores.
* Classificar requisitos por fases (MVP, Fase 2) quando necessário e associar critérios de aceite e testes.
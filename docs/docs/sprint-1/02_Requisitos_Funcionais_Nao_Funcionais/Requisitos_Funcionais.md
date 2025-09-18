---
sidebar_position: 1
slug: /sprint-1/requisitos/funcionais
description: "Especificação dos requisitos funcionais do MVP"
---

# Requisitos Funcionais

## Ingestão de Dados

### API de Telemetria

Requisitos:

- Acessar os dados da API de telemetria
- Transformar os requests da API em entidades dentro do sistema

### Fallback para Upload CSV

Requisitos:

- Upload via interface web com autenticação.
- Formato CSV UTF-8 com cabeçalho; separador vírgula.
- Campos mínimos por linha:
	- deviceId, timestamp, tipoVeiculo, odometroKm, custoVariavel, custoFixo, viagemId
- Validações em upload:
	- Cabeçalho obrigatório e colunas conhecidas
	- Datas em ISO 8601; números no formato decimal com ponto
	- Linhas inválidas geram relatório de erros e não bloqueiam as válidas (ingestão parcial)
- Tamanho máximo do arquivo: 10 MB; até 50 mil linhas.
- Confirmação: resumo de linhas aceitas, rejeitadas e link para log.

### Validação de Dados

Regras:

- Integridade:
	- deviceId existente em cadastro de ativos (ou fila de pendências para cadastro posterior)
	- timestamp não pode ser futuro > 5 min; tolerância de fora de ordem até 24h
- Tipagem e domínios:
	- tipoVeiculo  urbano, agricola
	- odometroKm >= 0; custoVariavel >= 0; custoFixo >= 0
- Duplicidade:
	- Considerar duplicado se (deviceId, timestamp, viagemId) repetir; manter o primeiro e descartar os demais, com log
- Qualidade:
	- Outliers de odômetro (variação negativa ou salto > 2.000 km/dia) sinalizados para revisão
	- Eventos sem viagemId são aceitos mas marcados como soltos para posterior conciliação

## Processamento e Cálculos

### Cálculo de Km Variável

Definições e Regras:

- kmDia(deviceId, data) = max(0, odometroMax - odometroMin) considerando eventos válidos do dia.
- kmMes(deviceId, mês) = soma de kmDia no período.
- kmPrevistoMes(deviceId) = tendência baseada na média diária do mês corrente × dias restantes, com ajuste por sazonalidade (parâmetro).
- kmPlanejadoMes(deviceId) = valor cadastrado em metas/planejamento.
- Tratamento:
	- Se odômetro regressivo entre eventos, normalizar para 0 no dia e sinalizar outlier.
	- Ausência de dados no dia: assumir 0 e marcar como dado faltante.

### Consolidação de Custos Fixos

Regras:

- custoFixoMes(deviceId) = soma de entradas custoFixo no mês, ou rateio mensal de contratos fixos (parâmetro).
- custoFixoTotalMes = soma por frota.
- Atualização D-1; ajustes retroativos permitidos por até 2 meses.

### Consolidação de Custos Variáveis

Regras:

- custoVarAteAgoraMes(deviceId) = soma custoVariavel até a data atual.
- custoVarPrevistoMes(deviceId) = (média diária custoVariavel no mês × dias do mês) com suavização exponencial (α configurável) para reduzir efeito de picos.
- custoTotalPrevistoMes = custoFixoTotalMes + soma custoVarPrevistoMes por frota.

## Geração de Relatórios

### Relatórios D-1 (Diários)

Conteúdo:

- Gasto total do dia (frota e por veículo)
- Total de viagens realizadas
- Quilometragem do dia (por veículo e consolidado)

Filtros:

- Data (padrão: ontem), tipo de veículo, centro de custo

Entrega:

- Disponível na UI até 08:00 BRT do dia seguinte
- Exportação PDF/CSV

### Relatórios Mensais

Conteúdo:

- Gasto médio por mês, custo fixo total do mês, custo variável até o momento, custo previsto até o fim do mês
- Comparativo planejado vs realizado (km e custos) por veículo urbano
- Consolidado para veículos agrícolas
Filtros:
- Mês/ano, regional/unidade, tipo de veículo
Entrega:
- Disponível na UI em D+1; fechamento mensal em D+3 com ajustes

### Exportação de Dados

Opções:

- CSV e XLSX dos datasets base (viagens, eventos de telemetria, custos)
- Intervalo de datas e seleção de colunas
- Paginação para arquivos grandes; notificações quando pronto para download

## Interface do Usuário

### Autenticação e Conta

- Login com e-mail corporativo e senha.
- Registro de conta com e-mail corporativo e senha.
- Regras de senha no registro:
	- Mínimo de 8 caracteres
	- Ao menos uma letra minúscula
	- Ao menos uma letra maiúscula
	- Ao menos um número
	- Ao menos um caractere especial (!@#$%&_)
	- Alternativamente, seguir os padrões de governança da ATVOS
- Recuperação de senha (uma ou mais opções):
	- Abertura de chamado para troca por administrador
	- E-mail com senha provisória
	- E-mail com botão para troca de senha
	- E-mail com código de recuperação

### Dashboard Principal

- Indicadores gerais:
	- Gasto total do dia (fonte: Telemetria/CSV; cálculo: soma diária custos variáveis)
	- Gasto médio por mês (fonte: custos históricos; cálculo: média móvel mensal)
	- Custo fixo total do mês (fonte: Gestão de Tarifas; ver Consolidação de Custos Fixos)
	- Custo total variável até o momento do mês (fonte: Telemetria/CSV; ver Consolidação de Custos Variáveis)
	- Custo previsto até o fim do mês (composição: fixo + variável previsto; ver Consolidação)
	- Custo variável previsto do mês (projeção; ver Consolidação de Custos Variáveis)
	- Total de viagens realizadas até o momento (fonte: Visualização de Viagens)
	- Quantidade de veículos ativos (fonte: eventos do mês distintos por deviceId)

- Veículos urbanos (lista):
	- Quilometragem até o momento do mês (ver Cálculo de Km Variável)
	- Quilometragem planejada até o fim do mês (fonte: metas)
	- Quilometragem prevista até o fim do mês (projeção; ver Cálculo de Km Variável)
	- Custo total até o momento do mês (soma fixo + variável realizados)
	- Custo planejado até o fim do mês (fonte: metas)
	- Custo previsto até o fim do mês (composição; ver Consolidação)

- Veículos agrícolas (lista):
	- Quilometragem até o momento do mês (ver Cálculo de Km Variável)
	- Quilometragem prevista até o fim do mês (projeção; ver Cálculo de Km Variável)
	- Custo total até o momento do mês (soma fixo + variável realizados)
	- Custo previsto até o fim do mês (composição; ver Consolidação)


### Visualização de Viagens

Requisitos:

- Lista de viagens com colunas: viagemId, veículo, início, fim, duração, km, custo variável, status.
- Detalhe da viagem: rota, eventos (telemetria), custos associados, anomalias detectadas.
- Ações: exportar viagem, marcar para revisão, adicionar observação.

### Filtros e Buscas

Requisitos:

- Filtros por período, tipoVeiculo, veículo, centro de custo, status da viagem.
- Busca por deviceId, placa, viagemId.
- Salvar filtro como favorito por usuário.

### Alertas e Notificações

Requisitos:

- Alertas de outliers de odômetro e custos (thresholds configuráveis).
- Notificação de falha de ingestão (arquivo CSV com erros, API com 5xx recorrentes).
- Preferências por usuário: canal (e-mail), frequência (imediato, diário), severidade.

## Gestão de Dados

### Gestão de Tarifas

Requisitos:

- CRUD de tarifas por tipo (fixa, variável) e por tipo de veículo (urbano/agricola).
- Campos: nome, tipo, base de cálculo (km, diária, contrato), valor, vigência (início/fim), centro de custo.
- Regras:
	- Versionamento de alterações com histórico e auditoria (quem, quando, o que mudou).
	- Simulação: visualizar impacto estimado no mês corrente antes de publicar.

### Configuração de Rotas

Requisitos:
- Cadastro de rotas padrão com pontos de início/fim e quilometragem esperada.
- Associação opcional a veículos/centros de custo.
- Validações:
	- Quilometragem esperada > 0
	- Rotas duplicadas (mesmo início/fim) devem ter identificador/versão distintos
 - Importação CSV para rotas em lote com relatório de inconsistências
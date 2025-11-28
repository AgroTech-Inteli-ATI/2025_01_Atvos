---
sidebar_position: 2
slug: /sprint-1/requisitos/nao-funcionais
description: "Especificação dos requisitos não funcionais do MVP"
---

# Requisitos Não Funcionais

Os requisitos não funcionais definem como o sistema deve operar. Critérios de qualidade, desempenho, segurança, disponibilidade, governança e experiência do usuário. Eles estabelecem métricas, SLAs/SLOs e políticas que condicionam a implementação dos requisitos funcionais. Neste documento, cada requisito é identificado por um código RNxx (por exemplo, RN01) e está relacionado aos RFs que impacta, garantindo rastreabilidade bidirecional entre o que o produto faz (RF) e sob quais parâmetros de qualidade e operação (RNF).

## Usabilidade

Esta seção define critérios de experiência e ergonomia das interfaces, com metas de desempenho percebido.

### Interface Web

Metas de carregamento, resposta e consistência visual para páginas principais e navegação.

| ID   | Requisito                                   | Métrica/Alvo                                                                                  | RF Relacionados |
|------|---------------------------------------------|-----------------------------------------------------------------------------------------------|-----------------|
| RN01 | Resposta de filtros e interações            | p95 ≤ 1s para ações de filtro nas páginas Dashboard, Viagens e Relatórios (mês corrente), medido por RUM e testes sintéticos em rede 4G/DSL | RF31, RF33, RF43–RF47, RF49–RF51 |
| RN02 | Carregamento e navegação                    | LCP ≤ 2,5s e TTFB ≤ 500ms no carregamento inicial (rede 4G); p95 da navegação lista/detalhe ≤ 2s | RF43–RF47, RF46–RF48 |
| RN03 | Responsividade                              | Suporte desktop ≥ 1366x768; mobile para consulta (sem edição avançada)                        | RF43–RF51 |
| RN04 | Consistência visual                         | 100% das telas principais aderem ao design system; regressão visual ≤ 0,5% vs baseline (visual diff) | RF43–RF47 |


### Experiência do Usuário

Padrões de feedback, legibilidade e comunicação de estado para ações do usuário.

| ID   | Requisito                        | Métrica/Alvo                                                        | RF Relacionados |
|------|----------------------------------|----------------------------------------------------------------------|-----------------|
| RN05 | Feedback de estado               | 100% das ações exibem carregando/sucesso/erro/sem dados              | RF43–RF48, RF36–RF38 |
| RN06 | Frescor de dados visível         | Exibir "Última atualização: dd/MM/yyyy HH:mm:ss BRT (há Xm)" no cabeçalho; cobertura 100% das páginas do Dashboard; autoatualização a cada 120s; botão "Atualizar"; cores por idade: verde ≤ 5 min, amarelo 5–15, vermelho > 15; tooltip com fonte/ETL; anúncio de atualização via aria-live="polite" | RF43 |
| RN07 | Mensagens de erro úteis          | 0 ocorrências de stack trace/segredos no UI; 100% das mensagens exibem código de suporte (formato ERR-####) e X-Request-ID correlacionado | RF03, RF08, RF10, RF38 |

### Acessibilidade

Critérios de inclusão e navegação por teclado com conformidade a padrões reconhecidos.

| ID   | Requisito                         | Métrica/Alvo                                              | RF Relacionados |
|------|-----------------------------------|-----------------------------------------------------------|-----------------|
| RN08 | WCAG 2.1 AA                       | 0 issues críticos/sérios em axe-core; contraste ≥ 4,5:1; navegação por teclado em 100% dos elementos das páginas principais | RF43–RF47, RF46–RF48 |
| RN09 | Alternativos para gráficos        | Textos alternativos/resumos para 100% dos indicadores     | RF43–RF45 |
| RN10 | Alvos de clique                   | ≥ 44×44px e espaçamento adequado                          | RF43–RF47 |

## Segurança

Requisitos para controle de acesso, perfis, autenticação e proteção de dados em trânsito e em repouso.

### Controle de Acesso

Regras de autorização e escopo de dados por perfil e unidade organizacional.

| ID   | Requisito                        | Métrica/Alvo                                           | RF Relacionados |
|------|----------------------------------|--------------------------------------------------------|-----------------|
| RN11 | RBAC por perfis                  | 100% das rotas protegidas por guard/autorização; 0 acessos indevidos nos testes E2E de RBAC; menus/ações ocultos quando sem permissão | RF55–RF58, RF46–RF48, RF36–RF38 |
| RN12 | Menor privilégio                  | Revisão trimestral de permissões e acessos             | RF55–RF58 |
| RN13 | Escopo por centro/unidade         | 0 registros fora do escopo retornados em consultas de amostra (3 perfis × 3 unidades); filtros pré-aplicados por escopo em 100% das páginas | RF31, RF34, RF46 |

### Perfis de Usuário

Definições de permissões por tipo de usuário e limites de acesso.

| ID   | Requisito          | Métrica/Alvo                                                       | RF Relacionados |
|------|--------------------|--------------------------------------------------------------------|-----------------|
| RN14 | Perfil Administrador | Permissões conforme escopo descrito implementadas                 | RF55–RF58, RF59–RF62 |
| RN15 | Perfil Analista      | Leitura completa, exportação, sem gestão de usuários              | RF36–RF38, RF46–RF48 |
| RN16 | Perfil Visualizador  | Leitura de dashboards/viagens/relatórios; sem exportação em massa | RF43–RF47, RF46 |

### Autenticação e Autorização

Políticas de senha, sessão e proteção contra tentativas indevidas e tráfego inseguro.

| ID   | Requisito                    | Métrica/Alvo                                                         | RF Relacionados |
|------|------------------------------|----------------------------------------------------------------------|-----------------|
| RN17 | Política de senhas           | Mín. 8, minúscula, maiúscula, número, especial ou política ATVOS     | RF41 |
| RN18 | Armazenamento de senhas      | Argon2id/bcrypt com sal único; sem logs de senha                     | RF39–RF41 |
| RN19 | Proteção de login            | Bloqueio após 5 falhas/15min; captcha após 3 falhas                  | RF39, RF42 |
| RN20 | Sessão e tokens              | Sessão 30min inatividade, 12h absoluta; JWT ≤ 15min; refresh ≤ 7 dias| RF39–RF42 |
| RN24 | Tráfego seguro               | TLS 1.2+ com HSTS                                                    | RF01–RF02, RF36–RF38, RF39–RF42 |
| RN32 | Rate limiting                | Login/ingestão/exportação com limites (ex.: 600 req/min por device)  | RF01–RF02, RF36–RF38, RF39 |

## Desempenho

Metas de tempo de resposta, processamento, exportação e capacidade sob diferentes cargas.

### Tempo de Processamento

SLOs de atualização de dados, geração de relatórios e exportações.

| ID   | Requisito                      | Métrica/Alvo                                         | RF Relacionados |
|------|--------------------------------|------------------------------------------------------|-----------------|
| RN51 | Frescor de dados no Dashboard  | Dados disponíveis em até 5 min após ingestão         | RF43–RF45 |
| RN26 | SLA Relatórios D-1             | Disponível até 08:00 BRT; reprocessos até 10:00 BRT  | RF30–RF32 |
| RN27 | SLA Relatórios Mensais         | Disponível em D+1; fechamento com ajustes até D+3    | RF33–RF35 |
| RN28 | SLA Exportações                | ≤ 2 min até 100k linhas; acima disso assíncrono      | RF36–RF38, RF48 |

### Capacidade de Dados

Limites de tamanho, taxa de ingestão e tolerância a picos de uso.

| ID   | Requisito                     | Métrica/Alvo                                         | RF Relacionados |
|------|-------------------------------|------------------------------------------------------|-----------------|
| RN30 | Limites de upload             | CSV até 10 MB e 50 mil linhas por arquivo            | RF09, RF62 |
| RN32 | Rate de ingestão              | 600 req/min por device (ajustável)                   | RF01–RF02 |
| RN31 | Tolerância a picos            | 3× carga média por 1h sem degradação severa          | RF43–RF47, RF46–RF48 |

### Disponibilidade

Níveis de serviço, janelas de manutenção e metas de recuperação.

| ID   | Requisito                 | Métrica/Alvo                      | RF Relacionados |
|------|---------------------------|-----------------------------------|-----------------|
| RN29 | SLO de disponibilidade    | 99,5% mensal (≤ 3h36m de indisponibilidade/mês), medido por monitoramento sintético e RUM | RF43–RF47, RF30–RF35 |
| RN33 | Manutenções               | Aviso com ≥ 48h; janelas fora do horário de pico (08:00–18:00 BRT) e com duração ≤ 2h | RF30–RF35 |
| RN34 | RTO/RPO                   | RTO ≤ 4h; RPO ≤ 1h                | RF30–RF35, RF36–RF38 |

## Governança de Dados

Padrões para qualidade, backup, recuperação e retenção de dados.

### Qualidade dos Dados

Validações de integridade, tipagem e padrões de formato antes de cálculos e relatórios.

| ID   | Requisito                     | Métrica/Alvo                                            | RF Relacionados |
|------|-------------------------------|---------------------------------------------------------|-----------------|
| RN35 | Ingestão parcial com relatório| ≥ 95% de aceitação por arquivo; relatório de erros      | RF08, RF10 |
| RN36 | Deduplicação                  | Duplicados < 1% dos eventos processados                 | RF15 |
| RN37 | Tipagem e domínios            | 100% dos registros participando de cálculos aprovados nas validações; registros inválidos excluídos de agregações e reportados com contagem por regra | RF11–RF14, RF18–RF19, RF23–RF29, RF59–RF61 |
| RN38 | Padrões de formatos           | Datas ISO 8601; números com ponto decimal               | RF07, RF12, RF37 |
| RN25 | Clock skew                     | Aceitar timestamps futuros até +5 min; reorder 24h      | RF12 |
| RN51 | Outliers/km e custos          | Regras aplicadas e sinalização em até 5 min             | RF16, RF22 |

### Backup e Recuperação

Frequência de backups, testes de restauração e diretrizes de continuidade do negócio.

| ID   | Requisito             | Métrica/Alvo                                   | RF Relacionados |
|------|-----------------------|------------------------------------------------|-----------------|
| RN39 | Backup                 | Diário completo; incrementais de hora em hora  | RF36–RF38, RF55–RF58 |
| RN40 | Criptografia           | Em repouso e em trânsito                       | RF36–RF38 |
| RN41 | Teste de restauração   | Trimestral                                     | RF36–RF38 |
| RN42 | Procedimentos de DR    | Documentados para parcial e total              | RF30–RF35, RF36–RF38 |

### Retenção de Dados

Prazos para manter dados brutos, agregados, logs e auditorias.

| ID   | Requisito                 | Métrica/Alvo                         | RF Relacionados |
|------|---------------------------|--------------------------------------|-----------------|
| RN43 | Telemetria bruta          | 24 meses                              | RF01–RF02 |
| RN44 | Agregados/indicadores     | 36 meses                              | RF43–RF45 |
| RN50 | Trilha de auditoria       | 12 meses (ou conforme política)       | RF55–RF58 |
| RN46 | Logs de aplicação         | 90 dias                               | RF36–RF38, RF01–RF02 |
| RN28 | Links de exportação       | Expiram em até 7 dias                 | RF36–RF38 |

## Rastreabilidade

Observabilidade, auditoria de ações e monitoramento contínuo do sistema.

### Logs do Sistema

Métricas, correlação e proteção de informações em logs estruturados.

| ID   | Requisito                     | Métrica/Alvo                                        | RF Relacionados |
|------|-------------------------------|-----------------------------------------------------|-----------------|
| RN45 | Observabilidade ingestão      | Correlation-Id e métricas de latência/erros         | RF01–RF02 |
| RN46 | Logs estruturados/mascaramento| JSON; sem segredos/PII; mascaramento e truncamento  | RF36–RF38, RF39–RF42 |
| RN47 | Relatórios de processamento   | Relatório gerado e disponível em até 60s após upload/exportação; inclui contagens de sucesso/falha e amostras de erro | RF08, RF10, RF38 |

### Trilha de Auditoria

Registros de mudanças e eventos de segurança com políticas de integridade.

| ID   | Requisito                 | Métrica/Alvo                                      | RF Relacionados |
|------|---------------------------|---------------------------------------------------|-----------------|
| RN48 | Auditoria de CRUD         | CRUD de usuários/tarifas/rotas/parametrizações    | RF55–RF58, RF59–RF62 |
| RN49 | Eventos de segurança      | Logins, falhas, relatórios e exportações          | RF39–RF42, RF30–RF38 |
| RN50 | Integridade e retenção    | Imutabilidade lógica; retenção ≥ 12 meses         | RF55–RF58 |

### Monitoramento

Checagens de saúde, alertas e notificações com metas de latência e confiabilidade.

| ID   | Requisito                 | Métrica/Alvo                                               | RF Relacionados |
|------|---------------------------|------------------------------------------------------------|-----------------|
| RN51 | Lag de processamento      | ≤ 5 min até refletir no Dashboard                          | RF43–RF45 |
| RN52 | Alertas de outliers       | Thresholds configuráveis; latência de alerta ≤ 5 min       | RF52–RF53 |
| RN53 | Notificações              | E-mail entregue ≤ 5 min; preferências por usuário salvas   | RF54 |
| RN54 | SLOs e alertas            | D-1 atraso > 07:30; 5xx ingestão > 1% em 5 min (alerta)    | RF30–RF32, RF01–RF02 |
| RN55 | Health checks/sintéticos  | Checagens a cada 1 min nas rotas críticas; tempo de resposta p95 ≤ 500ms; falhas consecutivas ≥ 3 disparam alerta | RF01–RF02, RF30–RF38 |

## Compatibilidade

Suporte a navegadores, dispositivos e integrações com padrões de versionamento e paginação.

### Navegadores Suportados

Lista de navegadores suportados e regras de regressão visual.

| ID   | Requisito                 | Métrica/Alvo                                   | RF Relacionados |
|------|---------------------------|-----------------------------------------------|-----------------|
| RN56 | Browsers suportados       | Chrome/Edge/Firefox (2 últimas) e Safari atual | RF43–RF48 |
| RN57 | Navegadores não suportados| Internet Explorer não suportado                | RF43–RF48 |
| RN58 | Regressão visual          | Testes nas páginas principais a cada release   | RF43–RF48 |

### Dispositivos

Sistemas operacionais e resoluções mínimas recomendadas para a melhor experiência.

| ID   | Requisito                 | Métrica/Alvo                          | RF Relacionados |
|------|---------------------------|---------------------------------------|-----------------|
| RN59 | Plataformas                | Windows/macOS/Linux nos navegadores   | RF43–RF48 |
| RN03 | Resolução mínima           | 1366x768 a 1920x1080 (verificado)     | RF43–RF48 |

### Integrações

Regras de coexistência de versões, idempotência e formatos de exportação.

| ID   | Requisito                 | Métrica/Alvo                                                   | RF Relacionados |
|------|---------------------------|----------------------------------------------------------------|-----------------|
| RN60 | Versionamento de APIs     | v1; política de depreciação e coexistência documentadas        | RF01–RF02, RF36–RF38 |
| RN61 | Idempotência              | Header/chave idempotente para replays                          | RF01–RF02 |
| RN62 | Formatos de exportação    | CSV UTF-8 (vírgula), XLSX; datas ISO 8601                      | RF36–RF38, RF07 |
| RN63 | Paginação                  | Padrão de 1000 registros por página (configurável)             | RF36–RF38, RF46 |
| RN64 | Localização                | pt-BR para números/datas; apresentação padrão em BRT           | RF43–RF47 |

## Conclusão

Os requisitos não funcionais estabelecem as condições de qualidade e operação sob as quais os requisitos funcionais devem atuar. As métricas, SLOs/SLAs e políticas aqui descritas (RNxx) devem ser utilizadas como critérios de aceite e de monitoração contínua em produção. Recomenda-se:
- Revisões periódicas das métricas e metas conforme o crescimento de uso e volumetria.
- Alinhar mudanças de RNF com impactos previstos nos RF e comunicar depreciações/versionamentos.
- Garantir que instrumentação (logs, métricas, audit) esteja ativa para comprovar atendimento aos RNF.

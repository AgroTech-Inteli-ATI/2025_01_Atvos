---
sidebar_position: 2
slug: /sprint-1/requisitos/nao-funcionais
description: "Especificação dos requisitos não funcionais do MVP"
---

# Requisitos Não Funcionais

Os requisitos não funcionais definem como o sistema deve operar — critérios de qualidade, desempenho, segurança, disponibilidade, governança e experiência do usuário. Eles estabelecem métricas, SLAs/SLOs e políticas que condicionam a implementação dos requisitos funcionais. Neste documento, cada requisito é identificado por um código RNxx (por exemplo, RN01) e está relacionado aos RFs que impacta, garantindo rastreabilidade bidirecional entre o que o produto faz (RF) e sob quais parâmetros de qualidade e operação (RNF).

## Usabilidade

### Interface Web

| ID   | Requisito                                   | Métrica/Alvo                                                                                  | RF Relacionados |
|------|---------------------------------------------|-----------------------------------------------------------------------------------------------|-----------------|
| RN01 | Resposta de filtros e interações            | ≤ 1s nas páginas Dashboard, Viagens e Relatórios (mês corrente)                               | RF31, RF33, RF43–RF47, RF49–RF51 |
| RN02 | Carregamento e navegação                    | Carregamento inicial ≤ 3s em 4G; navegação lista/detalhe ≤ 2s                                 | RF43–RF47, RF46–RF48 |
| RN03 | Responsividade                              | Suporte desktop ≥ 1366x768; mobile para consulta (sem edição avançada)                        | RF43–RF51 |
| RN04 | Consistência visual                         | Aderência ao design system (cores/tipografia/componentes); 100% das telas principais          | RF43–RF47 |


### Experiência do Usuário

| ID   | Requisito                        | Métrica/Alvo                                                        | RF Relacionados |
|------|----------------------------------|----------------------------------------------------------------------|-----------------|
| RN05 | Feedback de estado               | 100% das ações exibem carregando/sucesso/erro/sem dados              | RF43–RF48, RF36–RF38 |
| RN06 | Frescor de dados visível         | Timestamp da última atualização visível no Dashboard                 | RF43 |
| RN07 | Mensagens de erro úteis          | Erros sem stack/segredos; código de suporte em 100% das mensagens    | RF03, RF08, RF10, RF38 |

### Acessibilidade

| ID   | Requisito                         | Métrica/Alvo                                              | RF Relacionados |
|------|-----------------------------------|-----------------------------------------------------------|-----------------|
| RN08 | WCAG 2.1 AA                       | Conformidade AA nas páginas principais                     | RF43–RF47, RF46–RF48 |
| RN09 | Alternativos para gráficos        | Textos alternativos/resumos para 100% dos indicadores     | RF43–RF45 |
| RN10 | Alvos de clique                   | ≥ 44×44px e espaçamento adequado                          | RF43–RF47 |

## Segurança

### Controle de Acesso

| ID   | Requisito                        | Métrica/Alvo                                           | RF Relacionados |
|------|----------------------------------|--------------------------------------------------------|-----------------|
| RN11 | RBAC por perfis                  | Perfis aplicados a menus/ações/escopo de dados         | RF55–RF58, RF46–RF48, RF36–RF38 |
| RN12 | Menor privilégio                  | Revisão trimestral de permissões e acessos             | RF55–RF58 |
| RN13 | Escopo por centro/unidade         | Filtros e dados respeitam escopo do usuário            | RF31, RF34, RF46 |

### Perfis de Usuário

| ID   | Requisito          | Métrica/Alvo                                                       | RF Relacionados |
|------|--------------------|--------------------------------------------------------------------|-----------------|
| RN14 | Perfil Administrador | Permissões conforme escopo descrito implementadas                 | RF55–RF58, RF59–RF62 |
| RN15 | Perfil Analista      | Leitura completa, exportação, sem gestão de usuários              | RF36–RF38, RF46–RF48 |
| RN16 | Perfil Visualizador  | Leitura de dashboards/viagens/relatórios; sem exportação em massa | RF43–RF47, RF46 |

### Autenticação e Autorização

| ID   | Requisito                    | Métrica/Alvo                                                         | RF Relacionados |
|------|------------------------------|----------------------------------------------------------------------|-----------------|
| RN17 | Política de senhas           | Mín. 8, minúscula, maiúscula, número, especial ou política ATVOS     | RF41 |
| RN18 | Armazenamento de senhas      | Argon2id/bcrypt com sal único; sem logs de senha                     | RF39–RF41 |
| RN19 | Proteção de login            | Bloqueio após 5 falhas/15min; captcha após 3 falhas                  | RF39, RF42 |
| RN20 | Sessão e tokens              | Sessão 30min inatividade, 12h absoluta; JWT ≤ 15min; refresh ≤ 7 dias| RF39–RF42 |
| RN24 | Tráfego seguro               | TLS 1.2+ com HSTS                                                    | RF01–RF02, RF36–RF38, RF39–RF42 |
| RN32 | Rate limiting                | Login/ingestão/exportação com limites (ex.: 600 req/min por device)  | RF01–RF02, RF36–RF38, RF39 |

## Desempenho

### Tempo de Processamento

| ID   | Requisito                      | Métrica/Alvo                                         | RF Relacionados |
|------|--------------------------------|------------------------------------------------------|-----------------|
| RN51 | Frescor de dados no Dashboard  | Dados disponíveis em até 5 min após ingestão         | RF43–RF45 |
| RN26 | SLA Relatórios D-1             | Disponível até 08:00 BRT; reprocessos até 10:00 BRT  | RF30–RF32 |
| RN27 | SLA Relatórios Mensais         | Disponível em D+1; fechamento com ajustes até D+3    | RF33–RF35 |
| RN28 | SLA Exportações                | ≤ 2 min até 100k linhas; acima disso assíncrono      | RF36–RF38, RF48 |

### Capacidade de Dados

| ID   | Requisito                     | Métrica/Alvo                                         | RF Relacionados |
|------|-------------------------------|------------------------------------------------------|-----------------|
| RN30 | Limites de upload             | CSV até 10 MB e 50 mil linhas por arquivo            | RF09, RF62 |
| RN32 | Rate de ingestão              | 600 req/min por device (ajustável)                   | RF01–RF02 |
| RN31 | Tolerância a picos            | 3× carga média por 1h sem degradação severa          | RF43–RF47, RF46–RF48 |

### Disponibilidade

| ID   | Requisito                 | Métrica/Alvo                      | RF Relacionados |
|------|---------------------------|-----------------------------------|-----------------|
| RN29 | SLO de disponibilidade    | 99,5% mensal                      | RF43–RF47, RF30–RF35 |
| RN33 | Manutenções               | Aviso com 48h; fora horário pico  | RF30–RF35 |
| RN34 | RTO/RPO                   | RTO ≤ 4h; RPO ≤ 1h                | RF30–RF35, RF36–RF38 |

## Governança de Dados

### Qualidade dos Dados

| ID   | Requisito                     | Métrica/Alvo                                            | RF Relacionados |
|------|-------------------------------|---------------------------------------------------------|-----------------|
| RN35 | Ingestão parcial com relatório| ≥ 95% de aceitação por arquivo; relatório de erros      | RF08, RF10 |
| RN36 | Deduplicação                  | Duplicados < 1% dos eventos processados                 | RF15 |
| RN37 | Tipagem e domínios            | Validações aplicadas antes de cálculos                  | RF11–RF14, RF18–RF19, RF23–RF29, RF59–RF61 |
| RN38 | Padrões de formatos           | Datas ISO 8601; números com ponto decimal               | RF07, RF12, RF37 |
| RN25 | Clock skew                     | Aceitar timestamps futuros até +5 min; reorder 24h      | RF12 |
| RN51 | Outliers/km e custos          | Regras aplicadas e sinalização em até 5 min             | RF16, RF22 |

### Backup e Recuperação

| ID   | Requisito             | Métrica/Alvo                                   | RF Relacionados |
|------|-----------------------|------------------------------------------------|-----------------|
| RN39 | Backup                 | Diário completo; incrementais de hora em hora  | RF36–RF38, RF55–RF58 |
| RN40 | Criptografia           | Em repouso e em trânsito                       | RF36–RF38 |
| RN41 | Teste de restauração   | Trimestral                                     | RF36–RF38 |
| RN42 | Procedimentos de DR    | Documentados para parcial e total              | RF30–RF35, RF36–RF38 |

### Retenção de Dados

| ID   | Requisito                 | Métrica/Alvo                         | RF Relacionados |
|------|---------------------------|--------------------------------------|-----------------|
| RN43 | Telemetria bruta          | 24 meses                              | RF01–RF02 |
| RN44 | Agregados/indicadores     | 36 meses                              | RF43–RF45 |
| RN50 | Trilha de auditoria       | 12 meses (ou conforme política)       | RF55–RF58 |
| RN46 | Logs de aplicação         | 90 dias                               | RF36–RF38, RF01–RF02 |
| RN28 | Links de exportação       | Expiram em até 7 dias                 | RF36–RF38 |

## Rastreabilidade

### Logs do Sistema

| ID   | Requisito                     | Métrica/Alvo                                        | RF Relacionados |
|------|-------------------------------|-----------------------------------------------------|-----------------|
| RN45 | Observabilidade ingestão      | Correlation-Id e métricas de latência/erros         | RF01–RF02 |
| RN46 | Logs estruturados/mascaramento| JSON; sem segredos/PII; mascaramento e truncamento  | RF36–RF38, RF39–RF42 |
| RN47 | Relatórios de processamento   | Relatórios de upload/exportação disponíveis pós-ação | RF08, RF10, RF38 |

### Trilha de Auditoria

| ID   | Requisito                 | Métrica/Alvo                                      | RF Relacionados |
|------|---------------------------|---------------------------------------------------|-----------------|
| RN48 | Auditoria de CRUD         | CRUD de usuários/tarifas/rotas/parametrizações    | RF55–RF58, RF59–RF62 |
| RN49 | Eventos de segurança      | Logins, falhas, relatórios e exportações          | RF39–RF42, RF30–RF38 |
| RN50 | Integridade e retenção    | Imutabilidade lógica; retenção ≥ 12 meses         | RF55–RF58 |

### Monitoramento

| ID   | Requisito                 | Métrica/Alvo                                               | RF Relacionados |
|------|---------------------------|------------------------------------------------------------|-----------------|
| RN51 | Lag de processamento      | ≤ 5 min até refletir no Dashboard                          | RF43–RF45 |
| RN52 | Alertas de outliers       | Thresholds configuráveis; latência de alerta ≤ 5 min       | RF52–RF53 |
| RN53 | Notificações              | E-mail entregue ≤ 5 min; preferências por usuário salvas   | RF54 |
| RN54 | SLOs e alertas            | D-1 atraso > 07:30; 5xx ingestão > 1% em 5 min (alerta)    | RF30–RF32, RF01–RF02 |
| RN55 | Health checks/sintéticos  | Checagens periódicas nas rotas críticas                    | RF01–RF02, RF30–RF38 |

## Compatibilidade

### Navegadores Suportados

| ID   | Requisito                 | Métrica/Alvo                                   | RF Relacionados |
|------|---------------------------|-----------------------------------------------|-----------------|
| RN56 | Browsers suportados       | Chrome/Edge/Firefox (2 últimas) e Safari atual | RF43–RF48 |
| RN57 | Navegadores não suportados| Internet Explorer não suportado                | RF43–RF48 |
| RN58 | Regressão visual          | Testes nas páginas principais a cada release   | RF43–RF48 |

### Dispositivos

| ID   | Requisito                 | Métrica/Alvo                          | RF Relacionados |
|------|---------------------------|---------------------------------------|-----------------|
| RN59 | Plataformas                | Windows/macOS/Linux nos navegadores   | RF43–RF48 |
| RN03 | Resolução mínima           | 1366x768 a 1920x1080 (verificado)     | RF43–RF48 |

### Integrações

| ID   | Requisito                 | Métrica/Alvo                                                   | RF Relacionados |
|------|---------------------------|----------------------------------------------------------------|-----------------|
| RN60 | Versionamento de APIs     | v1; política de depreciação e coexistência documentadas        | RF01–RF02, RF36–RF38 |
| RN61 | Idempotência              | Header/chave idempotente para replays                          | RF01–RF02 |
| RN62 | Formatos de exportação    | CSV UTF-8 (vírgula), XLSX; datas ISO 8601                      | RF36–RF38, RF07 |
| RN63 | Paginação                  | Padrão de 1000 registros por página (configurável)             | RF36–RF38, RF46 |
| RN64 | Localização                | pt-BR para números/datas; apresentação padrão em BRT           | RF43–RF47 |

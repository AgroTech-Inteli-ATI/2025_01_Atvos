---
sidebar_position: 2
slug: /sprint-1/requisitos/nao-funcionais
description: "Especificação dos requisitos não funcionais do MVP"
---

# Requisitos Não Funcionais

## Usabilidade

### Interface Web

Requisitos:

- Tempo de carregamento inicial da aplicação ≤ 3s em rede 4G estável e hardware padrão corporativo.
- Páginas principais (Dashboard, Viagens, Relatórios) devem responder a interações de filtro em ≤ 1s para conjuntos de dados do mês corrente.
- Layout responsivo com prioridade para desktop (≥ 1366x768); visualização mobile suportada para consulta (sem edição avançada).
- Consistência visual (cores, tipografia, componentes) seguindo o design system definido para o produto.


### Experiência do Usuário

Requisitos:

- Feedbacks claros de estado (carregando, sem dados, erro, sucesso) em todas as telas.
- Indicativos de frescor dos dados (timestamp da última atualização) no Dashboard Principal.
- Mensagens de erro orientativas, sem expor detalhes internos, com código de suporte para rastreio.

### Acessibilidade

Requisitos:

- Conformidade com WCAG 2.1 AA: contraste, navegação por teclado, leitores de tela (atributos ARIA), foco visível.
- Todos os gráficos e indicadores devem possuir textos alternativos/resumos para tecnologia assistiva.
- Tamanhos de alvo de clique ≥ 44x44px e espaçamento adequado entre elementos interativos.

## Segurança

### Controle de Acesso

Requisitos:

- Modelo RBAC com perfis mínimos: Administrador, Analista, Visualizador.
- Princípio do menor privilégio aplicado a menus, ações (CRUD) e escopo de dados (unidade/região quando aplicável).
- Controle de escopo por centro de custo/unidade para relatórios e visualização de viagens.

### Perfis de Usuário

Requisitos:

- Administrador: gestão de usuários, tarifas, rotas, parâmetros e auditoria; acesso total de leitura.
- Analista: leitura completa, exportação, criação de relatórios, marcação para revisão; sem gestão de usuários.
- Visualizador: leitura de dashboards, viagens e relatórios; sem exportações em massa por padrão.

### Autenticação e Autorização

Requisitos:

- E-mails corporativos; política de senhas conforme RF (mín. 8, maiúscula, minúscula, número, especial) ou governança ATVOS.
- Senhas armazenadas com Argon2id ou bcrypt (cost adequado), sal único por usuário; nunca registrar em logs.
- Tentativas de login: bloqueio após 5 falhas por 15 minutos; captcha após 3 falhas.
- Sessão web: expiração por inatividade de 30 min e absoluta de 12h; logout em todos os dispositivos disponível.
- Tokens (se aplicável): JWT com expiração curta (≤ 15 min) e refresh token rotacionado (≤ 7 dias); escopos por perfil.
- CSRF habilitado para fluxos baseados em cookies; CORS restritivo para origens confiáveis.
- Tráfego sempre em TLS 1.2+; HSTS ativo.
- Rate limiting para endpoints de login, ingestão e exportação; proteção contra enumeração de usuários.

## Desempenho

### Tempo de Processamento

Requisitos:

- Ingestão de eventos: dados disponíveis para consultas do Dashboard em até 5 minutos após recebimento (near real-time).
- Relatórios D-1 disponíveis até 08:00 BRT (conforme RF); reprocessos permitidos até 10:00 BRT em caso de falhas.
- Relatórios Mensais disponíveis em D+1; fechamento com ajustes até D+3.
- Exportações até 100 mil linhas geradas em ≤ 2 min; acima disso, geração assíncrona com notificação.

### Capacidade de Dados

Requisitos (premissas iniciais):

- Conexões simultâneas: 100 usuários concorrentes; 600 req/min por device na ingestão (limite ajustável).
- Upload CSV: até 10 MB e 50 mil linhas por arquivo (conforme RF).
- Tolerar picos de 3× a carga média por pelo menos 1h sem degradação severa.

### Disponibilidade

Requisitos:

- SLO de disponibilidade de 99,5% mensal para a aplicação web e APIs críticas.
- Janela de manutenção comunicada com 48h de antecedência, preferencialmente fora do horário comercial local.
- RTO ≤ 4 horas e RPO ≤ 1 hora para serviços e dados de produção.

## Governança de Dados

### Qualidade dos Dados

Requisitos:

- Taxa de aceitação de linhas em uploads ≥ 95% por arquivo; rejeições documentadas em relatório de erros.
- Duplicidade controlada: taxa de duplicados < 1% dos eventos processados.
- Regras de validação conforme RF (tipagem, domínios, outliers) aplicadas antes de disponibilizar aos cálculos.
- Fuso horário: armazenamento em UTC; apresentação por padrão em BRT com indicação de fuso.

### Backup e Recuperação

Requisitos:

- Backups diários completos e incrementais horários dos dados transacionais.
- Criptografia de backups em repouso e em trânsito; testes de restauração trimestrais.
- Procedimentos documentados para recuperação parcial (tabelas-chave) e total.

### Retenção de Dados

Requisitos:

- Telemetria bruta: retenção por 24 meses; dados agregados/indicadores: 36 meses.
- Logs de aplicação: 90 dias; trilhas de auditoria: 12 meses (ou conforme política corporativa/LGPD).
- Links de exportação expiram em até 7 dias.

## Rastreabilidade

### Logs do Sistema

Requisitos:

- Logs estruturados em JSON com Correlation-Id por requisição/processo.
- Não registrar segredos/PII; mascarar e truncar payloads sensíveis.
- Níveis de log padronizados (INFO, WARN, ERROR) e campos para rastreio (usuarioId, deviceId, requestId).

### Trilha de Auditoria

Requisitos:

- Auditoria de CRUD em usuários, tarifas, rotas, parâmetros e permissões.
- Registro de logins, falhas de autenticação, geração de relatórios e exportações.
- Integridade dos registros de auditoria (imutabilidade lógica) e retenção mínima de 12 meses.

### Monitoramento

Requisitos:

- Métricas de ingestão (taxa, latência, erros), lag de processamento, tempos de geração de relatórios e exportações.
- SLOs monitorados com alertas (p. ex., atraso D-1 > 07:30 BRT, ingestão com erro 5xx > 1% em 5 min).
- Health checks e testes sintéticos periódicos nas rotas críticas.

## Compatibilidade

### Navegadores Suportados

Requisitos:

- Últimas duas versões estáveis de Chrome, Edge e Firefox; Safari versão estável mais recente.
- Internet Explorer não suportado.
- Testes de regressão visual nas páginas principais em cada release.

### Dispositivos

Requisitos:

- Suporte oficial para navegadores suportados.
- Responsividade mínima para 1366x768; verificação de layout até 1920x1080.

### Integrações

Requisitos:

- APIs versionadas (v1) com política de depreciação comunicada e período de coexistência.
- Idempotência para operações de ingestão via header/chave idempotente quando aplicável.
- Paginação padrão (por exemplo, 1000 registros por página) em listagens/exportações.
- Formatos de exportação: CSV (UTF-8, separador vírgula) e XLSX; datas em ISO 8601.
- Localização pt-BR: formatos numéricos e de data/hora na UI; timezone padrão BRT na apresentação.



# Documentação de Estimativa de Custos – Nuvem GCP para o Projeto Agro-Tech / ATVOS

Esta estimativa de custo foi elaborada com base no cálculo exportado pela ferramenta oficial de orçamento da Google Cloud Pricing Calculator, com os parâmetros de uso e infra-estrutura definidos para o projeto da Agro-Tech para a ATVOS.

No cenário atual, considerando a configuração ativa de infraestrutura (VM/e2-medium rodando 24/7 para front-end + armazenamento + backend), o custo estimado gira em torno de **US$ 35,80 por mês**.

No entanto, foi também simulada uma configuração de “stress test” ou “pico máximo” — como se fosse uma “Black Friday da infraestrutura” (alto volume de uso, alto armazenamento, múltiplas instâncias) — cujo custo estimado atinge **US$ 3.579,503 por mês**.

Estes dois valores expressam cenários extremos:

* O primeiro representa o uso esperado realista.
* O segundo representa um limite máximo projetado, com superprovisionamento deliberado, pensado para suportar carga elevada ou uso exagerado.

## Redução de custos via arquitetura otimizada

Embora a configuração atual use uma VM (e2-medium) para hospedar o front-end de forma contínua, é importante destacar que existe uma alternativa de custo muito mais baixo: servir o front-end como site estático. Isso pode ser feito usando Cloud Storage + Cloud CDN, sem necessidade de VM ou instâncias ativas constantemente.

A hospedagem de sites estáticos via Cloud Storage — com conteúdo público e servido via CDN / balanceamento de carga — é suportada oficialmente pela Google Cloud. ([Google Cloud Documentation][1])
Esse modelo reduz drasticamente os custos relativos ao front-end, uma vez que não há uso contínuo de CPU/memória — apenas armazenamento e banda passiva conforme acesso dos usuários.

## Justificativa da configuração atual

Escolhemos usar uma VM e2-medium rodando 24/7 para o front-end por razões de simplicidade e agilidade, já que estamos em fase de desenvolvimento/exploração. Essa configuração permite que a equipe teste rapidamente funcionalidades sem configurar bucket, balanceador de carga, CDN, DNS, políticas de cache etc.

Por essa razão, embora haja uma opção mais econômica, optamos por este setup “mais pesado” para acelerar o desenvolvimento e evitar burocracias iniciais.

## Uso pretendido: dados de telemetria e auditoria

O projeto vai armazenar dados de telemetria de viagens e manter um histórico para auditoria. Portanto o armazenamento (via Cloud Storage ou similar) existe, e essa parte está contemplada na estimativa de custo mensal. A quantidade de dados esperada é baixa/moderada, por enquanto, o que contribui para o custo mensal de ~US$ 35,80 em uso normal.

## Conclusão

Com a configuração atual:

* Custo mensal esperado: **US$ 35,80** (situação realista e conservadora).
* Custo máximo simulado (“Black Friday da infraestrutura”): **US$ 3.579,503**.

O custo pode ser reduzido consideravelmente servindo o front-end como estático via bucket + CDN, evitando a VM rodando 24/7 — mas a configuração atual privilegia agilidade no desenvolvimento.


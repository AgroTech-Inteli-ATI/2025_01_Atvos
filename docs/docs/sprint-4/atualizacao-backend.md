# Documentação Técnica de Atualização API Backend

  Esta documentação técnica descreve a arquitetura e os endpoints da API backend desenvolvida com o framework Django REST Framework, após a migração do banco de dados Supabase (PostgreSQL) para o Google BigQuery. A nova arquitetura foi projetada para lidar com grandes volumes de dados analíticos, aproveitando as capacidades de processamento massivamente paralelo do BigQuery para consultas agregadas.

### **Limitações e Considerações Técnicas do BigQuery**

1. **Streaming Buffer (90 minutos)**: Dados inseridos via streaming não podem ser deletados ou atualizados por 90 minutos. A API implementa verificação de idade dos registros antes de permitir DELETE.

2. **Consistência Eventual**: Inserções via `insert_rows_json` podem levar alguns segundos para ficarem visíveis em queries.

3. **Custos por Query**: Cada query processa dados e gera custos. A API implementa:  
* Filtros de data padrão (últimos 30 dias para listagens, 3 anos para detalhes)  
* Paginação eficiente com LIMIT/OFFSET  
* Cache de queries quando aplicável

## **1\. Gestão de Viagens (`/travels/`)**

### **1.1. Criar Viagem**

| Detalhe | Descrição |
| ----- | ----- |
| **Método HTTP** | `POST` |
| **URL** | `/travels/` |
| **Funcionalidade** | Cria um novo registro de viagem no BigQuery. Se a placa do veículo (`license_plate`) for fornecida, o sistema busca ou cria automaticamente o registro do veículo na tabela `vehicle`. |

**Exemplo de Requisição:**

```json
POST /travels/  
Content-Type: application/json

{  
"asset\_description": "Caminhão Mercedes-Benz Actros 2546",  
"register\_number": "REG12345",  
"asset\_id": 102,  
"garage\_name": "Garagem Sul \- Unidade Piracicaba",  
"full\_distance": 350.50,  
"datetime": "2024-11-03T14:30:00-03:00",  
"license\_plate": "XYZ-9876",  
"unit\_id": 20  
}
```
**Exemplo de Resposta (Sucesso \- Status Code `201 Created`):**

```json
{  
"success": true,  
"data": {  
"id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",  
"asset\_description": "Caminhão Mercedes-Benz Actros 2546",  
"register\_number": "REG12345",  
"license\_plate": "XYZ987",  
"datetime": "2024-11-03T14:30:00-03:00"  
},  
"message": "Viagem criada com sucesso",  
"timestamp": "2024-11-03T17:30:15.234567+00:00"  
}
```

**Exemplo de Resposta (Erro de Validação \- Status Code `400 Bad Request`):**
```json
{  
"success": false,  
"error": {  
"code": "VALIDATION\_ERROR",  
"message": {  
"datetime": \["A data da viagem não pode ser no futuro."\],  
"full\_distance": \["A distância deve ser um número positivo."\]  
}  
},  
"timestamp": "2024-11-03T17:30:15.234567+00:00"  
}
```
### **1.2. Listar Viagens**

| Detalhe | Descrição |
| ----- | ----- |
| **Método HTTP** | `GET` |
| **URL** | `/travels/` |
| **Funcionalidade** | Retorna uma lista paginada de viagens com informações agregadas (total de paradas, motorista principal). A query utiliza CTEs (Common Table Expressions) para otimizar a agregação de dados relacionados. Por padrão, filtra viagens dos últimos 30 dias. |

**Parâmetros de Query (Filtros e Paginação):**

| Parâmetro | Tipo | Descrição | Padrão | Exemplo |
| ----- | ----- | ----- | ----- | ----- |
| `page` | `int` | Número da página a ser retornada | 1 | `?page=2` |
| `limit` | `int` | Número de itens por página | 20 | `?limit=50` |
| `search` | `string` | Busca textual em placa ou descrição | \- | `?search=Mercedes` |
| `unit_id` | `int` | Filtra por ID da unidade operacional | \- | `?unit_id=10` |
| `start_date` | `date` | Data inicial (formato YYYY-MM-DD) | Últimos 30 dias | `?start_date=2024-01-01` |
| `end_date` | `date` | Data final (formato YYYY-MM-DD) | Data atual | `?end_date=2024-12-31` |

**Exemplo de Requisição:**

```http
GET /travels/?page=1\&limit=20\&search=Mercedes\&unit\_id=20\&start\_date=2024-10-01\&end\_date=2024-11-03
```

**Exemplo de Resposta (Sucesso \- Status Code `200 OK`):**

```json
{  
"success": true,  
"data": \[  
{  
"id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",  
"license\_plate": "XYZ987",  
"asset\_description": "Caminhão Mercedes-Benz Actros 2546",  
"register\_number": "REG12345",  
"garage\_name": "Garagem Sul \- Unidade Piracicaba",  
"full\_distance": "350.50",  
"datetime": "2024-11-03T14:30:00-03:00",  
"unit\_id": 20,  
"unit\_name": null,  
"total\_stops": 4,  
"primary\_driver": "João Silva"  
},  
{  
"id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",  
"license\_plate": "ABC123",  
"asset\_description": "Caminhão Mercedes-Benz Atego 1719",  
"register\_number": "REG12346",  
"garage\_name": "Garagem Central",  
"full\_distance": "275.30",  
"datetime": "2024-11-02T08:15:00-03:00",  
"unit\_id": 20,  
"unit\_name": null,  
"total\_stops": 3,  
"primary\_driver": "Maria Santos"  
}  
\],  
"pagination": {  
"page": 1,  
"limit": 20,  
"total": 2,  
"totalPages": 1  
},  
"timestamp": "2024-11-03T17:35:22.456789+00:00"  
}
```

### **1.3. Detalhes da Viagem**

| Detalhe | Descrição |
| ----- | ----- |
| **Método HTTP** | `GET` |
| **URL** | `/travels/{id}/` |
| **Funcionalidade** | Retorna os detalhes completos de uma viagem específica, incluindo informações do veículo, contagem de paradas e dados de custo (`bill`) quando existirem. A query faz LEFT JOIN com as tabelas relacionadas para consolidar todas as informações. Filtra automaticamente viagens dos últimos 3 anos (1095 dias). |

**Exemplo de Requisição:**

```http
GET /travels/a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d/
```

**Exemplo de Resposta (Sucesso \- Status Code `200 OK`):**

```json
{  
"success": true,  
"data": {  
"id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",  
"license\_plate": "XYZ987",  
"asset\_description": "Caminhão Mercedes-Benz Actros 2546",  
"register\_number": "REG12345",  
"asset\_id": 102,  
"garage\_name": "Garagem Sul \- Unidade Piracicaba",  
"full\_distance": "350.50",  
"datetime": "2024-11-03T14:30:00-03:00",  
"unit\_id": 20,  
"unit\_name": null,  
"stops\_count": 4,  
"bill": {  
"fix\_cost": 150.00,  
"variable\_km": 2.50,  
"total\_cost": 1026.25,  
"datetime": "2024-11-03T15:00:00-03:00"  
}  
},  
"timestamp": "2024-11-03T17:40:33.678901+00:00"  
}
```
**Exemplo de Resposta (Viagem sem Bill \- Status Code `200 OK`):**

```json
{  
"success": true,  
"data": {  
"id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",  
"license\_plate": "XYZ987",  
"asset\_description": "Caminhão Mercedes-Benz Actros 2546",  
"register\_number": "REG12345",  
"asset\_id": 102,  
"garage\_name": "Garagem Sul \- Unidade Piracicaba",  
"full\_distance": "350.50",  
"datetime": "2024-11-03T14:30:00-03:00",  
"unit\_id": 20,  
"unit\_name": null,  
"stops\_count": 4,  
"bill": null  
},  
"timestamp": "2024-11-03T17:40:33.678901+00:00"  
}
```

**Exemplo de Resposta (Erro \- Viagem Não Encontrada \- Status Code `404 Not Found`):**

```json
{  
"success": false,  
"error": {  
"code": "TRAVEL\_NOT\_FOUND",  
"message": "Viagem com ID a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d não encontrada"  
},  
"timestamp": "2024-11-03T17:40:33.678901+00:00"  
}
```

### **1.4. Remover Viagem**

| Detalhe | Descrição |
| ----- | ----- |
| **Método HTTP** | `DELETE` |
| **URL** | `/travels/{id}/` |
| **Funcionalidade** | Remove o registro de viagem do BigQuery. **ATENÇÃO**: Devido às limitações do streaming buffer, viagens criadas há menos de 90 minutos não podem ser deletadas e retornarão erro `409 Conflict`. A remoção também deleta em cascata todas as paradas (`stop`) e custos (`bill`) associados. |


**Exemplo de Requisição:**

```http
DELETE /travels/a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d/
```

**Exemplo de Resposta (Sucesso \- Status Code `200 OK`):**

```json
{  
"success": true,  
"message": "Viagem removida com sucesso",  
"timestamp": "2024-11-03T17:45:44.789012+00:00"  
}
```
**Exemplo de Resposta (Erro \- Streaming Buffer \- Status Code `409 Conflict`):**

```json
{  
"success": false,  
"error": {  
"code": "STREAMING\_BUFFER\_ERROR",  
"message": "Não é possível deletar viagens recém-criadas. Aguarde 90 minutos.",  
"details": "BigQuery não permite DELETE em dados no streaming buffer (\< 90 min)"  
},  
"timestamp": "2024-11-03T17:45:44.789012+00:00"  
}
```
**Exemplo de Resposta (Erro \- Viagem Não Encontrada \- Status Code `404 Not Found`):**

```json
{  
"success": false,  
"error": {  
"code": "TRAVEL\_NOT\_FOUND",  
"message": "Viagem com ID a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d não encontrada"  
},  
"timestamp": "2024-11-03T17:45:44.789012+00:00"  
}
```

### **1.5. Listar Paradas de uma Viagem**

| Detalhe | Descrição |
| ----- | ----- |
| **Método HTTP** | `GET` |
| **URL** | `/travels/{id}/stops/` |
| **Funcionalidade** | Retorna a lista completa de paradas (`stop`) associadas a uma viagem específica, ordenadas cronologicamente por `departure_datetime`. |

**Exemplo de Requisição:**

```http
GET /travels/a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d/stops/
```

**Exemplo de Resposta (Sucesso \- Status Code `200 OK`):**

```json
{  
"success": true,  
"data": \[  
{  
"id": "c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f",  
"travel\_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",  
"departure\_datetime": "2024-11-03T14:30:00-03:00",  
"driver": "João Silva",  
"departure\_site": "Usina Piracicaba \- Portaria Principal",  
"trip\_time": "01:45:00",  
"trip\_distance": "87.50",  
"arrival\_datetime": "2024-11-03T16:15:00-03:00",  
"arrival\_site": "Armazém Central \- Campinas"  
},  
{  
"id": "d4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f8a",  
"travel\_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",  
"departure\_datetime": "2024-11-03T16:30:00-03:00",  
"driver": "João Silva",  
"departure\_site": "Armazém Central \- Campinas",  
"trip\_time": "02:15:00",  
"trip\_distance": "112.30",  
"arrival\_datetime": "2024-11-03T18:45:00-03:00",  
"arrival\_site": "Fazenda Santa Rita \- Seção 5"  
},  
{  
"id": "e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b",  
"travel\_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",  
"departure\_datetime": "2024-11-03T19:00:00-03:00",  
"driver": "Maria Santos",  
"departure\_site": "Fazenda Santa Rita \- Seção 5",  
"trip\_time": "01:30:00",  
"trip\_distance": "75.40",  
"arrival\_datetime": "2024-11-03T20:30:00-03:00",  
"arrival\_site": "Posto de Combustível \- Rodovia SP-304"  
},  
{  
"id": "f6a7b8c9-d0e1-4f2a-3b4c-5d6e7f8a9b0c",  
"travel\_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",  
"departure\_datetime": "2024-11-03T20:45:00-03:00",  
"driver": "Maria Santos",  
"departure\_site": "Posto de Combustível \- Rodovia SP-304",  
"trip\_time": "01:20:00",  
"trip\_distance": "75.30",  
"arrival\_datetime": "2024-11-03T22:05:00-03:00",  
"arrival\_site": "Usina Piracicaba \- Portaria Principal"  
}  
\],  
"timestamp": "2024-11-03T17:50:55.890123+00:00"  
}
```

**Exemplo de Resposta (Viagem sem Paradas \- Status Code `200 OK`):**
```json
{  
"success": true,  
"data": \[\],  
"timestamp": "2024-11-03T17:50:55.890123+00:00"  
}
```
## **2\. Gestão de Custos (`/bills/`)**

### **2.1. Criar Custo**

| Detalhe | Descrição |
| ----- | ----- |
| **Método HTTP** | `POST` |
| **URL** | `/bills/` |
| **Funcionalidade** | Cria um novo registro de custo associado a uma viagem existente. O sistema valida automaticamente se a viagem existe antes de criar o bill. O `total_cost` é calculado automaticamente no backend e retornado na resposta. |

**Exemplo de Requisição:**
```json
POST /bills/  
Content-Type: application/json

{  
"travel\_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",  
"fix\_cost": 150.00,  
"variable\_km": 2.50,  
"datetime": "2024-11-03T15:00:00-03:00"  
}
```

**Exemplo de Resposta (Sucesso \- Status Code `201 Created`):**
```json
{  
"success": true,  
"data": {  
"travel\_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",  
"fix\_cost": 150.00,  
"variable\_km": 2.50,  
"total\_cost": 1026.25,  
"datetime": "2024-11-03T15:00:00-03:00"  
},  
"message": "Custo registrado com sucesso",  
"timestamp": "2024-11-03T18:00:11.234567+00:00"  
}
```
**Exemplo de Resposta (Erro \- Viagem Não Encontrada \- Status Code `404 Not Found`):**
```json
{  
"success": false,  
"error": {  
"code": "TRAVEL\_NOT\_FOUND",  
"message": "Viagem com ID a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d não encontrada"  
},  
"timestamp": "2024-11-03T18:00:11.234567+00:00"  
}
```
**Exemplo de Resposta (Erro \- Validação \- Status Code `400 Bad Request`):**

```json
{  
"success": false,  
"error": {  
"code": "VALIDATION\_ERROR",  
"message": {  
"fix\_cost": \["O custo fixo não pode ser negativo."\],  
"variable\_km": \["O custo variável não pode ser negativo."\]  
}  
},  
"timestamp": "2024-11-03T18:00:11.234567+00:00"  
}
```
### **2.2. Listar Custos**

| Detalhe | Descrição |
| ----- | ----- |
| **Método HTTP** | `GET` |
| **URL** | `/bills/` |
| **Funcionalidade** | Retorna uma lista paginada de custos com informações detalhadas da viagem associada (placa do veículo e distância percorrida). A query faz JOIN com as tabelas `travel` e `vehicle` para enriquecer os dados. Filtra automaticamente custos dos últimos 3 anos. |

**Parâmetros de Query (Filtros e Paginação):**

| Parâmetro | Tipo | Descrição | Padrão | Exemplo |
| ----- | ----- | ----- | ----- | ----- |
| `page` | `int` | Número da página a ser retornada | 1 | `?page=1` |
| `limit` | `int` | Número de itens por página | 20 | `?limit=50` |
| `travel_id` | `string` | Filtra custos de uma viagem específica (UUID) | \- | `?travel_id=a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d` |

**Exemplo de Requisição:**
```http
GET /bills/?page=1\&limit=20\&travel\_id=a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d
```
**Exemplo de Resposta (Sucesso \- Status Code `200 OK`):**

```json
{  
"success": true,  
"data": \[  
{  
"id": "g7h8i9j0-k1l2-4m3n-4o5p-6q7r8s9t0u1v",  
"travel\_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",  
"fix\_cost": "150.00",  
"variable\_km": "2.50",  
"total\_cost": 1026.25,  
"datetime": "2024-11-03T15:00:00-03:00",  
"travel\_info": {  
"license\_plate": "XYZ987",  
"full\_distance": 350.5  
}  
}  
\],  
"timestamp": "2024-11-03T18:05:22.345678+00:00"  
}
```

**Exemplo de Requisição (Sem Filtro \- Todos os Bills):**

```http
GET /bills/?page=1\&limit=20
```

**Exemplo de Resposta (Sucesso \- Status Code `200 OK`):**

```json
{  
"success": true,  
"data": \[  
{  
"id": "g7h8i9j0-k1l2-4m3n-4o5p-6q7r8s9t0u1v",  
"travel\_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",  
"fix\_cost": "150.00",  
"variable\_km": "2.50",  
"total\_cost": 1026.25,  
"datetime": "2024-11-03T15:00:00-03:00",  
"travel\_info": {  
"license\_plate": "XYZ987",  
"full\_distance": 350.5  
}  
},  
{  
"id": "h8i9j0k1-l2m3-4n4o-5p6q-7r8s9t0u1v2w",  
"travel\_id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",  
"fix\_cost": "120.00",  
"variable\_km": "2.30",  
"total\_cost": 753.19,  
"datetime": "2024-11-02T09:00:00-03:00",  
"travel\_info": {  
"license\_plate": "ABC123",  
"full\_distance": 275.3  
}  
}  
\],  
"timestamp": "2024-11-03T18:05:22.345678+00:00"  
}
```

## **3. Dashboard (`/dashboard/`)**

### **3.1. Resumo de Viagens e Custos**

| Detalhe | Descrição |
| ----- | ----- |
| **Método HTTP** | `GET` |
| **URL** | `/dashboard/travel-summary/` |
| **Funcionalidade** | Retorna métricas consolidadas de viagens e custos para análise gerencial. Por padrão, filtra os dados dos últimos 30 dias. |

**Parâmetros de Query (Filtros):**

| Parâmetro | Tipo | Descrição | Padrão | Exemplo |
| ----- | ----- | ----- | ----- | ----- |
| `start_date` | `datetime` | Data/hora inicial (ISO 8601) | Últimos 30 dias | `2024-01-01T00:00:00Z` |
| `end_date` | `datetime` | Data/hora final (ISO 8601) | Data/hora atual | `2024-12-31T23:59:59Z` |
| `unit_id` | `int` | Filtrar por unidade operacional | Todas | `20` |

**Exemplo de Requisição (Padrão - Últimos 30 Dias):**

```http
GET /dashboard/travel-summary/
```

**Exemplo de Resposta (Sucesso - Status Code `200 OK`):**

```json
{
"success": true,
"data": {
"total_distance_km": 15847.30,
"total_cost": 245630.85,
"total_travels": 87,
"avg_cost_per_travel": 2823.34,
"avg_distance_per_travel": 182.15,
"filters_applied": {
"date_range": "last_30_days",
"start_date_calculated": "2024-10-04 00:00:00",
"end_date_calculated": "2024-11-03 18:50:00"
}
},
"timestamp": "2024-11-03T18:50:22.123456+00:00"
}
```

**Exemplo de Requisição (Com Filtros Personalizados):**

```http
GET /dashboard/travel-summary/?start_date=2024-01-01T00:00:00Z&end_date=2024-12-31T23:59:59Z&unit_id=20
```

**Exemplo de Resposta (Com Filtros Personalizados - Status Code `200 OK`):**

```json
{
"success": true,
"data": {
"total_distance_km": 184522.75,
"total_cost": 3245890.50,
"total_travels": 1053,
"avg_cost_per_travel": 3082.65,
"avg_distance_per_travel": 175.26,
"filters_applied": {
"start_date": "2024-01-01T00:00:00Z",
"end_date": "2024-12-31T23:59:59Z",
"unit_id": 20
}
},
"timestamp": "2024-11-03T18:52:15.234567+00:00"
}
```

---

### **3.2. Evolução de Custos ao Longo do Tempo**

| Detalhe | Descrição |
| ----- | ----- |
| **Método HTTP** | `GET` |
| **URL** | `/dashboard/cost-evolution/` |
| **Funcionalidade** | Retorna uma série temporal detalhando a evolução dos custos agregados por dia, semana ou mês, permitindo análise de tendências. |

**Parâmetros de Query (Filtros e Agregação):**

| Parâmetro | Tipo | Obrigatório | Descrição | Valores Aceitos | Padrão |
| ----- | ----- | ----- | ----- | ----- | ----- |
| `period` | `string` | Não | Nível de agregação temporal | `day`, `week`, `month` | `month` |
| `limit` | `int` | Não | Número de períodos a retornar | 1-100 | `12` |
| `start_date` | `datetime` | Não | Data inicial (ISO 8601) | - | Calculado com base no `limit` |
| `end_date` | `datetime` | Não | Data final (ISO 8601) | - | Data/hora atual |
| `unit_id` | `int` | Não | Filtrar por unidade operacional | Inteiro positivo | Todas |

**Exemplo de Requisição (Evolução Mensal - Últimos 12 Meses):**

```http
GET /dashboard/cost-evolution/?period=month&limit=12
```

**Exemplo de Resposta (Evolução Mensal - Status Code `200 OK`):**

```json
{
"success": true,
"data": [
{
"period": "2023-12",
"period_full_date": "2023-12-01T00:00:00+00:00",
"total_cost": 285430.50,
"fix_cost": 125000.00,
"variable_cost": 160430.50,
"total_distance_km": 18250.75,
"total_bills": 95,
"avg_cost": 3004.53
},
{
"period": "2024-01",
"period_full_date": "2024-01-01T00:00:00+00:00",
"total_cost": 312580.25,
"fix_cost": 138000.00,
"variable_cost": 174580.25,
"total_distance_km": 19820.30,
"total_bills": 103,
"avg_cost": 3034.76
},
{
"period": "2024-02",
"period_full_date": "2024-02-01T00:00:00+00:00",
"total_cost": 298765.80,
"fix_cost": 131500.00,
"variable_cost": 167265.80,
"total_distance_km": 18975.45,
"total_bills": 98,
"avg_cost": 3048.63
}
],
"params": {
"period": "month",
"limit": 12,
"results_count": 3,
"start_date_calculated": "2023-12-03 18:55:00"
},
"timestamp": "2024-11-03T18:55:30.345678+00:00"
}
```

**Exemplo de Requisição (Evolução Diária - Últimos 7 Dias):**

```http
GET /dashboard/cost-evolution/?period=day&limit=7
```

**Exemplo de Resposta (Evolução Diária - Status Code `200 OK`):**

```json
{
"success": true,
"data": [
{
"period": "2024-10-28",
"period_full_date": "2024-10-28T00:00:00+00:00",
"total_cost": 9850.30,
"fix_cost": 4200.00,
"variable_cost": 5650.30,
"total_distance_km": 645.20,
"total_bills": 3,
"avg_cost": 3283.43
},
{
"period": "2024-10-29",
"period_full_date": "2024-10-29T00:00:00+00:00",
"total_cost": 12340.75,
"fix_cost": 5400.00,
"variable_cost": 6940.75,
"total_distance_km": 790.50,
"total_bills": 4,
"avg_cost": 3085.19
},
{
"period": "2024-10-30",
"period_full_date": "2024-10-30T00:00:00+00:00",
"total_cost": 8920.50,
"fix_cost": 3600.00,
"variable_cost": 5320.50,
"total_distance_km": 605.80,
"total_bills": 2,
"avg_cost": 4460.25
}
],
"params": {
"period": "day",
"limit": 7,
"results_count": 3,
"start_date_calculated": "2024-10-27 18:57:00"
},
"timestamp": "2024-11-03T18:57:45.456789+00:00"
}
```

**Exemplo de Requisição (Evolução Semanal com Filtros Customizados):**

```http
GET /dashboard/cost-evolution/?period=week&start_date=2024-01-01T00:00:00Z&end_date=2024-03-31T23:59:59Z&unit_id=15
```

**Exemplo de Resposta (Evolução Semanal com Filtros Customizados - Status Code `200 OK`):**

```json
{
"success": true,
"data": [
{
"period": "2024-W01",
"period_full_date": "2024-01-01T00:00:00+00:00",
"total_cost": 45230.80,
"fix_cost": 20000.00,
"variable_cost": 25230.80,
"total_distance_km": 2875.40,
"total_bills": 15,
"avg_cost": 3015.39
},
{
"period": "2024-W02",
"period_full_date": "2024-01-08T00:00:00+00:00",
"total_cost": 52840.25,
"fix_cost": 23400.00,
"variable_cost": 29440.25,
"total_distance_km": 3350.75,
"total_bills": 18,
"avg_cost": 2935.57
}
],
"params": {
"period": "week",
"limit": 12,
"results_count": 2,
"start_date": "2024-01-01T00:00:00Z",
"end_date": "2024-03-31T23:59:59Z",
"unit_id": 15
},
"timestamp": "2024-11-03T19:00:10.567890+00:00"
}
```


## **Conclusão**

  A migração do Supabase (PostgreSQL) para o Google BigQuery representa uma evolução estratégica na arquitetura da API, posicionando o sistema para escalar horizontalmente e processar volumes massivos de dados analíticos com performance superior. Esta documentação consolida todos os aspectos técnicos da nova implementação, descrevendo detalhadamente a estrutura de dados, os endpoints disponíveis, as operações suportadas e as considerações específicas do BigQuery.
# Documentação Técnica da API Backend

&ensp; Esta documentação técnica descreve os endpoints da API backend, desenvolvida com o framework Django. Nesse sentido, implementa-se um sistema de gestão de usuários, contemplando funcionalidades de cadastro, autenticação e autorização baseadas em JSON Web Tokens (JWT), assegurando um controle de acesso seguro. Além disso, a documentação apresenta os recursos de gestão de viagens, com endpoints dedicados à criação, listagem, detalhamento, atualização e exclusão de registros de viagens, incluindo a possibilidade de associar informações de custo a cada viagem.

## 1. Usuários

### 1.1. Cadastro de Usuário

| Detalhe | Descrição |
| :--- | :--- |
| **Método HTTP** | `POST` |
| **URL** | `/users/register` |
| **Funcionalidade** | Permite o cadastro de um novo usuário no sistema. A senha é hasheada antes de ser salva. |

**Exemplo de Requisição:**

```json
POST /users/register
Content-Type: application/json

{
    "name": "João da Silva",
    "email": "joao.silva@exemplo.com",
    "senha": "senhaSegura123"
}
```

**Exemplo de Resposta (Sucesso - Status Code `201 Created`):**

```json
{
    "message": "Usuário cadastrado com sucesso!",
    "user": {
        "id": 1,
        "name": "João da Silva",
        "email": "joao.silva@exemplo.com",
        "created_at": "2025-11-02T10:00:00.000000Z"
    }
}
```


### 1.2. Login de Usuário

| Detalhe | Descrição |
| :--- | :--- |
| **Método HTTP** | `POST` |
| **URL** | `/users/login` |
| **Funcionalidade** | Autentica o usuário com email e senha, retornando um **JSON Web Token (JWT)** para acesso a rotas protegidas. |

**Exemplo de Requisição:**

```json
POST /users/login
Content-Type: application/json

{
    "email": "joao.silva@exemplo.com",
    "senha": "senhaSegura123"
}
```

**Exemplo de Resposta (Sucesso - Status Code `200 OK`):**

```json
{
    "message": "Login realizado com sucesso!",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "name": "João da Silva",
        "email": "joao.silva@exemplo.com"
    }
}
```


### 1.3. Obter Detalhes do Usuário

| Detalhe | Descrição |
| :--- | :--- |
| **Método HTTP** | `GET` |
| **URL** | `/users/{user_id}` |
| **Funcionalidade** | Retorna os detalhes do usuário especificado. **Requer autenticação JWT.** O usuário só pode consultar seus próprios dados. |

**Exemplo de Requisição:**

```http
GET /users/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemplo de Resposta (Sucesso - Status Code `200 OK`):**

```json
{
    "user": {
        "id": 1,
        "name": "João da Silva",
        "email": "joao.silva@exemplo.com",
        "created_at": "2025-11-02T10:00:00.000000Z",
        "updated_at": "2025-11-02T10:00:00.000000Z"
    }
}
```

### 1.4. Atualizar Usuário

| Detalhe | Descrição |
| :--- | :--- |
| **Método HTTP** | `PUT` / `PATCH` |
| **URL** | `/users/update/{user_id}` |
| **Funcionalidade** | Atualiza os dados do usuário. `PUT` requer todos os campos. `PATCH` permite atualização parcial. **Requer autenticação JWT.** O usuário só pode atualizar seus próprios dados. |

**Exemplo de Requisição (`PATCH` para atualizar apenas o nome):**

```json
PATCH /users/update/1
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
    "name": "João Silva Atualizado"
}
```

**Exemplo de Resposta (Sucesso - Status Code `200 OK`):**

```json
{
    "message": "Usuário atualizado com sucesso!",
    "user": {
        "id": 1,
        "name": "João Silva Atualizado",
        "email": "joao.silva@exemplo.com",
        "updated_at": "2025-11-02T10:30:00.000000Z"
    }
}
```

### 1.5. Desativar Usuário (Soft Delete)

| Detalhe | Descrição |
| :--- | :--- |
| **Método HTTP** | `DELETE` |
| **URL** | `/users/delete/{user_id}` |
| **Funcionalidade** | Realiza a exclusão lógica (soft delete) do usuário, alterando o campo `ativo` para `False`. **Requer autenticação JWT.** O usuário só pode desativar sua própria conta. |

**Exemplo de Requisição:**

```http
DELETE /users/delete/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemplo de Resposta (Sucesso - Status Code `200 OK`):**

```json
{
    "message": "Usuário desativado com sucesso!",
    "user": {
        "id": 1,
        "name": "João Silva Atualizado",
        "email": "joao.silva@exemplo.com",
        "ativo": false
    }
}
```

Esse módulo de cadastro e autenticação de usuários adota práticas de segurança, utilizando JSON Web Tokens (JWT) para controle de acesso. O token, gerado no endpoint `/users/login`, inclui informações do usuário como `user_id`, `email` e `name`, além de um tempo de expiração, e deve ser enviado no cabeçalho `Authorization` no formato `Bearer <token>` para acessar rotas protegidas. A validação é realizada pelo decorador `@token_required`, que verifica a presença, autenticidade e validade do token, anexando o `user_id` decodificado à requisição. As senhas são armazenadas de forma segura com o uso da função `make_password` do Django, que aplica hashing com `pbkdf2_sha256`, garantindo proteção contra acesso indevido. A autorização segue o princípio de *Self-Authorization*, permitindo que cada usuário visualize ou modifique apenas seus próprios dados por meio da comparação entre o `user_id` do token e o da URL. Além disso, a API adota o conceito de Soft Delete, marcando registros como inativos (`ativo = False`) em vez de removê-los fisicamente, o que preserva a integridade e o histórico dos dados.


## 2. Gestão de Viagens 

### 2.1. Criar Viagem

| Detalhe | Descrição |
| :--- | :--- |
| **Método HTTP** | `POST` |
| **URL** | `/travels/` |
| **Funcionalidade** | Cria um novo registro de viagem. A placa do veículo. |

**Exemplo de Requisição:**

```json
POST /travels/
Content-Type: application/json

{
    "asset_description": "Caminhão Mercedes-Benz",
    "register_number": "REG002",
    "asset_id": 102,
    "garage_name": "Garagem Sul",
    "full_distance": 350.50,
    "datetime": "2024-11-03T14:30:00Z",
    "license_plate": "XYZ9876",
    "unit_id": 20
}
```

**Exemplo de Resposta (Sucesso - Status Code `201 Created`):**

```json
{
    "success": true,
    "data": {
        "id": 2,
        "asset_description": "Caminhão Mercedes-Benz",
        "register_number": "REG002",
        "license_plate": "XYZ9876",
        "datetime": "2024-11-03T14:30:00Z"
    },
    "message": "Viagem criada com sucesso",
    "timestamp": "2024-11-03T15:00:00.000000Z"
}
```

### 2.2. Listar Viagens

| Detalhe | Descrição |
| :--- | :--- |
| **Método HTTP** | `GET` |
| **URL** | `/travels/` |
| **Funcionalidade** | Retorna uma lista paginada de viagens. Suporta filtragem, busca e ordenação. |


**Exemplo de Requisição:**

```http
GET /travels/
```

**Exemplo de Resposta (Sucesso - Status Code `200 OK`):**

```json
{
    "success": true,
    "data": [
        {
            "id": 2,
            "license_plate": "ABC123",
            "asset_description": "Carro de Serviço 1",
            "register_number": "CSV001",
            "garage_name": "Garagem Oeste",
            "full_distance": "55.70",
            "datetime": "2024-02-10T06:15:00-03:00",
            "unit_name": null,
            "total_stops": 4,
            "primary_driver": "Ana Lima"
        },
        {
            "id": 1,
            "license_plate": "ABC123",
            "asset_description": "Veículo",
            "register_number": "ABC123",
            "garage_name": "Garagem Atualizada",
            "full_distance": "120.50",
            "datetime": "2024-01-15T07:00:00-03:00",
            "unit_name": null,
            "total_stops": 0,
            "primary_driver": "Gabriel Oliveira"
        }
    ],
    "pagination": {
        "page": 1,
        "limit": 20,
        "total": 4,
        "totalPages": 1
    },
    "timestamp": "2025-11-03T03:09:46.404704+00:00"
}
```

### 2.3. Detalhes da Viagem

| Detalhe | Descrição |
| :--- | :--- |
| **Método HTTP** | `GET` |
| **URL** | `/travels/{id}/` |
| **Funcionalidade** | Retorna os detalhes completos de uma viagem específica, incluindo informações de custo (`bill`) se existirem. |

**Exemplo de Requisição:**

```http
GET /travels/1/
```

**Exemplo de Resposta (Sucesso - Status Code `200 OK`):**

```json
{
    "success": true,
    "data": {
        "id": 1,
        "license_plate": "ABC1234",
        "asset_description": "Caminhão Mercedes-Benz",
        "register_number": "REG001",
        "asset_id": 101,
        "garage_name": "Garagem Central",
        "full_distance": "500.75",
        "datetime": "2024-10-25T10:00:00Z",
        "unit_name": null,
        "unit_id": 10,
        "stops_count": 3,
        "bill": {
            "fix_cost": 150.00,
            "variable_km": 0.50,
            "total_cost": 400.38,
            "datetime": "2024-10-25T11:00:00Z"
        }
    },
    "timestamp": "2024-11-03T15:00:00.000000Z"
}
```

### 2.4. Atualizar Viagem

| Detalhe | Descrição |
| :--- | :--- |
| **Método HTTP** | `PATCH` |
| **URL** | `/travels/{id}/` |
| **Funcionalidade** | Atualiza os dados de uma viagem. |

**Exemplo de Requisição:**

```json
PATCH /travels/1/
Content-Type: application/json

{
    "asset_description": "Caminhão Mercedes-Benz - Atualizado"
}
```

**Exemplo de Resposta (Sucesso - Status Code `200 OK`):**

```json
{
    "success": true,
    "data": {
        "id": 1,
        "garage_name": "Garagem Central",
        "full_distance": 500.75,
        "license_plate": "ABC1234",
        "updated_at": "2024-11-03T15:05:00.000000Z"
    },
    "message": "Viagem atualizada com sucesso",
    "timestamp": "2024-11-03T15:05:00.000000Z"
}
```

### 2.5. Remover Viagem

| Detalhe | Descrição |
| :--- | :--- |
| **Método HTTP** | `DELETE` |
| **URL** | `/travels/{id}/` |
| **Funcionalidade** | Remove o registro de viagem. A remoção em cascata (CASCADE) também remove todas as paradas (`Stop`) e o custo (`Bill`) associados. |

**Exemplo de Requisição:**

```http
DELETE /travels/1/
```

**Exemplo de Resposta (Sucesso - Status Code `200 OK`):**

```json
{
    "success": true,
    "message": "Viagem removida com sucesso",
    "timestamp": "2024-11-03T15:06:00.000000Z"
}
```

### 2.6. Listar Paradas de uma Viagem

| Detalhe | Descrição |
| :--- | :--- |
| **Método HTTP** | `GET` |
| **URL** | `/travels/{id}/stops/` |
| **Funcionalidade** | Retorna a lista de paradas (`Stop`) associadas a uma viagem específica. |

**Exemplo de Requisição:**

```http
GET /travels/1/stops/
```

**Exemplo de Resposta (Sucesso - Status Code `200 OK`):**

```json
{
    "success": true,
    "data": [
        {
            "id": 10,
            "departure_datetime": "2024-10-25T10:00:00Z",
            "driver": "Carlos Silva",
            "departure_site": "Rua A, 123",
            "trip_time": "01:30:00",
            "trip_distance": "100.00",
            "arrival_datetime": "2024-10-25T11:30:00Z",
            "arrival_site": "Avenida B, 456",
            "travel_id": 1
        }
    ],
    "timestamp": "2024-11-03T15:07:00.000000Z"
}
```


## 3. Gestão de Custos (`/bills/`)

### 3.1. Criar Custo

| Detalhe | Descrição |
| :--- | :--- |
| **Método HTTP** | `POST` |
| **URL** | `/bills/` |
| **Funcionalidade** | Cria um novo registro de custo, associando-o a uma viagem existente. |

**Fórmula de Cálculo:** `total_cost = fix_cost + (variable_km * travel.full_distance)`

**Exemplo de Requisição:**

```json
POST /bills/
Content-Type: application/json

{
    "travel": 2,
    "fix_cost": 100.00,
    "variable_km": 0.45,
    "datetime": "2024-11-03T15:00:00Z"
}
```

**Exemplo de Resposta (Sucesso - Status Code `201 Created`):**

```json
{
    "success": true,
    "data": {
        "travel_id": 2,
        "fix_cost": 100.00,
        "variable_km": 0.45,
        "total_cost": 257.73,
        "datetime": "2024-11-03T15:00:00Z"
    },
    "message": "Custo registrado com sucesso",
    "timestamp": "2024-11-03T15:09:00.000000Z"
}
```

### 3.2. Listar Custos

| Detalhe | Descrição |
| :--- | :--- |
| **Método HTTP** | `GET` |
| **URL** | `/bills/` |
| **Funcionalidade** | Retorna uma lista paginada de custos. O filtro principal é por `travel_id`. |

**Parâmetros de Query (Filtros e Paginação):**

| Parâmetro | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `page` | `int` | Número da página a ser retornada. | `?page=1` |
| `limit` | `int` | Número de itens por página. | `?limit=20` |
| `travel_id` | `int` | Filtra custos associados a uma viagem específica. | `?travel_id=1` |

**Exemplo de Requisição:**

```http
GET /bills/?travel_id=1
```

**Exemplo de Resposta (Sucesso - Status Code `200 OK`):**

```json
{
    "success": true,
    "data": [
        {
            "travel": 1,
            "fix_cost": "150.00",
            "variable_km": "0.50",
            "total_cost": 400.38,
            "datetime": "2024-10-25T11:00:00Z",
            "travel_info": {
                "license_plate": "ABC1234",
                "full_distance": 500.75
            }
        }
    ],
    "pagination": {
        "page": 1,
        "limit": 20,
        "total": 1,
        "totalPages": 1
    },
    "timestamp": "2024-11-03T15:08:00.000000Z"
}
```

## 4. Dashboard 

### 4.1. Resumo de Viagens e Custos

Este endpoint fornece um resumo estatístico consolidado de todas as viagens e custos, permitindo a filtragem por período e unidade.

| Detalhe | Descrição |
| :--- | :--- |
| **Método HTTP** | `GET` |
| **URL** | `/travel-summary/` |
| **Funcionalidade** | Retorna métricas consolidadas (distância total, custo total, número de viagens, médias) com base nos filtros aplicados. |

**Parâmetros de Query (Filtros):**

| Parâmetro | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `start_date` | `datetime` | Filtra dados a partir desta data/hora (`datetime >= start_date`). Formato ISO 8601. | `?start_date=2024-10-01T00:00:00Z` |
| `end_date` | `datetime` | Filtra dados até esta data/hora (`datetime <= end_date`). Formato ISO 8601. | `?end_date=2024-10-31T23:59:59Z` |
| `unit_id` | `int` | Filtra dados por ID da unidade operacional. | `?unit_id=10` |

**Exemplo de Requisição:**

```http
GET /travel-summary/travel-summary/
```

**Exemplo de Resposta (Sucesso - Status Code `200 OK`):**

```json
{
    "success": true,
    "data": {
        "total_distance_km": 729.2,
        "total_cost": 163144.65,
        "total_travels": 4,
        "avg_cost_per_travel": 40786.16,
        "avg_distance_per_travel": 182.3
    },
    "timestamp": "2025-11-03T02:27:31.799013+00:00"
}
```

### 4.2. Evolução dos Custos ao Longo do Tempo

Este endpoint retorna uma série temporal que detalha a evolução dos custos (fixo, variável e total) e distância ao longo de um período.

| Detalhe | Descrição |
| :--- | :--- |
| **Método HTTP** | `GET` |
| **URL** | `/cost-evolution/` |
| **Funcionalidade** | Retorna dados agregados de custo e distância agrupados por dia, semana ou mês, permitindo a visualização da evolução. |

**Parâmetros de Query (Filtros e Agregação):**

| Parâmetro | Tipo | Descrição | Padrão | Exemplo |
| :--- | :--- | :--- | :--- | :--- |
| `period` | `string` | Nível de agregação: `day`, `week` ou `month`. | `month` | `?period=day` |
| `start_date` | `datetime` | Filtra dados a partir desta data/hora. Se omitido, usa o `limit` para calcular o início. | (Calculado) | `?start_date=2024-01-01T00:00:00Z` |
| `end_date` | `datetime` | Filtra dados até esta data/hora. | (Atual) | `?end_date=2024-12-31T23:59:59Z` |

**Exemplo de Requisição:**

```http
GET /cost-evolution/?period=month&limit=3
```

**Exemplo de Resposta (Sucesso - Status Code `200 OK`):**

```json
{
    "success": true,
    "data": [
        {
            "period": "2024-08",
            "period_full_date": "2024-08-01T00:00:00+00:00",
            "total_cost": 2500.00,
            "fix_cost": 1000.00,
            "variable_cost": 1500.00,
            "total_distance_km": 3000.00,
            "total_bills": 50,
            "avg_cost": 50.00
        },
        {
            "period": "2024-09",
            "period_full_date": "2024-09-01T00:00:00+00:00",
            "total_cost": 3000.00,
            "fix_cost": 1200.00,
            "variable_cost": 1800.00,
            "total_distance_km": 3600.00,
            "total_bills": 60,
            "avg_cost": 50.00
        },
        {
            "period": "2024-10",
            "period_full_date": "2024-10-01T00:00:00+00:00",
            "total_cost": 2800.00,
            "fix_cost": 1100.00,
            "variable_cost": 1700.00,
            "total_distance_km": 3400.00,
            "total_bills": 55,
            "avg_cost": 50.91
        }
    ],
    "params": {
        "period": "month",
        "limit": 3,
        "results_count": 3
    },
    "timestamp": "2024-11-03T16:05:00.000000Z"
}
```
## Conclusão

  Por fim, a presente documentação consolida a estrutura, o funcionamento e as principais funcionalidades desenvolvidas em Django, descrevendo de forma detalhada os endpoints voltados à gestão de usuários, viagens e custos, bem como os recursos de dashboard para análise e acompanhamento de métricas operacionais.

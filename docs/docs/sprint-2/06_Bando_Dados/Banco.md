---
sidebar_position: 1
slug: /sprint-2/banco-de-dados/arquitetura
description: "Descrição da arquitura do banco de dados"
---

# Documentação do Banco de Dados

&ensp; Esta seção apresenta a estrutura lógica e relacional do banco de dados, descrevendo como as informações são armazenadas, interligadas e utilizadas pelo sistema. O objetivo é garantir clareza na compreensão das entidades e de seus relacionamentos.

## 1. Modelo de Dados

&ensp; Aqui são detalhadas as tabelas que compõem o banco, incluindo seus campos, tipos, funções e vínculos entre si. Essa visão facilita o entendimento da arquitetura e serve de referência para manutenção e evolução do sistema.

### **Tabela: `TRAVEL`**

&ensp; Representa uma viagem completa, composta por uma ou mais paradas (`STOP`).

| Campo               | Tipo     | Descrição                                                      | Exemplo                        |
| ------------------- | -------- | -------------------------------------------------------------- | ------------------------------ |
| `id`                | PK (int) | Identificador único da viagem.                                 | `1`                            |
| `asset_description` | string   | Descrição completa do ativo (veículo), geralmente concatenada. | `"Glória\|3803\|GDP-4J68-DVR"` |
| `register_number`   | string   | Número de registro do ativo.                                   | `"GDP4J68"`                    |
| `asset_id`          | int      | Identificação interna do ativo (não é FK).                     | `46`                           |
| `garage_name`       | string   | Nome da garagem de origem do ativo.                            | `"Teodoro Sampaio"`            |
| `full_distance`     | decimal  | Distância total percorrida na viagem (km).                     | `10,94`                        |
| `datetime`          | datetime | Data e hora da viagem no padrão ISO8601.                       | `2025-09-29T13:45:30-03:00`    |
| `license_plate`     | string   | Placa do veículo.                                              | `ABC-1D23`                     |
| `unit_id`           | FK (int) | Unidade operacional responsável.                               | `1`                            |
| `occupancy_percentage` | decimal | Ocupação média na viagem (%).                                  | `90,00`                        |

---

### **Tabela: `STOP`**

&ensp; Registra as paradas dentro de uma viagem (`TRAVEL`).

| Campo                | Tipo     | Descrição                               | Exemplo                                           |
| -------------------- | -------- | --------------------------------------- | ------------------------------------------------- |
| `id`                 | PK (int) | Identificador único da parada.          | `100`                                             |
| `departure_datetime` | datetime | Data e hora de saída (ISO8601).         | `2025-09-29T14:00:00-03:00`                       |
| `driver`             | string   | Nome do motorista responsável.          | `DONIZETE DE SOUZA NEVES`                         |
| `departure_site`     | string   | Endereço/local de saída.                | `Av. Gen. Euclides, Prof. Murilo - SP, 19260-000` |
| `trip_time`          | time     | Tempo de condução.                      | `01:15:30`                                        |
| `trip_distance`      | decimal  | Distância percorrida nesta parada (km). | `51,66`                                           |
| `arrival_datetime`   | datetime | Data e hora de chegada (ISO8601).       | `2025-09-29T15:15:30-03:00`                       |
| `arrival_site`       | string   | Endereço/local de chegada.              | `Av. Gen. Euclides, Prof. Murilo - SP, 19260-000` |
| `travel_id`          | FK (int) | Referência para a viagem (`TRAVEL.id`). | `1`                                               |

---

### **Tabela: `BILL`**

&ensp; Tabela de custos associados a uma viagem.

| Campo         | Tipo     | Descrição                               | Exemplo                     |
| ------------- | -------- | --------------------------------------- | --------------------------- |
| `fix_cost`    | decimal  | Custo fixo da viagem.                   | `40.314,14`                 |
| `variable_km` | decimal  | Custo variável por quilômetro.          | `2,73`                      |
| `travel_id`   | FK (int) | Referência para a viagem (`TRAVEL.id`). | `1`                         |
| `datetime`    | datetime | Data de geração da medição (ISO8601).   | `2025-09-29T14:10:00-03:00` |

---

### **Tabela: `RAW_LAYER`**

&ensp; Dados crus recebidos diretamente da API de telemetria.

| Campo       | Tipo     | Descrição                                           | Exemplo                          |
| ----------- | -------- | --------------------------------------------------- | -------------------------------- |
| `url`       | string   | Caminho no bucket do arquivo bruto (XLSX).          | `2025-09-29T13:45:30-03:00.xlsx` |
| `travel_id` | FK (int) | Referência para a viagem (`TRAVEL.id`).             | `1`                              |
| `datetime`  | datetime | Data e hora de ingestão dos dados brutos (ISO8601). | `2025-09-29T13:45:30-03:00`      |

---

### **Tabela: `STAGING_LAYER`**

&ensp; Dados tratados, após processamento e limpeza.

| Campo          | Tipo     | Descrição                                          | Exemplo                             |
| -------------- | -------- | -------------------------------------------------- | ----------------------------------- |
| `url`          | string   | Caminho no bucket do arquivo processado (Parquet). | `2025-10-13T09:20:50-07:00.parquet` |
| `raw_layer_id` | FK (int) | Referência para os dados crus (`RAW_LAYER.id`).    | `10`                                |
| `datetime`     | datetime | Data e hora de processamento/tratamento (ISO8601). | `2025-10-13T09:20:50-07:00`         |

---

### **Tabela: `UNIT`**

&ensp; Unidades operacionais (ex.: UAT, USL).

| Campo         | Tipo     | Descrição                         | Exemplo |
| ------------- | -------- | --------------------------------- | ------- |
| `id`          | PK (int) | Identificador único da unidade.   | `1`     |
| `name`        | string   | Sigla/nome da unidade.            | `UAT`   |
| `description` | string   | Descrição opcional da unidade.    | `...`   |

---

### **Tabela: `OCCURRENCE_CATEGORY`**

&ensp; Categorias de ocorrências.

| Campo | Tipo     | Descrição                     | Exemplo      |
| ----- | -------- | ----------------------------- | ------------ |
| `id`  | PK (int) | Identificador da categoria.   | `1`          |
| `name`| string   | Nome da categoria.            | `Manutenção` |

---

### **Tabela: `OCCURRENCE`**

&ensp; Registro de ocorrências relacionadas às viagens.

| Campo        | Tipo     | Descrição                                      | Exemplo                 |
| ------------ | -------- | ---------------------------------------------- | ----------------------- |
| `id`         | PK (int) | Identificador da ocorrência.                   | `10`                    |
| `travel_id`  | FK (int) | Referência para a viagem (`TRAVEL.id`).        | `1`                     |
| `unit_id`    | FK (int) | Unidade da ocorrência (`UNIT.id`).             | `1`                     |
| `carrier_name` | string | Transportadora relacionada.                    | `Sertran`               |
| `category_id`| FK (int) | Categoria (`OCCURRENCE_CATEGORY.id`).          | `2`                     |
| `root_cause` | text     | Causa raiz.                                    | `Falta de manutenção`   |
| `description`| text     | Descrição detalhada.                           | `...`                   |
| `datetime`   | datetime | Data/hora do evento (ISO8601).                 | `2025-09-29T16:30:00`   |

---

## 2. Organização do Bucket (S3)

&ensp; Esta parte explica como os dados são organizados e versionados dentro do armazenamento em nuvem, distinguindo as camadas bruta (raw) e tratada (staging). A estrutura garante rastreabilidade e eficiência no fluxo de ingestão e processamento dos dados.

### Estrutura de diretórios

```
s3://agro-bucket/
│
├── raw/       # Camada bruta - arquivos XLSX recebidos da API
│   └── 2025-09-29T13:45:30-03:00.xlsx
│
└── staging/   # Camada de tratamento - arquivos Parquet processados
    └── 2025-10-13T09:20:50-07:00.parquet
```

### Regras

* **RAW Layer (`/raw`)**: contém os dados exatamente como recebidos da API, sem transformação.
* **Staging Layer (`/staging`)**: contém os dados tratados (formato parquet), prontos para análises ou cargas em data warehouse.
* Nome dos arquivos segue o padrão:

  ```
  YYYY-MM-DDTHH:MM:SS±hh:mm.{extensão}
  ```

  * `.xlsx` → dados crus (raw)
  * `.parquet` → dados tratados (staging)
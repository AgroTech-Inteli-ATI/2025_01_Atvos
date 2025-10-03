
# 📖 Documentação do Banco de Dados e Organização do Bucket

## 1. Modelo de Dados

### **Tabela: `TRAVEL`**

Representa uma viagem completa, composta por uma ou mais paradas (`STOP`).

| Campo               | Tipo     | Descrição                                                      | Exemplo                        |
| ------------------- | -------- | -------------------------------------------------------------- | ------------------------------ |
| `id`                | PK (int) | Identificador único da viagem.                                 | `1`                            |
| `asset_description` | string   | Descrição completa do ativo (veículo), geralmente concatenada. | `"Glória\|3803\|GDP-4J68-DVR"` |
| `register_number`   | string   | Número de registro do ativo.                                   | `"GDP4J68"`                    |
| `asset_id`          | int      | Identificação interna do ativo (não é FK).                     | `46`                           |
| `garage_name`       | string   | Nome da garagem de origem do ativo.                            | `"Teodoro Sampaio"`            |
| `full_distance`     | decimal  | Distância total percorrida na viagem (km).                     | `10,94`                        |
| `datetime`          | datetime | Data e hora da viagem no padrão ISO8601.                       | `2025-09-29T13:45:30-03:00`    |

---

### **Tabela: `STOP`**

Registra as paradas dentro de uma viagem (`TRAVEL`).

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

Tabela de custos associados a uma viagem.

| Campo         | Tipo     | Descrição                               | Exemplo                     |
| ------------- | -------- | --------------------------------------- | --------------------------- |
| `fix_cost`    | decimal  | Custo fixo da viagem.                   | `40.314,14`                 |
| `variable_km` | decimal  | Custo variável por quilômetro.          | `2,73`                      |
| `travel_id`   | FK (int) | Referência para a viagem (`TRAVEL.id`). | `1`                         |
| `datetime`    | datetime | Data de geração da medição (ISO8601).   | `2025-09-29T14:10:00-03:00` |

---

### **Tabela: `RAW_LAYER`**

Dados crus recebidos diretamente da API de telemetria.

| Campo       | Tipo     | Descrição                                           | Exemplo                          |
| ----------- | -------- | --------------------------------------------------- | -------------------------------- |
| `url`       | string   | Caminho no bucket do arquivo bruto (XLSX).          | `2025-09-29T13:45:30-03:00.xlsx` |
| `travel_id` | FK (int) | Referência para a viagem (`TRAVEL.id`).             | `1`                              |
| `datetime`  | datetime | Data e hora de ingestão dos dados brutos (ISO8601). | `2025-09-29T13:45:30-03:00`      |

---

### **Tabela: `STAGING_LAYER`**

Dados tratados, após processamento e limpeza.

| Campo          | Tipo     | Descrição                                          | Exemplo                             |
| -------------- | -------- | -------------------------------------------------- | ----------------------------------- |
| `url`          | string   | Caminho no bucket do arquivo processado (Parquet). | `2025-10-13T09:20:50-07:00.parquet` |
| `raw_layer_id` | FK (int) | Referência para os dados crus (`RAW_LAYER.id`).    | `10`                                |
| `datetime`     | datetime | Data e hora de processamento/tratamento (ISO8601). | `2025-10-13T09:20:50-07:00`         |

---

## 2. Organização do Bucket (S3)

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



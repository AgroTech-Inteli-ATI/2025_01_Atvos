# Documento de Arquitetura de Solução

## 1. Introdução e Visão Geral da Arquitetura

**Objetivo:** O propósito principal desta arquitetura é estabelecer um fluxo de dados robusto e escalável para monitoramento de sistemas, processamento de dados em larga escala e visualização de insights de negócios. Além disso, ela foi projetada para se integrar de forma compatível com a arquitetura atual dos sistemas da Atvos.

<p style={{ textAlign: "center" }}>Figura 1: Arquitetura da Solução Atualizada</p>

<div style={{ margin: 25, textAlign: "center" }}>
  <img src={require("../../static/img/arquitetura-atualizada.jpeg").default} style={{width: 800}} />
</div>

<p style={{ textAlign: "center" }}>Fonte: Produzida pelos Autores (2025)</p>


**Componentes Principais:**

*   **Monitoramento/Visualização:** Prometheus e Grafana.
*   **Plataforma de Dados (Google Cloud):** BigQuery, Cloud Storage, Dataflow/Composer.
*   **Dashboard (Business Intelligence):** Power BI.

## 2. Camada de Monitoramento e Observabilidade

### Prometheus

*   **Função:** O Prometheus é um sistema de monitoramento e alerta de código aberto que coleta e armazena métricas como séries temporais. Ele é projetado para monitorar a saúde e a performance de serviços e sistemas, coletando dados de *endpoints* configurados (exporters) em intervalos regulares.
*   **Interconexões:** O Prometheus expõe os dados coletados para que possam ser consumidos por ferramentas de visualização.

### Grafana

*   **Função:** O Grafana é uma plataforma de código aberto para visualização e análise de dados. Ele se conecta a diversas fontes de dados para criar dashboards interativos e em tempo real, permitindo a criação de gráficos, alertas e uma análise visual detalhada das métricas coletadas.
*   **Fontes de Dados (Datasources):** A principal fonte de dados para o Grafana nesta arquitetura é o Prometheus, de onde ele extrai as métricas de monitoramento para exibição. Potencialmente, também pode se conectar ao BigQuery para visualizar dados já processados.

## 3. Google Cloud Platform (GCP) - Plataforma de Dados e ETL

### BigQuery (Data Warehouse)

*   **Função:** O BigQuery é o Data Warehouse (DW) central desta arquitetura. Trata-se de um serviço totalmente gerenciado, *serverless* e altamente escalável, projetado para armazenar e analisar grandes volumes de dados utilizando SQL. Ele serve como o repositório analítico principal, onde os dados transformados são armazenados para consulta e análise.
*   **Fontes de Ingestão:** Os dados chegam ao BigQuery principalmente através dos pipelines de ETL orquestrados pelo Dataflow e/ou Composer, que processam os dados brutos armazenados no Cloud Storage.

### Cloud Storage (Data Lake/Staging)

*   **Função:** O Google Cloud Storage é utilizado como um repositório de objetos para armazenar grandes volumes de dados não estruturados ou semi-estruturados. Nesta arquitetura, ele atua como uma *staging area* (área de preparação) ou *data lake*, onde os dados brutos são ingeridos antes de serem processados e carregados no BigQuery.
*   **Interconexões:** O Cloud Storage é a fonte de dados para os processos de ETL executados pelo Dataflow/Composer e também pode ser o destino para backups ou exportações de dados do BigQuery.

### Power BI (Business Intelligence/Visualização)

*   **Função:** O Power BI é a ferramenta de Business Intelligence utilizada para a camada final de visualização e análise de negócios. Ele se conecta aos dados consolidados para criar relatórios e dashboards interativos que permitem aos usuários de negócio explorar os dados e extrair insights valiosos.
*   **Acesso a Dados:** A principal fonte de dados para o Power BI nesta arquitetura é o BigQuery, que oferece os dados já limpos, transformados e prontos para análise de negócio.

### Dataflow / Composer (ETL/Orquestração)

*   **Função:** Esta camada, composta pelo Dataflow e/ou Composer, é responsável por todo o processo de **ETL (Extração, Transformação e Carga)**.
    *   **Dataflow:** É um serviço totalmente gerenciado para processamento de dados em lote e em tempo real. Ele executa os pipelines que transformam os dados brutos do Cloud Storage.
    *   **Composer:** É um serviço de orquestração de fluxos de trabalho totalmente gerenciado, construído sobre o Apache Airflow. Ele é usado para agendar, monitorar e gerenciar os pipelines de ETL de forma programática e confiável.
*   **Interconexões:** Essa camada lê os dados do Cloud Storage, aplica as transformações necessárias e carrega o resultado no BigQuery.

## 4. Fluxo de Dados e Processamento (End-to-End)

O fluxo de dados de ponta a ponta nesta arquitetura pode ser descrito no seguinte cenário:

1.  **Origem:** Os dados são gerados por aplicações, como os contêineres hospedados na Vercel, ou por sistemas de infraestrutura. Métricas de performance e saúde são expostas através de *exporters*.
2.  **Coleta de Métricas:** O **Prometheus** coleta ativamente as métricas desses sistemas em tempo real e as armazena em seu banco de dados de séries temporais. O **Grafana** se conecta ao Prometheus para visualizar essas métricas em dashboards de monitoramento técnico.
3.  **Ingestão de Dados Brutos:** Paralelamente, dados brutos (logs, eventos, dados de aplicação) são enviados e armazenados no **Google Cloud Storage**, que atua como nosso Data Lake.
4.  **Processamento (ETL):** O **Cloud Composer** aciona um pipeline de **Dataflow** de forma agendada. Este pipeline extrai os dados brutos do Cloud Storage, os transforma (limpando, enriquecendo, agregando) e os carrega em tabelas estruturadas no **BigQuery**.
5.  **Análise e Visualização de Negócios:** O **Power BI** se conecta diretamente ao **BigQuery** para consumir os dados já processados. Os analistas e gestores utilizam o Power BI para criar relatórios e dashboards que fornecem insights estratégicos para o negócio.

## 5. Conclusão

Esta arquitetura oferece uma solução completa que é compatível com a arquitetura atual dos sistemas da Atvos. Nesse sentido, a utilização dos serviços gerenciados da Google Cloud, como BigQuery e Dataflow, permite que a plataforma escale automaticamente de acordo com a demanda, operando em um modelo de pagamento por uso. Além disso, o uso de Dataflow e Composer para os processos de ETL garante que a transformação e o movimento dos dados sejam robustos, escaláveis e fáceis de gerenciar. Por fim, a integração com o Power BI sobre os dados centralizados no BigQuery capacita a organização a tomar decisões mais inteligentes e baseadas em dados, atendendo as necessidades de análise da Atvos.
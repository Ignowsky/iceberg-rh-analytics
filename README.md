#  🧊 Projeto Iceberg RH: People Analytics & Data Simulator

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![dbt](https://img.shields.io/badge/dbt-Data_Build_Tool-FF694B)
![Airflow](https://img.shields.io/badge/Apache_Airflow-Orchestration-017CEE)
![BigQuery](https://img.shields.io/badge/BigQuery-Data_Warehouse-4285F4)
![Power BI](https://img.shields.io/badge/Power_BI-Semantic_Model-F2C811)


## Visão Geral (O Produto Entregavel)
O **Iceberg RH** é uma arquitetura de dados *End-to-End* que simula, a ingestão, transformação e analise de dados de um ecossistema corporativo completo (ATS, Core HR, LMS e Ponto).
O Objetivo do projeto é substituir relatórios transacionais reativos por uma de **Inteligência Preditiva** e a **Modelagem Geospacial** no Power BI.

- **prj-iceberg-rh-prd** (Nosso projeto isolado no bigquery)
- BigQuery Datasets:
    - iceberg_rh_bronze (Dados brutos ingeridos, sem tratamentos)
    - iceberg_rh_silver (Dados limpos e tipados pelo dbt)
    - iceberg_rh_gold (O StarSchema  final que o Power BI vai consumir)
- Nome do Repositório no Github: ``iceberg-rh-analytics``

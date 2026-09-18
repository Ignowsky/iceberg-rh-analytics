# 🧊 Projeto Iceberg RH: People Analytics & Data Simulator

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![pytest](https://img.shields.io/badge/pytest-Quality_Gates-0A9EDC)
![dbt](https://img.shields.io/badge/dbt-Data_Build_Tool-FF694B)
![BigQuery](https://img.shields.io/badge/BigQuery-Data_Warehouse-4285F4)
![Power BI](https://img.shields.io/badge/Power_BI-Semantic_Model-F2C811)

> *"A ponta de um iceberg apenas mostra o que aconteceu, mas é o que está submerso que demonstra o verdadeiro padrão de comportamento."*

## 🎯 Visão Geral (O Produto Entregável)
O **Iceberg RH** é uma arquitetura de dados *End-to-End* que simula a geração, ingestão, transformação e análise de dados de um ecossistema corporativo completo (ATS, Core HR, LMS, Avaliação de Desempenho e Ponto). 

O objetivo do projeto é substituir relatórios transacionais e planilhas reativas por um modelo de **Inteligência Preditiva**, **Análise de Sobrevivência (Turnover)** e **Modelagem Dimensional** escalável, culminando em um Data Mart consumido pelo Power BI.

---

## 🏗️ Arquitetura e Infraestrutura de Dados

O projeto adota o paradigma moderno de **ELT (Extract, Load, Transform)**, utilizando o Google Cloud Platform (GCP) como infraestrutura principal e o dbt para orquestração da modelagem.

- **Projeto GCP:** `prj-iceberg-rh-prd`
- **Repositório GitHub:** `iceberg-rh-analytics`
- **Data Warehouse (BigQuery Datasets):**
  - 🥉 `iceberg_rh_bronze`: *Data Lake* relacional. Recebe os dados brutos (Raw) via ingestão automatizada (Arquivos Parquet/JSON imutáveis).
  - 🥈 `iceberg_rh_silver`: Camada de padronização, tipagem estrita e chaves criptografadas (Surrogate Keys) gerenciadas pelo dbt.
  - 🥇 `iceberg_rh_gold`: Data Mart final em *Star Schema* otimizado para o motor VertiPaq do Power BI.

---

## 🚀 Estado Atual do Desenvolvimento

O pipeline já está operando de ponta a ponta até a subcamada de *Staging* (Silver), garantindo governança estrutural e qualidade dos dados.

### 1. Motor Estocástico de Geração de Dados (Python)
Desenvolvemos um simulador de RH altamente realista que não gera apenas "dados aleatórios", mas simula comportamentos corporativos ao longo de 16 anos (2010 a 2026):
- **Matriz 9-Box e Curva de Gauss:** Distribuição realista de desempenho e potencial, abandonando *scores* lineares.
- **Motor de Turnover Avançado:** Simulação de crises econômicas (*Hiring Freezes*), demissões involuntárias por baixo desempenho e fuga de talentos travados no teto salarial.
- **Tracking Histórico (Snapshots):** Geração de fotografias mensais de toda a base de colaboradores ativos para cálculo preciso de *Headcount* e *Tenure*.

### 2. Quality Gates e Orquestração (DataOps)
- Implementação de arquitetura *Fail-Fast* no orquestrador principal (`main.py`).
- Uso programático do **pytest** para validar regras de negócio rígidas (ex: CPFs únicos, ausência de salários negativos, datas lógicas de demissão) *antes* de autorizar a ingestão na nuvem, protegendo o Data Warehouse contra corrupção silenciosa.

### 3. Modelagem Analytics Engineering (dbt)
- Materialização de **10 views de Staging** no BigQuery.
- Desacoplamento arquitetural: geração de **Surrogate Keys** utilizando a função nativa `FARM_FINGERPRINT` no banco de dados, em vez de onerar o script Python de extração.
- Tipagem estrita (`INT64`, `FLOAT64`, `DATE`) garantindo compatibilidade nativa de *Time Intelligence* para o modelo semântico.
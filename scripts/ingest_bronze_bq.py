"""
Projeto Iceberg RH: People Analytics & Data Simulator
Módulo: Ingestão Camada Bronze no Google Bigquery
Descrição: Realiza o upload 1:1 (As-Is) dos arquivos Parquet e JSON locais
para o Data Warehouse, garatindo a imutabilidade da origem (ELT)
"""
# Importações de bibliotecas internas
import os
import json
import sys
# importações de bibliotecas externas
import pandas as pd
# importações de bibliotecas do Google Cloud
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv
# Importações de bibliotecas de logging
from loguru import logger

# Carregando as váriaveis de ambiente do arquivo .env
load_dotenv()

# Configuração do Diretório base do Projeto e Gcp
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_DATASET_BRONZE = os.getenv("BQ_DATASET_BRONZE")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
BASE_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw')
KEY_PATH = os.path.join(PROJECT_ROOT, 'gcp_key.json')
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')

# Configuração do loguru
logger.remove()  # Remove o logger padrão
logger.add(sys.stdout, colorize = True, format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>", level = "INFO")
logger.add(os.path.join(LOG_DIR, "hr_pipeline_{time:YYYY-MM-DD}.log"), rotation = "10 MB", retention = "7 days", level = "INFO")

# Configuração do cliente Bigquery
try:
    credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
    client = bigquery.Client(credentials=credentials, project=GCP_PROJECT_ID)
except FileNotFoundError:
    logger.error(f"Arquivo de credenciais não encontrado em: {KEY_PATH}")
    raise

def ingest_parquet_native(file_name: str, table_name: str):
    """
    Função para a ingestão nativa de arquivos parquet no bigquery
    Args:
        file_name (str): Nome do arquivo parquet a ser ingerido
        table_name (str): Nome da tabela destino no Bigquery
    """
    
    file_path = os.path.join(BASE_DIR, file_name)
    table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET_BRONZE}.{table_name}"
    
    job_config = bigquery.LoadJobConfig(
        source_format = bigquery.SourceFormat.PARQUET,
        write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect = True
    )
    
    logger.info(f"[INFO] - Iniciando a ingestão do arquivo {file_name} para a tabela {table_id}")
    with open(file_path, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_id, job_config = job_config)
    
    job.result()
    logger.success(f"[SUCCESS] - Ingestão do arquivo {file_name} para a tabela {table_id} concluída com sucesso.")
    
def ingest_json_native(file_name: str, table_name: str):
    """
    Função para a ingestão nativa de arquivos JSON no Bigquery utilizando a lib
    pandas para leitura do arquivo e conversão para dataframe, garantindo a consistência de tipos.
    Args:
        file_name (str): Nome do arquivo JSON a ser ingerido
        table_name (str): Nome da tabela destino no Bigquery
    """
    
    file_path = os.path.join(BASE_DIR, file_name)
    table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET_BRONZE}.{table_name}"
    
    logger.info(f"[INFO] - Iniciando a ingestão do arquivo {file_name} para a tabela {table_id}")
    
    with open(file_path, "r", encoding = "utf-8") as f:
        data = json.load(f)
        
    df = pd.DataFrame(data)
    
    # Convertendo os tipos complexos presentes no json para listas e dicionarios
    df['dependentes'] = df['dependentes'].apply(json.dumps)
    
    job_config = bigquery.LoadJobConfig(
        write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect = True
    )
    
    job = client.load_table_from_dataframe(df, table_id, job_config = job_config)
    job.result()
    
    logger.success(f"[SUCCESS] - Ingestão do arquivo {file_name} para a tabela {table_id} concluída com sucesso.")
    
    
def run_bronze_ingestion():
    """
    Função principal para realizar a ingestão dos arquivos da camada raw para a camada bronze no Bigquery.
    """
    logger.info(f"[INFO] - Iniciando a ingestão da Camada Bronze no Bigquery, Target Dataset: {BQ_DATASET_BRONZE}")
    
    arquivos_parquet = {
        "Dim_Estrutura.parquet": "Dim_Estrutura",
        "Dim_Cargos.parquet": "Dim_Cargos",
        "Fato_Contratos.parquet": "Fato_Contratos",
        "Fato_Ponto_Mensal.parquet": "Fato_Ponto",
        "Fato_Movimentacoes.parquet": "Fato_Movimentacoes",
        "Fato_Pesquisa_Clima.parquet": "Fato_Pesquisa_Clima",
        "Fato_Avaliacao_9box.parquet": "Fato_Avaliacao_9box",
        "Fato_Snapshot_Mensal.parquet": "Fato_Snapshot_Mensal",
        "Fato_Requisicoes_Vagas.parquet": "Fato_Requisicoes_Vagas"
    }
    
    for arquivo, tabela in arquivos_parquet.items():
        ingest_parquet_native(arquivo, tabela)
        
    ingest_json_native("Dim_Pessoas.json", "Dim_Pessoas")
    logger.info(f"[INFO] - Ingestão da Camada Bronze Concluída com sucesso, Target Dataset: {BQ_DATASET_BRONZE}")
    
    
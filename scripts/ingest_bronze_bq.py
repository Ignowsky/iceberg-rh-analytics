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
# importações de bibliotecas do Databricks
from databricks.sdk import WorkspaceClient
from databricks.sql import connect as sql_connect
from dotenv import load_dotenv
# Importações de bibliotecas de logging
from loguru import logger

# Carregando as váriaveis de ambiente do arquivo .env
load_dotenv()

# Configuração das variáveis de ambiente do Databricks
DBX_HOST = os.getenv("DATABRICKS_HOST")
DBX_TOKEN = os.getenv("DATABRICKS_TOKEN")
DBX_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
CATALOG = os.getenv("DBX_CATALOG")
SCHEMA = os.getenv("DBX_SCHEMA_BRONZE")
VOLUME = os.getenv("DBX_VOLYME")

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
    w = WorkspaceClient(
        host = DBX_HOST,
        token = DBX_TOKEN
    )
except Exception as e:
    logger.error(f"[ERROR] - Falha ao autenticar no Databricks Workspace. {e}")

def execute_databricks_sql(query: str):
    """
    Executa um comando SQL diretamente no motor Photon do Databricks
    """
    
    with sql_connect(server_hostname = DBX_HOST, http_path = DBX_HTTP_PATH, access_token = DBX_TOKEN) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            

def upload_to_volume(local_path: str, file_name: str) -> str:
    """
    Realiza o upload do arquivo físico para o Unity Catalog Volume.
    """
    volume_path = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}/{file_name}"
    logger.info(f"[INFO] - Realizando o upload do arquivo físico para o volume: {volume_path}")
    
    with open(local_path, "rb") as f:
        w.files.upload(volume_path, f, overwrite = True)
    
    return volume_path
    

def ingest_parquet_native(file_name: str, table_name: str):
    """
    Função para a ingestão nativa de arquivos parquet no bigquery
    Args:
        file_name (str): Nome do arquivo parquet a ser ingerido
        table_name (str): Nome da tabela destino no Bigquery
    """
    
    local_path = os.path.join(BASE_DIR, file_name)
    table_full_name = f"{CATALOG}.{SCHEMA}.{table_name}"
    
    volume_path = upload_to_volume(local_path, file_name)
    
    logger.info(f"[INFO] - Realizando a materialização das tabelas deltas: {table_full_name}")
    query = f"""
        CREATE OR REPLACE TABLE {table_full_name}
        AS SELECT *
           FROM parquet.`{volume_path}`
    """
    
    execute_databricks_sql(query)
    logger.success(f"[SUCCESS] - Tabela {table_full_name} ingerida com sucesso na camada raw")
    
    
def ingest_json_native(file_name: str, table_name: str):
    """
    Função para a ingestão nativa de arquivos JSON no Bigquery utilizando a lib
    pandas para leitura do arquivo e conversão para dataframe, garantindo a consistência de tipos.
    Args:
        file_name (str): Nome do arquivo JSON a ser ingerido
        table_name (str): Nome da tabela destino no Bigquery
    """
    local_path = os.path.join(BASE_DIR, file_name)
    temp_parquet_path = os.path.join(BASE_DIR, f"temp_{table_name}.parquet")
    table_full_name = f"{CATALOG}.{SCHEMA}.{table_name}"
    
    logger.info(f"[INFO] - Tratando as complexidades do JSON localmente.")
    
    with open(local_path, "r", encoding = "utf-8") as f:
        data = json.load(f)
        
    df = pd.DataFrame(data)
    df['dependentes'] = df['dependentes'].apply(json.dumps)
    
    # Salvando temporariamente como parquet pra manter a tipagem
    df.to_parquet(temp_parquet_path, engine = "pyarrow", index = False)
    
    volume_path = upload_to_volume(temp_parquet_path, f"{table_name}.parquet")
    
    query = f"""
        CREATE OR REPLACE TABLE {table_full_name}
        SELECT *
        FROM parquet.`{volume_path}`
    """
    
    execute_databricks_sql(query)
    
    os.remove(temp_parquet_path)
    logger.success(f"[SUCCESS - Tabela {table_full_name} ingerida com sucesso na camada raw")
    
    
    
def run_bronze_ingestion():
    """
    Função principal para realizar a ingestão dos arquivos da camada raw para a camada bronze no Bigquery.
    """
    logger.info(f"[INFO] - Iniciando a ingestão da Camada raw no Databricks Catalogo Target: {CATALOG}")
    
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
    logger.info(f"[INFO] - Ingestão da Camada raw concluída Catalogo target: {CATALOG}")
    
    
"""
Projeto Iceberg RH: People Analytics & Data Simulator
Módulo: Orquestrador Principal (Entrypoint)
Descrição: Gerencia o Fluxo completo do pipeline (Geração -> Qualidade -> Ingestão)
e garante a execução sequencial das etapas, com logs detalhados e tratamento de erros.
"""
import os
import sys
from loguru import logger
from scripts.ingest_bronze_bq import run_bronze_ingestion

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
BASE_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw')
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')

# Configuração do loguru
logger.remove()  # Remove o logger padrão
logger.add(sys.stdout, colorize = True, format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>", level = "INFO")
logger.add(os.path.join(LOG_DIR, "hr_pipeline_{time:YYYY-MM-DD}.log"), rotation = "10 MB", retention = "7 days", level = "INFO")

def main():
    
    logger.info("[INFO] - Iniciando o Orquestrador Principal do Projeto Iceberg RH")
    
    #  Etapa 1: Geração de Dados (Conectar futuramente)
    # run_data_generation()
    
    #  Etapa 2: Validação de Qualidade de Dados (Conectar futuramente)
    # run_data_quality_tests()
    
    # etapa 3: Ingestão de Dados para o Bigquery (Camada Bronze)
    logger.info("[INFO] - Iniciando a Ingestão de Dados para o Bigquery (Camada Bronze)")
    run_bronze_ingestion()
    
    logger.success("[SUCCESS] - Geração de Dados, validação de testes e ingestão de dados concluídas com sucesso.")
    
if __name__ == "__main__":
    main()

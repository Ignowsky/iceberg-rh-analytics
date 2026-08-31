"""
Projeto Iceberg RH: People Analytics & Data Simulator

Módulo: Testes de Qualidade de Dados (Data Quality - Camada Brozne)
Descrição: Validações automatizadas via Pytests para garantir a integridade estrutural,
consistência de tipos e integridade referencial dos arquivos gerados na Camada Bronze
"""
import os
import pytest
import pandas as pd
import json

# Definição inicial do diretório alvo dos arquivos Bronze
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
BASE_DIR = os.path.join(PROJECT_ROOT, 'data', 'bronze')

@pytest.fixture(scope = "module")
def load_bronze_data():
    """
    Fixture do Pytest para carregar os datasets uma única vez para todos os testes do módulo.
    """
    try:
        data = {
            "estrutura": pd.read_parquet(os.path.join(BASE_DIR, "Dim_Estrutura.parquet")),
            "cargos": pd.read_parquet(os.path.join(BASE_DIR, "Dim_Cargos.parquet")),
            "contratos": pd.read_parquet(os.path.join(BASE_DIR, "Fato_Contratos.parquet")),
            "snapshots": pd.read_parquet(os.path.join(BASE_DIR, "Fato_Snapshot_Mensal.parquet")),
            "movimentacoes": pd.read_parquet(os.path.join(BASE_DIR,"Fato_Movimentacoes.parquet")),
            "requisicoes": pd.read_parquet(os.path.join(BASE_DIR, "Fato_Requisicoes_Vagas.parquet")),
            "Dim_Cargos": pd.read_parquet(os.path.join(BASE_DIR, "Dim_Cargos.parquet"))
        }
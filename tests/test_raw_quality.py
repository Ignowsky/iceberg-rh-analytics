"""
Projeto Iceberg RH: People Analytics & Data Simulator

Módulo: Testes de Qualidade de Dados (Data Quality - Camada Brozne)
Descrição: Validações automatizadas via Pytests para garantir a integridade estrutural,
consistência de tipos e integridade referencial dos arquivos gerados na Camada raw
"""
import os
import pytest
import pandas as pd
import duckdb
import json

# Definição inicial do diretório alvo dos arquivos raw
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
BASE_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw')

@pytest.fixture(scope = "module")
def load_raw_data():
    """
    Fixture do Pytest para carregar os datasets uma única vez para todos os testes do módulo.
    """
    try:
        data = {
            "estrutura": duckdb.sql(f"SELECT * FROM read_parquet('{BASE_DIR}/Dim_Estrutura.parquet')").df(),
            "cargos": duckdb.sql(f"SELECT * FROM read_parquet('{BASE_DIR}/Dim_Cargos.parquet')").df(),
            "contratos": duckdb.sql(f"SELECT * FROM read_parquet('{BASE_DIR}/Fato_Contratos.parquet')").df(),
            "snapshot": duckdb.sql(f"SELECT * FROM read_parquet('{BASE_DIR}/Fato_Snapshot_Mensal.parquet')").df(),
            "movimentacoes": duckdb.sql(f"SELECT * FROM read_parquet('{BASE_DIR}/Fato_Movimentacoes.parquet')").df(),
            "requisicoes": duckdb.sql(f"SELECT * FROM read_parquet('{BASE_DIR}/Fato_Requisicoes_Vagas.parquet')").df(),
            "9box": duckdb.sql(f"SELECT * FROM read_parquet('{BASE_DIR}/Fato_Avaliacao_9box.parquet')").df(),
            "Pesquisa_Clima": duckdb.sql(f"SELECT * FROM read_parquet('{BASE_DIR}/Fato_Pesquisa_Clima.parquet')").df(),
            "Ponto": duckdb.sql(f"SELECT * FROM read_parquet('{BASE_DIR}/Fato_Ponto_Mensal.parquet')").df()
        }
        
        with open(os.path.join(BASE_DIR, "Dim_Pessoas.json"), "r", encoding = "utf-8") as f:
            data["pessoas"] = json.load(f)
            
            return data
        
    except FileNotFoundError as e:
        pytest.fail(F"[ERRO Crítico] - Arquivo da Camada Bronze não encontrado no disco. Rode o Gerador de Dados primeiro. Detalhes {e}")
        
def test_arquivos_existem():
    """
    Garante que os todos os artefatos de dados obrigatórios da camada bronze foram gerados com sucesso.
    """
    arquivos_obrigatorios = [
        "Dim_Estrutura.parquet",
        "Dim_Cargos.parquet",
        "Dim_Pessoas.json",
        "Fato_Contratos.parquet",
        "Fato_Ponto_Mensal.parquet",
        "Fato_Movimentacoes.parquet",
        "Fato_Pesquisa_Clima.parquet",
        "Fato_Avaliacao_9box.parquet",
        "Fato_Snapshot_Mensal.parquet",
        "Fato_Requisicoes_Vagas.parquet"
    ]
    
    for arquivo in arquivos_obrigatorios:
        caminho_completo = os.path.join(BASE_DIR, arquivo)
        assert os.path.exists(caminho_completo), f"O artefato obrigatório {arquivo} não existe na Camada Bronze."
        

def test_integridade_contratos(load_raw_data):
    """
    Valida se a tabela de contratos possui registros e as colunas essenciais.
    """
    df_contratos = load_raw_data["contratos"]
    
    # Verifica se existem registros na tabela de contratos
    assert len(df_contratos) > 0, "A Fato_Contratos não possui registros, verificar"
    
    # Validação da presentação das colunas de chave (IDs)
    colunas_esperadas = [
        "id_contrato",
        "id_pessoa",
        "id_area",
        "id_cargo",
        "tipo_contrato",
        "status",
        "salario"
    ]
    
    for col in colunas_esperadas:
        assert col in df_contratos.columns, f"A coluna obrigatória '{col}' não foi encontrada na tabela Fato_Contratos"
    
def test_sem_salario_negativos_ou_nulos(load_raw_data):
    """
    Garante a existência de salarios para que a folha salarial na tabela de snapshot se mantenha integra.
    """
    
    # Carrega inicialmente a fato_Snapshot_Mensal
    df_snapshot = load_raw_data["snapshot"]
    
    # Verifica a existência de valores nulos na coluna de salário vigente 
    assert df_snapshot["salario_vigente"].isnull().sum() == 0, "Encontrados valores nulos na coluna de salário da Fato_Snapshot_Mensal."
    
    # Verifica se todos os salários são estritamente mairoes que zeor
    assert (df_snapshot["salario_vigente"] > 0).all(), "Existem salários menores ou iguais a zero na tabela 'Fato_Snapshot_Mensal'"
    
    # Por fim carrega a fato_contratos
    df_contratos = load_raw_data["contratos"]
    
    # Verifica a existência de valores nulos na coluna de salário vigente 
    assert df_contratos["salario"].isnull().sum() == 0, "Encontrados valores nulos na coluna de salário da Fato_contratos."
    
    # Verifica se todos os salários são estritamente mairoes que zeor
    assert (df_contratos["salario"] > 0).all(), "Existem salários menores ou iguais a zero na tabela fato_contratos"
    
def test_integridade_referencial_snapshot(load_raw_data):
    """
    Verifica se todos os contratos referenciados na tabela de snapshot realmente existem na tabela de contratos
    """
    df_snapshot = load_raw_data["snapshot"]
    df_contratos = load_raw_data["contratos"]
    
    contratos_validos = set(df_contratos["id_contrato"])
    contratos_snapshot = set(df_snapshot["id_contrato"])
    
    # Garante que todos os contratos presentes na snapshot devem existir na tabela
    # mestre de contratos
    orfaos = contratos_snapshot - contratos_validos
    assert len(orfaos) == 0, f"Integridade referencial quebrada: {len(orfaos)} IDs de contratos na snapshot não constam na Fato_Contratos."
    
def test_demografia_diversidade_preenchida(load_raw_data):
    """
    Assegura que os dados de D&I (Diversidade e Inclusão) na Dim_Pessoas não possuem nulos em campos obrigatorios
    de analise
    """
    
    pessoas = load_raw_data["pessoas"]
    
    for pessoa in pessoas:
        assert pessoa.get("sexo_biologico") is not None, f"Pessoa ID {pessoa.get('id_pessoa')} está com o sexo_biologico nulo."
        assert pessoa.get("raca_cor") is not None, f"Pessoa ID {pessoa.get('id_pessoa')} está com a raca_cor nulo."
        assert pessoa.get("identidade_genero") is not None, f"Pessoa ID {pessoa.get('id_pessoa')} está com a identidade_genero nulo."

def test_snapshot_faixa_competencia(load_raw_data):
    """
    Garante que as competências do snapshot respeitam o horizonte histórico simulado
    """
    
    df_snapshot = load_raw_data["snapshot"]
    df_ponto_mensal = load_raw_data["Ponto"]
    
    competencias_unicas_snapshot = df_snapshot["competencia"].unique()
    competencias_unicas_ponto_mensal = df_ponto_mensal["competencia"].unique()
    
    assert "2010-01" in competencias_unicas_snapshot, "A competência inicial de 2010-01 está ausente na snapshot"
    assert "2010-01" in competencias_unicas_ponto_mensal, "A competência inicial de 2010-01 está ausente na Ponto_Mensal"
    
    assert "2026-08" in competencias_unicas_snapshot, "A competência final de 2026-08 está ausente na snapshot"
    assert "2026-08" in competencias_unicas_ponto_mensal, "A competência final de 2026-08 está ausente na Ponto_Mensal"
        
def test_dominio_pesquisa_clima(load_raw_data):
    """
    Valida se as notas e grupos da pesquisa de clima estão dentro dos domínios aceitaveis
    """
    df_clima = load_raw_data["Pesquisa_Clima"]
    
    assert len(df_clima) > 0, "A tabela Fato_Pesquisa_Clima está vazia."
    assert df_clima["nota_enps"].between(1, 10).all(), "Existem notas de eNPS fora do interalo pre-definido de 1 a 10"
    
    grupos_validos = {"Detrator", "Neutro", "Promotor"}
    assert set(df_clima["grupo"].unique()).issubset(grupos_validos), "Encontrados grupos de eNPS desconhecidos."
    
def test_consistencia_9box(load_raw_data):
    """
    Valida os limites impostos e a coerência matemática da matriz 9-Box
    """
    df_9box = load_raw_data["9box"]
    
    assert len(df_9box), "A tabela Fato_Avaliacao_9Box está vazia."
    assert df_9box["desempenho"].between(1, 5).all(), "Valores de desempenho fora da escala pré-definida"
    assert df_9box["potencial"].between(1, 5).all if "potencial" in df_9box.columns else True, "Valores de potencial fora da escala."
    
    # Verifica se o score total confere com as regras pré definidas (desempenho + potencial)
    score_calculado = df_9box["desempenho"] + df_9box["potencial"]
    assert (df_9box["score_total"] == score_calculado).all(), "Incosistência  detectada no cálculo do score_total da 9-Box"
    
def test_sanidade_ponto_mensal(load_raw_data):
    """
    Valida a consistência das marcações de ponto e banco de horas.
    """
    df_ponto = load_raw_data["Ponto"]
    
    assert len(df_ponto) > 0, "A tabela Fato_Ponto_Mensal está vazia."
    assert (df_ponto["horas_trabalhadas"] >= 0).all(), "Encontradas horas trabalhadas negativas ou igual a zero."
    assert (df_ponto["horas_extras"] >= 0).all(), "Encontradas horas extras negativas."
    assert (df_ponto["horas_faltas"] >= 0).all(), "Encontradas horas faltas negativas"
        
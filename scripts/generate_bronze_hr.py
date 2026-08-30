"""
Projeto Iceberg - RH: People Analytics & Data Simulator
Módulo: Geração da camada de dados Bronze (Simulação de Ecossistema)
Descrição: Script para gerar dados simulados de Rh, utilizando a biblioteca faker, por se tratar da camada não teremos tratamentos complexos e tipagem de dados, realizaremos a carga inicial com os dados originais.
"""

# ================================
# Importações Iniciais
# ================================

import os
import sys
import json
import random
import math
import pandas as pd

# ================================
# Bibliotecas de terceiros
# ================================
from datetime import datetime
from dateutil.relativedelta import relativedelta
from faker import Faker
from typing import List, Dict, Any
from loguru import logger

# =============================================================
# 1º Setup inicial de ambiente e observação (logs)
# =============================================================
# Configuração do loguru
logger.remove()  # Remove o logger padrão
logger.add(sys.stdout, colorize = True, format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>", level = "INFO")
logger.add(".../logs/hr_pipeline_{time:YYYY-MM-DD}.log", rotation = "10 MB", retention = "7 days", level = "INFO")


# Garantia de idempotência: Garantia de que execuções repetidas do script não resultem em duplicações de dados ou inconsistências.
fake = Faker('pt_BR')  # Inicializa o gerador de dados falsos com localidade brasileira
Faker.seed(42)  # Semente para garantir reprodutibilidade dos dados gerados
random.seed(42)  # Semente para garantir reprodutibilidade dos dados aleatórios

# O código deve rodar na pasta 'scripts/'. e o output deve ser feito na pasta 'data/bronze/'.
BASE_DIR = '../data/bronze/'  # Diretório base para salvar os arquivos de saída
os.makedirs(BASE_DIR, exist_ok = True)  # Cria o diretório se não existir


# ==============================================================
# 2º Definição dos metadados e regras de negócio para a geração de dados simulados
# ==============================================================

# Criando a matriz geográfica
# A declaração 'peso_volume' é oque dita a densidade populacional de cada estado, ou seja, quanto maior o peso, maior a quantidade de colaboraores simulados
escritorios_base = [
    {"uf": "SP", "cidade": "São Paulo", "lat": -23.5505, "lon": -46.6333, "peso_volume": 0.40},
    {"uf": "RJ", "cidade": "Rio de Janeiro", "lat": -22.9068, "lon": -43.1729, "peso_volume": 0.20},
    {"uf": "MG", "cidade": "Belo Horizonte", "lat": -19.9167, "lon": -43.9345, "peso_volume": 0.15},
    {"uf": "PR", "cidade": "Curitiba", "lat": -25.4284, "lon": -49.2733, "peso_volume": 0.10},
    {"uf": "BA", "cidade": "Salvador", "lat": -12.9714, "lon": -38.5114, "peso_volume": 0.10},
    {"uf": "DF", "cidade": "Brasília", "lat": -15.7942, "lon": -47.8822, "peso_volume": 0.05}
]

# Matriz Estrutural de Diretorias: um total de 7 diretorias e seus departamentos, o 'peso_volume' é o que dita a quantidade de colaboradores
diretorias_dict = {
    "Tecnologia (CTO)": {"peso_volume": 0.20, "departamentos": ["Engenharia de Software", "Dados e IA", "Infraestrutura e Cloud", "Segurança da Informação", "Arquitetura Corporativa", "Produtos Digitais"]},
    "Negócios (CRO)": {"peso_volume": 0.25, "departamentos": ["Vendas B2B", "Vendas B2C", "Marketing de Perfomance", "Branding", "Sucesso do Cliente (CS)", "Parcerias e Canais"]},
    "Operações (COO)": {"peso_volume": 0.35, "departamentos": ["Logística e Supply Chain", "Atendimento (CX)", "Facilities", "Suprimentos e Compras", "Qualidade e Processos"]},
    "Gente e Gestão (CHRO)": {"peso_volume": 0.05, "departamentos": ["Business Partners", "Talent Acquisition", "People Analytics", "Remuneração e Benefícios", "Diversidade e Inclusão (D&I)", "Departamento Pessoal"]},
    "Finanças (CFO)": {"peso_volume": 0.08, "departamentos": ["Controladoria", "Tesouraria", "Contabilidade", "Planejamento Financeiro e Análise (FP&A)", "Relações com Investidores (RI)"]},
    "Jurídico e Compliance (CLO)": {"peso_volume": 0.02, "departamentos": ["Contratos Cíveis", "Trabalhista", "Societário", "Compliance e Riscos", "Privacidade e LGPD"]},
    "Produto e Design (CPO)": {"peso_volume": 0.05, "departamentos": ["Gestão de Produtos (PMs)", "UX/UI Design", "Pesquisa e Desenvolvimento (P&D)"]}
}

# Matriz Salarial de Cargos levando como base os midpoints (target 100%)
tabela_cargos_referencia = {
    "Analista Júnior (I)": {"midpoint": 4000, "peso_hc": 0.35},
    "Analista Pleno (II)": {"midpoint": 6500, "peso_hc": 0.30},
    "Analista Sênior (III)": {"midpoint": 9500, "peso_hc": 0.15},
    "Especialista": {"midpoint": 14000, "peso_hc": 0.08},
    "Coordenador": {"midpoint": 14000, "peso_hc": 0.08},
    "Gerente": {"midpoint": 22000, "peso_hc": 0.04}
}

# ==============================================================
# 3º Motores de Calculos e Funções Auxiliares
# ==============================================================
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula a distância entre dois pontos geográficos usando a fórmula de Haversine.
    Args:
        lat1 (float): Latitude do ponto 1.
        lon1 (float): Longitude do ponto 1.
        lat2 (float): Latitude do ponto 2.
        lon2 (float): Longitude do ponto 2.
        
    Returns:
        float: Distância em quilômetros entre os dois pontos.
    """
    R = 6371. # Raio da terra em quilometros
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def calculate_salary_compa_ratio(midpoint: float, anos_de_casa: float) -> float:
    """
    Calcula o salário com base no midpoint e nos anos de casa.
    Simula a maturidade salarial da faixa, novatos(80%), veteranos (até 130%).
    
    Args:
        midpoint(float): Salário de referência para o cargo.
        anos_de_casa(float): tempo de casa do colaborador.
        
    Return:
        float: Salário calculado com base no midpoint e anos de casa.
    """
    
    if anos_de_casa < 1.0:
        multiplicador = random.uniform(0.80, 0.85) # Novatos recebem entre 80% e 95% do midpoint
    elif anos_de_casa < 3.0:
        multiplicador = random.uniform(0.90, 1.05) # Colaboradore entre 1 e 3 anos recebem entre 90% e 105% do midpoint
    elif anos_de_casa < 5.0:
        multiplicador = random.uniform(1.10, 1.20) # Colaboradores entre 3 e 5 anos recebem entre 110% e 120% do midpoint
    else:
        return round(midpoint * multiplicador, 2)
    
def record_movement(emp_id: int, data_evento: str, tipo_evento: str, 
                           cargo_ant: int, cargo_novo: int, sal_ant: float, sal_novo: float) ->None:
    """
    Log transacional (SCD Tipo 2): captura o delta (diferença de salario) para otimizar análises futuras, como por exemplo, calcular o turnover de cargos e salários.
    
    Args:
        emp_id (int): ID do colaborador.
        data_evento (str): Data do evento de movimentação.
        tipo_evento (str): Tipo de evento (promoção, demissão, etc.).
        cargo_ant (int): Cargo anterior do colaborador.
        cargo_novo (int): Novo cargo do colaborador.
        sal_ant (float): Salário anterior do colaborador.
        sal_novo (float): Novo salário do colaborador.
    """
    
    perc_aumento = (sal_novo / sal_ant - 1) if sal_ant > 0 else 0.0
    ganho_efetivo = sal_novo - sal_ant
    db['Fato_Movimentacao'].append({
        "id_contrato": emp_id,
        "data_evento": data_evento,
        "tipo_evento": tipo_evento,
        "id_cargo_anterior": cargo_ant,
        "id_cargo_novo": cargo_novo,
        "salario_anterior": round(sal_ant, 2),
        "salario_novo": round(sal_novo, 2),
        "perc_aumento": round(perc_aumento, 4),
        "ganho_efetivo": round(ganho_efetivo, 2)
    })
    
    

# ==========================================================================
# 4º Geração do Modelo Dimensional Simulado (Star schema)
# ==========================================================================

dim_estrutura_data, dim_cargos_data = [], [] # Listas vazias para armezenar os dados das dimensões
id_area_seq, id_cargo_seq = 1, 1

logger.info("[INFO] Iniciando a construção da matriz organizacional e a malha salarial (Dimensões)...")
for esc in escritorios_base:
    for diretoria, dados_dir in diretorias_dict.items():
        for depto in dados_dir["departamentos"]:
            prob_final = esc["peso_volume"] * dados_dir["peso_volume"] # Probabilidade final de um colaborador estar em determinado escritório
            dim_estrutura_data.append({
                "id_area": id_area_seq,
                "diretoria": diretoria,
                "departamento": depto,
                "centro_de_custo": f"CC-{esc['uf']}-{str(id_area_seq).zfill(3)}",
                "estado_sigla": esc["uf"],
                "cidade_escritorio": esc["cidade"],
                "lat": esc["lat"],
                "lon": esc["lon"],
                "probabilidade_alocacao": prob_final
            })
            id_area_seq += 1
            
departamentos_unicos = [d for dir_info in diretorias_dict.values() for d in dir_info["departamentos"]]
for depto in departamentos_unicos:
    for nivel, info in tabela_cargos_referencia.items():
        dim_cargos_data.append({
            "id_cargo": id_cargo_seq,
            "departamento": depto,
            "nivel_hierarquico": nivel,
            "nome_cargo": f"{nivel} de {depto}",
            "faixa_80_min": round(info["midpoint"] * 0.80, 2),
            "faixa_100_mid": round(info["midpoint"]),
            "faixa_130_mid": round(info["midpoint"] * 1.30, 2),
            "peso_contratacao": info["peso_hc"]
        })
        id_cargo_seq
        
# ======================================================================================    
# 5º Criação da maquina de estados dos colaboradores (ativos demitidos) e tabelas fato
# ======================================================================================
db: Dict[str, List[Dict[str, Any]]] = {
    "Dim_Pessoas": [],
    "Fato_Contratos": [],
    "Fato_Ponto": [],
    "Fato_Avaliacao_9Box": [],
    "Fato_Pesquisa_Clima": [],
    "Fato_Movimentacoes": [],
    "Fato_Snapshot_Mensal": []
}

active_employees: Dict[int, Dict[str, Any]] = {}
person_id_seq: contract_id_seq = 1, 1

pesos_areas = [a["probabilidade_alocacao"] for a in dim_estrutura_data]

def admit_employee(current_date: date, is_carga_inicial: bool = False) -> None:
    """
    Executa a rotina de admissão gerando perfis sintéticos, localização e cargos
    
    Args:
        current_data: Data atual do sistema,
        is_carga_inicial: flag boolena que determina se é a primeira carga
    """
    # 1. Alocação dos colaboradores
    office = random.choices(dim_estrutura_data, weights = pesos_areas, k = 1)[0]
    cargos_do_depto = [c for c in dim_cargos_data if c["departamento"] == office["departamento"]]
    cargo = random.choices(cargos_do_depto, weights = [c["peso_contratacao"] for c in cargos_do_depto], k = 1)[0]
    
    # 2. Modelo de trabalho com viés tecnologico
    if office["diretoria"].startswith("Tecnologia"):
        modelo = random.choices(["Presencial", "Híbrido", "Remoto"], weights = [0.1, 0.4, 0.5])[0]
    else:
        modelo = random.choices(["Presencial", "Híbrido", "Remoto"], weights = [0.5, 0.4, 0.1])[0]
        
    
    # 3. Modelagem geoespacial considernado a curva de gauss
    p_lat = random.gauss(office["lat"], 0.15)
    p_lon = random.gauss(office["lon"], 0.15)
    distance_km = haversine(p_lat, p_lon,  office["lat"], office["lon"])
    
    # 4. maturidade salarial
    anos_de_casa_simulado = random.uniform(0, 7) if is_carga_inicial else 0.0
    data_admissao = current_date - relativedelta(days = int(anos_de_casa_simulado * 365))
    salario_final = calculate_salary_compa_ratio(cargo["faixa_100_mid"], anos_de_casa_simulado)
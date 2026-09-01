"""
Projeto Iceberg - RH: People Analytics & Data Simulator
Módulo: Geração da camada de dados raw (Simulação de Ecossistema)
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
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from faker import Faker
from typing import List, Dict, Any
from loguru import logger

# =============================================================
# 1º Setup inicial de ambiente e observação (logs)
# =============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))

BASE_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw')
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')

# Configuração do loguru
logger.remove()  # Remove o logger padrão
logger.add(sys.stdout, colorize = True, format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>", level = "INFO")
logger.add(os.path.join(LOG_DIR, "hr_pipeline_{time:YYYY-MM-DD}.log"), rotation = "10 MB", retention = "7 days", level = "INFO")


# Garantia de idempotência: Garantia de que execuções repetidas do script não resultem em duplicações de dados ou inconsistências.
fake = Faker('pt_BR')  # Inicializa o gerador de dados falsos com localidade brasileira
Faker.seed(42)  # Semente para garantir reprodutibilidade dos dados gerados
random.seed(42)  # Semente para garantir reprodutibilidade dos dados aleatórios


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
        multiplicador = random.uniform(1.25, 1.30)
    
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
    db["Fato_Movimentacoes"].append({
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
            "faixa_130_max": round(info["midpoint"] * 1.30, 2),
            "peso_contratacao": info["peso_hc"]
        })
        id_cargo_seq += 1
        
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
    "Fato_Snapshot_Mensal": [],
    "Fato_Requisicoes_Vagas": []
}

active_employees: Dict[int, Dict[str, Any]] = {}
person_id_seq, contract_id_seq, requisicao_id_seq = 1, 1, 1

pesos_areas = [a["probabilidade_alocacao"] for a in dim_estrutura_data]

def admit_employee(current_date: date, is_carga_inicial: bool = False, req_area_id: int = None, req_cargo_id: int = None) -> None:
    """
    Executa a rotina de admissão gerando perfis sintéticos, localização e cargos
    
    Args:
        current_data: Data atual do sistema,
        is_carga_inicial: flag boolena que determina se é a primeira carga
    """
    global person_id_seq, contract_id_seq, requisicao_id_seq
    
    
    # 1. Alocação dos colaboradores
    if req_area_id and req_cargo_id:
        office = next(a for a in dim_estrutura_data if a["id_area"] == req_area_id)
        cargo = next(c for c in dim_cargos_data if c["id_cargo"] == req_cargo_id)
    else:
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
    
    # Configuração de pesos demograficos e distribuições de D&I
    sexo = random.choices(["Feminino", "Masculino"], weights = [0.51, 0.49])[0]
    
    id_genero = random.choices(["Cisgênero", "Transgênero", "Não-Binário"], weights = [0.94, 0.04, 0.02])[0]
    
    orientacao = random.choices(["Heterossexual", "Homossexual", "Bissexual", "Pansexual", "Outros", "Não Informado"],
                                weights = [0.85, 0.06, 0.04, 0.02, 0.01, 0.02])[0]
    
    raca = random.choices(["Branca", "Parda", "Preta", "Amarela", "Indígena"],
                          weights = [0.43, 0.45, 0.10, 0.01, 0.01])[0]
    
    is_pcd = random.choices([False, True], weights = [0.85, 0.15])[0]
    
    if is_pcd:
        # Registra algum tipo de defiência caso a flag "is_pcd" seja igual a true
        tipo_deficiencia = random.choices(["Física", "Auditiva", "Visual", "Intelectual", "Mental / Psicossocial", "Múltipla"],
                                  weights = [0.44, 0.19, 0.15, 0.08, 0.03, 0.11])[0]
    else:
        # Se for false mantém como none
        tipo_deficiencia = None
    
    db["Dim_Pessoas"].append({
        "id_pessoa": person_id_seq,
        "nome": fake.name(),
        "cpf": fake.cpf(),
        "data_nascimento": fake.date_of_birth(
            minimum_age = 18,
            maximum_age = 75
        ).isoformat(),
        "sexo_biologico": sexo,
        "identidade_genero": id_genero,
        "orientacao_sexual": orientacao,
        "raca_cor": raca,
        "is_pcd": is_pcd,
        "tipo_deficiencia": tipo_deficiencia,
        "estado_sigla": office["estado_sigla"],
        "cidade": office["cidade_escritorio"],
        "latitude": p_lat,
        "longitude": p_lon,
        "dependentes": [{"nome": fake.first_name()} for _ in range(random.randint(0, 2))]
    })
    
    
    # Criação da gravação para a fato_contratos
    contract_data = {
        "id_contrato": contract_id_seq,
        "id_pessoa": person_id_seq,
        "id_area": office["id_area"],
        "id_cargo": cargo["id_cargo"],
        "tipo_contrato": "CLT",
        "modelo_trabalho": modelo,
        "data_admissao": data_admissao.isoformat(),
        "data_demissao": None,
        "status": "Ativo",
        "salario": salario_final
    }
    db["Fato_Contratos"].append(contract_data)
    
    # Registro transacional
    record_movement(
        contract_id_seq,
        data_admissao.isoformat(),
        "Admissão",
        None,
        cargo["id_cargo"],
        0.0,
        salario_final
    )
    
    # Inicialização dos estados
    active_employees[contract_id_seq] = {
        "contract": contract_data,
        "distance_km": distance_km,
        "overtime_history": [0, 0, 0],
        "enps_group": "Neutro",
        "nine_box_score": random.randint(3 ,7) if is_carga_inicial else 5,
        "months_since_promo": int(anos_de_casa_simulado * 12)
    }
    id_gerado = contract_id_seq
    person_id_seq += 1
    contract_id_seq += 1
    
    return id_gerado

# ======================================================================
# 6º Orquestração do tempo
# =====================================================================
def main():
    global requisicao_id_seq
    logger.info("Iniciando a Carga Inicial: 1.000 funcionários de base...")
    
    # Este loop roda apenas para os 1000 iniciais
    for _ in range(1000):
        admit_employee(date(2010, 1, 1), is_carga_inicial=True)
        
    # --- AS VARIÁVEIS ABAIXO AGORA ESTÃO FORA DO 'FOR' ---
    start_date = date(2010, 1, 1)
    end_date = date(2026, 8, 1)
    current_date = start_date
    
    logger.info(f"Acionando o Motor Temporal ({start_date} a {end_date})...")
    
    vagas_reposicao = 0 

    while current_date <= end_date:
            # Conta quantas requisições estão ativas na base de dados
            vagas_abertas = [r for r in db["Fato_Requisicoes_Vagas"] if r["status"] == "Aberta"]
            
            competencia_atual = current_date.strftime("%m/%Y")
            logger.info(f"Competência: {competencia_atual} | Headcount: {len(active_employees)} | Vagas no ATS: {len(vagas_abertas)}")
            
            is_may = (current_date.month == 5)
            is_nov = (current_date.month == 11)
            is_clima_month = (current_date.month in [6,12])
            to_terminate = []
            
            # --- 1. MOTOR DE RECRUTAMENTO (CRIAR E FECHAR VAGAS) ---
            taxa_crescimento = random.uniform(0.001, 0.003) 
            novas_vagas = int(len(active_employees) * taxa_crescimento)
            
            if current_date.year in [2015, 2016, 2020]:  
                novas_vagas = 0 # Congelamento de expansão
                # Crise cancela até 80% das vagas de reposição que estavam abertas
                for req in vagas_abertas:
                    if random.random() < 0.80:
                        req["status"] = "Cancelada"
                        req["data_fechamento"] = current_date.isoformat()
                # Atualiza a lista após os cancelamentos
                vagas_abertas = [r for r in db["Fato_Requisicoes_Vagas"] if r["status"] == "Aberta"]
                
            # Abertura de vagas de Expansão (Orgânico)
            for _ in range(novas_vagas):
                office_target = random.choices(dim_estrutura_data, weights = pesos_areas, k = 1)[0]
                cargos_target = [c for c in dim_cargos_data if c["departamento"] == office_target["departamento"]]
                cargo_target = random.choices(cargos_target, weights = [c["peso_contratacao"] for c in cargos_target], k = 1)[0]
                
                db["Fato_Requisicoes_Vagas"].append({
                    "id_requisicao": requisicao_id_seq, 
                    "data_abertura": current_date.isoformat(),
                    "data_fechamento": None, 
                    "tipo_vaga": "Aumento de Quadro",
                    "id_area": office_target["id_area"], 
                    "id_cargo": cargo_target["id_cargo"],
                    "status": "Aberta",
                    "id_contrato_preenchimento": None
                })
                requisicao_id_seq += 1
                vagas_abertas = [r for r in db["Fato_Requisicoes_Vagas"] if r["status"] == "Aberta"]

            # Recrutamento operando: Fecha entre 60% e 85% do pipeline do mês
            if vagas_abertas:
                qtd_para_fechar = int(len(vagas_abertas) * random.uniform(0.60, 0.85))
                vagas_selecionadas = random.sample(vagas_abertas, qtd_para_fechar)
                
                for req in vagas_selecionadas:
                    # Contrata o perfil exato que a vaga pede e amarra os IDs
                    id_novo_colaborador = admit_employee(current_date, req_area_id=req["id_area"], req_cargo_id=req["id_cargo"])
                    req["status"] = "Preenchida"
                    req["data_fechamento"] = current_date.isoformat()
                    req["id_contrato_preenchimento"] = id_novo_colaborador
                
            # --- 2. LOOP INTRA-MÊS BLINDADO COM list() ---
            for emp_id, state in list(active_employees.items()):
                c = state["contract"]
                salario_atual = c["salario"]
                cargo_atual_id = c["id_cargo"]
                
                # (A) Ponto e Burnout Físico
                base_faltas = 0
                if c["modelo_trabalho"] in ["Presencial", "Híbrido"] and state["distance_km"] > 30:
                    base_faltas = random.choices([0, 8 ,16], weights = [0.6, 0.3, 0.1])[0]
                    
                horas_extras = random.randint(0, 30)
                db["Fato_Ponto"].append({
                    "id_contrato": emp_id, "competencia": current_date.isoformat()[:7],
                    "horas_trabalhadas": 180 - base_faltas, "horas_extras": horas_extras, "horas_faltas": base_faltas 
                })
                
                # (B) Burnout Mental
                state["overtime_history"].pop(0)
                state["overtime_history"].append(horas_extras)
                if sum(state["overtime_history"]) > 60:
                    state["enps_group"] = "Detrator"
                    if random.random() < 0.05:
                        db["Fato_Movimentacoes"].append({
                            "id_contrato": emp_id, "data_evento": current_date.isoformat(), "tipo_evento": "Afastamento_Saude",
                            "id_cargo_anterior": cargo_atual_id, "id_cargo_novo": cargo_atual_id,
                            "salario_anterior": salario_atual, "salario_novo": salario_atual,
                            "perc_aumento": 0.0, "ganho_efetivo": 0.0
                        })
                        
                # (C) Sazonalidades (Clima e 9-Box)
                if is_clima_month:
                    nota = random.randint(1, 6) if (state["distance_km"] > 30 and state["enps_group"] == "Detrator") else random.randint(5, 10)
                    grupo = "Detrator" if nota <= 6 else "Neutro" if nota <= 8 else "Promotor"
                    state["enps_group"] = grupo
                    db["Fato_Pesquisa_Clima"].append({"id_contrato": emp_id, "data": current_date.isoformat(), "nota_enps": nota, "grupo": grupo})
                
                if is_nov:
                    desempenho, potencial = random.randint(1, 5), random.randint(1, 5)
                    score = desempenho + potencial
                    state["nine_box_score"] = score
                    db["Fato_Avaliacao_9Box"].append({"id_contrato": emp_id, "ano": current_date.year, "desempenho": desempenho, "potencial": potencial, "score_total": score})
                    
                # (D) Dissídio, Mérito e Promoção
                if is_may:
                    novo_salario = round(salario_atual * 1.05, 2)
                    record_movement(emp_id, current_date.isoformat(), "Dissídio", cargo_atual_id, cargo_atual_id, salario_atual, novo_salario)
                    c["salario"] = novo_salario
                    salario_atual = novo_salario
                    
                state["months_since_promo"] += 1
                is_elegivel = state["nine_box_score"] >= 8 and state["months_since_promo"] >= 12
                
                if is_elegivel:
                    cargo_obj = next(cg for cg in dim_cargos_data if cg["id_cargo"] == cargo_atual_id)
                    teto_faixa = cargo_obj["faixa_130_max"]
                    
                    if salario_atual < (cargo_obj["faixa_100_mid"] * 1.15):
                        if random.random() < 0.15:
                            novo_salario = min(round(salario_atual * random.uniform(1.05, 1.10), 2), teto_faixa)
                            record_movement(emp_id, current_date.isoformat(), "Mérito", cargo_atual_id, cargo_atual_id, salario_atual, novo_salario)
                            c["salario"] = novo_salario
                            state["months_since_promo"] = 0
                    else:
                        if random.random() < 0.10:
                            novo_cargo_id = min(cargo_atual_id + 1, len(dim_cargos_data))
                            novo_cargo_obj = next(cg for cg in dim_cargos_data if cg["id_cargo"] == novo_cargo_id)
                            novo_salario = round(max(salario_atual * 1.10, novo_cargo_obj["faixa_80_min"]), 2)
                            record_movement(emp_id, current_date.isoformat(), "Promoção", cargo_atual_id, novo_cargo_id, salario_atual, novo_salario)
                            c["salario"], c["id_cargo"] = novo_salario, novo_cargo_id
                            state["months_since_promo"] = 0
                            
                # --- 3. REGRAS DE TURNOVER (A MAGIA DO NEGÓCIO) ---
                # Turnover Involuntário (Baixo Desempenho no 9-Box)
                if state["nine_box_score"] <= 4 and current_date.month in [1, 2]: # Demissões costumam ocorrer após o fechamento do ano
                    if random.random() < 0.20: # 20% de chance de corte
                        to_terminate.append((emp_id, "Demissão Sem Justa Causa"))
                        continue
                        
                # Fuga de Talentos Voluntária
                if is_elegivel and state["enps_group"] == "Detrator" and salario_atual >= (dim_cargos_data[cargo_atual_id-1]["faixa_130_max"] * 0.95):
                    if random.random() < 0.08:
                        to_terminate.append((emp_id, "Desligamento Voluntário"))
                        
                # --- 4. EFETIVAÇÃO DOS DESLIGAMENTOS E GERAÇÃO DE VAGAS ---
            for emp_id, motivo in to_terminate:
                if emp_id in active_employees:
                    area_id_saida = active_employees[emp_id]["contract"]["id_area"]
                    cargo_id_saida = active_employees[emp_id]["contract"]["id_cargo"]
                    salario_saida = active_employees[emp_id]["contract"]["salario"]
                    
                    active_employees[emp_id]["contract"]["status"] = "Desligado"
                    active_employees[emp_id]["contract"]["data_demissao"] = current_date.isoformat()
                    
                    record_movement(emp_id, current_date.isoformat(), motivo, cargo_id_saida, cargo_id_saida, salario_saida, 0.0)
                    del active_employees[emp_id]
                    
                    # ABRE A VAGA DE REPOSIÇÃO (BACKFILL)
                    db["Fato_Requisicoes_Vagas"].append({
                        "id_requisicao": requisicao_id_seq, "data_abertura": current_date.isoformat(),
                        "data_fechamento": None, "tipo_vaga": "Substituição",
                        "id_area": area_id_saida, "id_cargo": cargo_id_saida,
                        "status": "Aberta", "id_contrato_preenchimento": None
                    })
                    requisicao_id_seq += 1
                    
            str_competencia = current_date.strftime("%Y-%m")    
            
            # [Restante do Snapshot Mensal e Salvamento Parquet continuam idênticos]    
            
            for emp_id, state in active_employees.items():
                db["Fato_Snapshot_Mensal"].append({
                    "competencia": str_competencia,
                    "id_contrato": emp_id,
                    "id_cargo": state["contract"]["id_cargo"],
                    "id_area": state["contract"]["id_area"],
                    "salario_vigente": state["contract"]["salario"],
                    "enps_group": state["enps_group"],
                    "nine_box_score": state["nine_box_score"]
                })
                
            current_date += relativedelta(months = 1)
# ======================================================================
# 7º Serialização e Dump do Disco local
# ======================================================================
    logger.info("[INFO] Convertendo os dados salvos em memória para DataFrames (Pandas)...")
    pd.DataFrame(dim_estrutura_data).to_parquet(f"{BASE_DIR}/Dim_Estrutura.parquet")
    pd.DataFrame(dim_cargos_data).to_parquet(f"{BASE_DIR}/Dim_Cargos.parquet")
    pd.DataFrame(db["Fato_Contratos"]).to_parquet(f"{BASE_DIR}/Fato_Contratos.parquet")
    pd.DataFrame(db["Fato_Ponto"]).to_parquet(f"{BASE_DIR}/Fato_Ponto_Mensal.parquet")
    pd.DataFrame(db["Fato_Movimentacoes"]).to_parquet(f"{BASE_DIR}/Fato_Movimentacoes.parquet")
    pd.DataFrame(db["Fato_Pesquisa_Clima"]).to_parquet(f"{BASE_DIR}/Fato_Pesquisa_Clima.parquet")
    pd.DataFrame(db["Fato_Avaliacao_9Box"]).to_parquet(f"{BASE_DIR}/Fato_Avaliacao_9box.parquet")
    pd.DataFrame(db["Fato_Requisicoes_Vagas"]).to_parquet(f"{BASE_DIR}/Fato_Requisicoes_Vagas.parquet")
    pd.DataFrame(db["Fato_Snapshot_Mensal"]).to_parquet(f"{BASE_DIR}/Fato_Snapshot_Mensal.parquet")
            
    with open(f"{BASE_DIR}/Dim_Pessoas.json", "w", encoding = "utf-8") as f:
        json.dump(db["Dim_Pessoas"], f, ensure_ascii = False, indent = 2)
                
    logger.success("[SUCESSO] Geração de arquivos concluída com sucesso! Camada Raw (Parquet/Json) populada.")
            
if __name__ == "__main__":
    main()
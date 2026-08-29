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

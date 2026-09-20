import random

# Listas de blocos construtores para análise combinatória
PREFIXOS_HARD = ["Fundamentos de", "Bootcamp:", "Introdução a", "Arquitetura e", "Masterclass:", "Trilha Avançada:"]
TEMAS_HARD = [
    "Python para Análise de Dados", "PySpark e Big Data no Lakehouse", "Modelagem Dimensional com dbt",
    "DAX Avançado e Modelagem em Power BI", "Machine Learning e MLOps", "SQL Refactoring e BigQuery",
    "Macros em VBA e Excel Avançado", "Desenvolvimento Frontend com React e Tailwind", 
    "Aplicações Web com Django", "Governança no Unity Catalog"
]

PREFIXOS_SOFT = ["Desenvolvendo", "Imersão em", "Workshop:", "Práticas de", "Dominando a"]
TEMAS_SOFT = [
    "Inteligência Emocional", "Comunicação Não-Violenta (CNV)", "Gestão de Tempo e Foco",
    "Resolução de Problemas Complexos", "Adaptabilidade no Ambiente de Trabalho", "Escuta Ativa"
]

PREFIXOS_LID = ["Liderança na Prática:", "Gestão Estratégica:", "Formação de Líderes:"]
TEMAS_LID = [
    "Feedback Efetivo e Feedforward", "Liderança Situacional", "People Analytics Estratégico",
    "Gestão por OKRs", "Formação de Equipes de Alta Performance", "Tomada de Decisão Baseada em Dados"
]

# Cursos fixos de Onboarding que não precisam de combinatória
CURSOS_ONBOARDING = [
    {"nome_curso": "Café com SDH - Cultura e Integração", "horas": 4},
    {"nome_curso": "Compliance e Código de Conduta", "horas": 2},
    {"nome_curso": "Segurança da Informação e Privacidade", "horas": 2},
    {"nome_curso": "LGPD na Prática Corporativa", "horas": 2}
]

def gerar_catalogo_lms(qtd_hard=50, qtd_soft=30, qtd_lid=20) -> dict:
    """
    Gera um catálogo sintético de cursos misturando prefixos e temas,
    garantindo IDs únicos para a dimensão de cursos.
    """
    random.seed(42) # Idempotência
    catalogo = {"Onboarding": [], "Hard Skills": [], "Soft Skills": [], "Liderança": []}
    id_seq = 1000

    # 1. Carrega Onboarding
    for curso in CURSOS_ONBOARDING:
        catalogo["Onboarding"].append({
            "id_curso": id_seq,
            "nome_curso": curso["nome_curso"],
            "horas": curso["horas"]
        })
        id_seq += 1

    # 2. Motor Gerador Combinatório (Função Interna)
    def fabricar_cursos(categoria, prefixos, temas, quantidade):
        nonlocal id_seq
        cursos_gerados = set()
        
        # Trava de segurança (Failsafe): Impede loops infinitos
        max_combinacoes = len(prefixos) * len(temas)
        quantidade_segura = min(quantidade, max_combinacoes)
        
        while len(cursos_gerados) < quantidade_segura:
            nome = f"{random.choice(prefixos)} {random.choice(temas)}"
            if nome not in cursos_gerados:
                cursos_gerados.add(nome)
                horas = random.choices([2, 4, 8, 12, 16, 20, 40], weights=[0.1, 0.2, 0.3, 0.2, 0.1, 0.05, 0.05])[0]
                catalogo[categoria].append({
                    "id_curso": id_seq,
                    "nome_curso": nome,
                    "horas": horas
                })
                id_seq += 1

    fabricar_cursos("Hard Skills", PREFIXOS_HARD, TEMAS_HARD, qtd_hard)
    fabricar_cursos("Soft Skills", PREFIXOS_SOFT, TEMAS_SOFT, qtd_soft)
    fabricar_cursos("Liderança", PREFIXOS_LID, TEMAS_LID, qtd_lid)

    return catalogo
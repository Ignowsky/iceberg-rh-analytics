{{ config(
    materialized = 'table', 
    tags = ['silver', 'dimensao', 'rh_core']
) }}

WITH pessoas AS (
    SELECT * FROM {{ ref('stg_pessoas') }}
),
contratos AS (
    SELECT * FROM {{ ref('stg_fato_contratos') }}
),
cargos AS (
    SELECT * FROM {{ ref('stg_cargos') }}
),
estrutura AS (
    SELECT * FROM {{ ref('stg_estrutura') }}
),

cruzamento AS (
    SELECT
        c.sk_contrato,
        c.sk_pessoa,
        p.nome_completo,
        p.data_nascimento,
        
        -- Controle de Dimensionalidade Histórica (SCD Tipo 2)
        c.data_admissao AS data_inicio_validade,
        COALESCE(c.data_demissao, CAST('9999-12-31' AS DATE)) AS data_fim_validade,
        c.status_contrato,
        CASE WHEN c.status_contrato = 'Ativo' THEN 1 ELSE 0 END AS flag_ativo,
        
        -- Extração inteligente do JSON de dependentes (Motor Photon/Spark)
        CASE 
            WHEN p.dependentes_json IS NULL OR p.dependentes_json = '[]' THEN 0
            ELSE size(from_json(p.dependentes_json, 'array<string>')) 
        END AS qtd_dependentes,

        -- Idade congelada na admissão (Melhor prática para análise de cohorts)
        FLOOR(months_between(c.data_admissao, p.data_nascimento) / 12) AS idade_na_admissao,
        
        -- Idade dinâmica mantida para análises contemporâneas
        FLOOR(months_between(CURRENT_DATE(), p.data_nascimento) / 12) AS idade_atual,
        
        CASE
            WHEN FLOOR(months_between(CURRENT_DATE(), p.data_nascimento) / 12) < 25 THEN 'Geração Z (Até 24 anos)'
            WHEN FLOOR(months_between(CURRENT_DATE(), p.data_nascimento) / 12) BETWEEN 25 AND 40 THEN 'Millenials (25 a 40 anos)'
            WHEN FLOOR(months_between(CURRENT_DATE(), p.data_nascimento) / 12) BETWEEN 41 AND 56 THEN 'Geração X (41 a 56 Anos)'
            ELSE 'Baby Boomers (57+ anos)'
        END AS geracao_faixa_etaria,
        
        p.sexo_biologico,
        p.identidade_genero,
        CASE WHEN p.is_pcd = true THEN 1 ELSE 0 END AS flag_pcd,
        COALESCE(p.tipo_deficiencia, 'Não Possui') AS tipo_deficiencia,
        p.raca_cor,
        p.escolaridade,
        
        FLOOR(months_between(COALESCE(c.data_demissao, CURRENT_DATE()), c.data_admissao) / 12) AS tempo_casa_anos,
        c.modelo_trabalho,
        c.salario_base,
        cg.nome_cargo,
        cg.nivel_senioridade,
        e.departamento AS nome_area,
        e.diretoria,
        e.cidade_escritorio,
        e.latitude,
        e.longitude
        
    FROM contratos c
    INNER JOIN pessoas p ON c.sk_pessoa = p.sk_pessoa
    LEFT JOIN cargos cg ON c.sk_cargo = cg.sk_cargo
    LEFT JOIN estrutura e ON c.sk_area = e.sk_area
)

SELECT * FROM cruzamento
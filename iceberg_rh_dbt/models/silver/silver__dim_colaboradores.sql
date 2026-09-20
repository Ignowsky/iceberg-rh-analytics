{{ config(materialized = 'table', tags = ['silver', 'transacional']) }}

WITH pessoas as (
    SELECT *
    FROM {{ ref('stg_pessoas') }}
),

contratos AS (
    SELECT *
    FROM {{ ref('stg_fato_contratos') }}
),

cargos AS (
    SELECT *
    FROM {{ ref('stg_cargos') }}
),

estrutura AS (
    SELECT *
    FROM {{ ref('stg_estrutura') }}
)

SELECT
    c.sk_contrato,
    c.sk_pessoa,
    p.nome_completo,
    p.data_nascimento,
    floor(months_between(current_date(), p.data_nascimento) / 12) as idade_atual,
    CASE
        WHEN floor(months_between(current_date(), p.data_nascimento) / 12) < 25 then 'Geração Z (Até 24 anos)'
        WHEN floor(months_between(current_date(), p.data_nascimento) / 12) between 25 and 40 then 'Millenials (25 a 40 anos)'
        WHEN floor(months_between(current_date(), p.data_nascimento) / 12) between 41 and 56 then 'Geração X (41 a 56 Anos)'
        ELSE 'Baby Boomers (57+ anos)'
    END AS geracao_faixa_etaria,
    p.sexo_biologico,
    p.identidade_genero,
    CASE WHEN p.is_pcd = true THEN 1 ELSE 0 END AS flag_pcd,
    CASE WHEN p.tipo_deficiencia IS NULL THEN 'Não Possui' ELSE p.tipo_deficiencia END AS tipo_deficiencia,
    p.raca_cor,
    p.escolaridade,
    c.data_admissao,
    c.data_demissao,
    c.status_contrato,
    CASE WHEN c.status_contrato = 'Ativo' THEN 1 ELSE 0 END as flag_ativo,
    floor(
        months_between(
            coalesce(c.data_demissao, current_date()),
            c.data_admissao
        ) / 12
    ) as tempo_casa_anos,
    c.modelo_trabalho,
    c.salario_base,
    cg.nome_cargo,
    cg.nivel_senioridade,
    e.departamento as nome_area,
    e.diretoria,
    e.cidade_escritorio,
    e.latitude,
    e.longitude
FROM contratos c
INNER JOIN pessoas p
    ON c.sk_pessoa = p.sk_pessoa
LEFT JOIN cargos cg
    ON c.sk_cargo = cg.sk_cargo
LEFT JOIN estrutura e
    ON c.sk_area = e.sk_area
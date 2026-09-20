{{ config(materialized = 'table', tags = ['silver', 'transacional']) }}

WITH absenteismo AS (
    SELECT *
    FROM {{  ref('stg_fato_absenteismo') }}
),
colaboradores AS (
    SELECT 
        sk_contrato,
        salario_base
    FROM {{ ref('silver__dim_colaboradores') }}
)
SELECT 
    a.sk_absenteismo,
    a.sk_contrato,
    a.mes_competencia,
    a.data_inicio,
    a.qtd_dias,
    (a.qtd_dias * 8) AS horas_perdidas,
    a.tipo_afastamento,
    a.cid_simulado,

    -- Custo financeiro estimado
    CAST(
        (c.salario_base / 30) * a.qtd_dias AS DOUBLE
    ) AS custo_ausencia,

    CASE
        WHEN a.qtd_dias > 15 THEN 'Afastamento Longo (>15d)'
        WHEN a.qtd_dias BETWEEN 5 AND 15 THEN 'Moderado (5-15d)'
        ELSE 'Curto (<5d)'
    END AS risco_afastamento
FROM absenteismo a
INNER JOIN colaboradores c
    ON a.sk_contrato = c.sk_contrato
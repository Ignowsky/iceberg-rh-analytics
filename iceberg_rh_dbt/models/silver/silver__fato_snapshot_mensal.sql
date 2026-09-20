{{ config(
    materialized = 'table',
    tags = ['silver', 'kpi_historico']
) }}

WITH snapshot_raw AS (
    -- Assumindo que a stg_fato_snapshot_mensal já gerou as SKs via macro
    SELECT * FROM {{ ref('stg_fato_snapshot_mensal') }}
),
colaboradores AS (
    SELECT sk_contrato, flag_ativo, tempo_casa_anos 
    FROM {{ ref('silver__dim_colaboradores') }}
)

SELECT
    s.sk_snapshot, -- Chave MD5 gerada na staging
    s.sk_contrato,
    s.sk_cargo,
    s.sk_area,
    
    -- Conversão da string 'YYYY-MM' para o formato DATE real (Primeiro dia do mês)
    CAST(concat(s.mes_competencia, '-01') AS DATE) AS data_competencia,
    
    s.salario_vigente,
    s.grupo_enps AS grupo_clima,
    s.desempenho_nine_box AS nota_desempenho,
    s.potencial_nine_box AS nota_potencial,
    
    -- Trazendo a flag atual para saber se esse colaborador da foto histórica ainda está na empresa hoje
    c.flag_ativo AS flag_ativo_hoje
    
FROM snapshot_raw s
LEFT JOIN colaboradores c ON s.sk_contrato = c.sk_contrato
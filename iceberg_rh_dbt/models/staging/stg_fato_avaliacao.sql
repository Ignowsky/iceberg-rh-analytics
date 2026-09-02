{{ config(materialized = 'view')}}

WITH source AS (
    SELECT *
    FROM {{ source('hr_bronze', 'Fato_Avaliacao_9box')}}
),
classificacao_eixo AS (
SELECT 
    -- Gerando uma SK pelo dbt
    FARM_FINGERPRINT(CONCAT(CAST(id_contrato AS STRING), '-', CAST(ano AS STRING))) AS sk_avaliacao,
    CAST(id_contrato AS INT64) AS sk_contrato,
    CAST(ano AS INT64)AS ano_avaliacao,
    CAST(desempenho AS INT64) AS nota_desempenho,
    CAST(potencial AS INT64) AS nota_potencial,

    CASE CAST(desempenho AS INT64)
        WHEN 1 THEN 'Baixo'
        WHEN 2 THEN 'Médio'
        WHEN 3 THEN 'Alto'
    END AS eixo_desempenho,

    CASE CAST(potencial AS INT64)
        WHEN 1 THEN 'Baixo'
        WHEN 2 THEN 'Médio'
        WHEN 3 THEN 'Alto'
    END AS eixo_potencial
FROM source
)

SELECT *,
    CONCAT(eixo_desempenho, ' / ', eixo_potencial) AS quadrante_9box
FROM classificacao_eixo
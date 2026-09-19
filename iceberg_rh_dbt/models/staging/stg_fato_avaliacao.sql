{{ config(materialized = 'view')}}

WITH source AS (
    SELECT *
    FROM {{ source('hr_bronze', 'Fato_Avaliacao_9box')}}
),
classificacao_eixo AS (
SELECT 
    -- Gerando uma SK pelo dbt
    MD5(CONCAT(CAST(id_contrato AS STRING), '-', CAST(ano AS STRING))) AS sk_avaliacao,
    CAST(id_contrato AS INT) AS sk_contrato,
    CAST(ano AS INT)AS ano_avaliacao,
    CAST(desempenho AS INT) AS nota_desempenho,
    CAST(potencial AS INT) AS nota_potencial,

    CASE CAST(desempenho AS INT)
        WHEN 1 THEN 'Baixo'
        WHEN 2 THEN 'Médio'
        WHEN 3 THEN 'Alto'
    END AS eixo_desempenho,

    CASE CAST(potencial AS INT)
        WHEN 1 THEN 'Baixo'
        WHEN 2 THEN 'Médio'
        WHEN 3 THEN 'Alto'
    END AS eixo_potencial
FROM source
)

SELECT *,
    CONCAT(eixo_desempenho, ' / ', eixo_potencial) AS quadrante_9box
FROM classificacao_eixo
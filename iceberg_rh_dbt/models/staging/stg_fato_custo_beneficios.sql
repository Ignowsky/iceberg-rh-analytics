{{  config(materialized = 'view') }}

WITH source AS (
    SELECT *
    FROM {{ source('hr_bronze', 'Fato_Custo_Beneficios') }}
),
renamed_and_casted AS (
    SELECT 
        MD5(CONCAT(CAST(id_contrato AS STRING), '-', competencia)) AS sk_fatura_mensal,
        competencia AS mes_competencia,
        CAST(id_contrato AS INT) AS sk_contrato,
        CAST(custo_saude_titular AS DOUBLE) AS custo_saude_titular,
        CAST(custo_saude_dependentes AS DOUBLE) AS custo_saude_dependentes,
        CAST(custo_odonto AS DOUBLE) AS custo_odonto,
        CAST(custo_vale_alimentacao AS DOUBLE) AS custo_vale_alimentacao,
        CAST(custo_total_beneficios AS DOUBLE) AS custo_total_beneficios
    FROM source
)
SELECT *
FROM renamed_and_casted
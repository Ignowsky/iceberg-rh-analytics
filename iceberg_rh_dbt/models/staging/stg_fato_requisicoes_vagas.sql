{{ config(materialized = 'view')}}
WITH source AS (
    SELECT *
    FROM {{ source('hr_bronze', 'Fato_Requisicoes_Vagas')}}
),
renamed_and_casted AS (
    SELECT 
        CAST(id_requisicao AS INT64) AS sk_requisicao,
        CAST(data_abertura AS DATE) AS data_abertura,
        CAST(data_fechamento AS DATE) AS data_fechamento,
        tipo_vaga,
        CAST(id_area AS INT64) AS sk_area,
        CAST(id_cargo AS INT64) AS sk_cargo,
        status,
        CAST(id_contrato_preenchimento AS INT64) AS sk_contrato_preechimento
    FROM source
)
SELECT *
FROM renamed_and_casted
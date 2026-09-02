{{ config(materialized = 'view') }}
WITH source AS (
    SELECT *
    FROM {{ source('hr_bronze', 'Fato_Pesquisa_Clima') }}
),
renamed_and_casted AS (
    SELECT
        FARM_FINGERPRINT(CONCAT(CAST(id_contrato AS STRING), '-', CAST(data AS STRING))) AS sk_pesquisa_clima,
        CAST(id_contrato AS INT64) AS sk_contrato,
        CAST(data AS DATE) AS data_pesquisa_clima,
        CAST(nota_enps AS INT64) nota_enps,
        grupo
    FROM source
)
SELECT *
FROM renamed_and_casted
{{ config(materialized = 'view') }}
WITH source AS (
    SELECT *
    FROM {{ source('hr_bronze', 'Fato_Pesquisa_Clima') }}
),
renamed_and_casted AS (
    SELECT
        MD5(CONCAT(CAST(id_contrato AS STRING), '-', CAST(data AS STRING))) AS sk_pesquisa_clima,
        CAST(id_contrato AS INT) AS sk_contrato,
        CAST(data AS DATE) AS data_pesquisa_clima,
        CAST(nota_enps AS INT) nota_enps,
        grupo
    FROM source
)
SELECT *
FROM renamed_and_casted
{{ config(materialized = 'view')}}

WITH source AS (
    SELECT *
    FROM {{ source('hr_bronze', 'Fato_Contratos')}}
),
renamed_and_casted AS (
    SELECT
        CAST(id_contrato AS INT) AS sk_contrato,
        CAST(id_pessoa AS INT) AS sk_pessoa,
        CAST(id_area AS INT) AS sk_area,
        CAST(id_cargo AS INT) AS sk_cargo,
        tipo_contrato,
        modelo_trabalho,
        CAST(data_admissao AS DATE) AS data_admissao,
        CAST(data_demissao AS DATE) AS data_demissao,
        status AS status_contrato,
        CAST(salario AS DOUBLE) AS salario_base
    FROM source
)
SELECT *
FROM renamed_and_casted
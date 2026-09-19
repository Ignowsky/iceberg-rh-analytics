{{ config(materialized = 'view') }}

WITH source AS(
    SELECT *
    FROM {{ source('hr_bronze', 'Fato_Ponto')}}
),

renamed_and_casted AS (
    SELECT
        MD5(CONCAT(CAST(id_contrato AS STRING), '-', CAST(competencia AS STRING))) AS sk_ponto_mensal,
        CAST(id_contrato AS INT) AS sk_contrato,
        competencia AS mes_competencia,
        CAST(horas_trabalhadas AS INT) AS horas_trabalhadas,
        CAST(horas_extras AS INT) AS horas_extras,
        CAST(horas_faltas AS INT) AS horas_faltas
    FROM source
)
SELECT *
FROM renamed_and_casted
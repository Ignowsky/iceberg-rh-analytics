{{ config(materialized = 'view') }}

WITH source AS (
    SELECT *
    FROM {{ source('hr_bronze', 'Dim_Cursos') }}
),
renamed_and_casted AS (
    SELECT 
        CAST(id_curso AS INT) AS sk_curso,
        nome_curso,
        trilha_conhecimento,
        CAST(carga_horaria_padrao AS INT) AS carga_horaria_padrao
    FROM source
)
SELECT *
FROM renamed_and_casted
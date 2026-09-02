{{config(
    materialized = 'view'
)}}

WITH source AS (
    SELECT *
    FROM {{ source('hr_bronze', 'Dim_Pessoas')}}
),

renamed_and_casted AS (
    SELECT 
        CAST(id_pessoa as INT64) AS sk_pessoa,
        nome as nome_completo,
        cpf,
        CAST(data_nascimento AS DATE) AS data_nascimento,
        sexo_biologico,
        identidade_genero,
        raca_cor,
        CAST(is_pcd AS BOOLEAN) AS is_pcd,
        tipo_deficiencia,
        estado_sigla,
        cidade,
        CAST(latitude AS FLOAT64) AS latitude,
        CAST(longitude AS FLOAT64) AS longitude,
        dependentes as dependentes_json
    FROM source
)

SELECT *
FROM renamed_and_casted
{{ config(materialized = 'view')}}

WITH source AS (
    SELECT *
    FROM {{ source('hr_bronze', 'Dim_Cargos')}}
),

renamed_and_casted AS (
    SELECT 
        CAST(id_cargo AS INT64) AS sk_cargo,
        departamento AS nome_departamento,
        cargo AS nome_cargo,
        nivel_hierarquico AS nivel_senioridade,
        CAST(faixa_80_min AS FLOAT64) AS faixa_80_min,
        CAST(faixa_100_mid AS FLOAT64) AS faixa_100_mid,
        CAST(faixa_130_max AS FLOAT64) AS faixa_130_max,
        CAST(peso_contratacao AS FLOAT64) AS peso_contratacao
    FROM source
)
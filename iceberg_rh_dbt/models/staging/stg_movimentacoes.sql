{{ config(materialized = 'view') }}
WITH source AS (
    SELECT *
    FROM {{ source('hr_bronze', 'Fato_Movimentacoes')}}
),
renamed_and_casted AS (
    SELECT 
        CAST(id_contrato AS INT64) AS sk_contrato,
        CAST(data_evento AS DATE) AS data_evento,
        tipo_evento,
        CAST(id_cargo_anterior AS INT64) AS sk_cargo_anterior,
        CAST(id_cargo_novo AS INT64) AS sk_novo_cargo,
        CAST(salario_anterior AS FLOAT64) AS salario_anterior,
        CAST(salario_novo AS FLOAT64) AS salario_novo,
        CAST(perc_aumento AS FLOAT64) AS percentual_aumento,
        CAST(ganho_efetivo AS FLOAT64) AS ganho_efetivo
    FROM source
)
SELECT *
FROM renamed_and_casted
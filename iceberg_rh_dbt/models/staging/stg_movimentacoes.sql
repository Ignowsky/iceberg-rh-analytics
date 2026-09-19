{{ config(materialized = 'view') }}
WITH source AS (
    SELECT *
    FROM {{ source('hr_bronze', 'Fato_Movimentacoes')}}
),
renamed_and_casted AS (
    SELECT 
        CAST(id_contrato AS INT) AS sk_contrato,
        CAST(data_evento AS DATE) AS data_evento,
        tipo_evento,
        CAST(id_cargo_anterior AS INT) AS sk_cargo_anterior,
        CAST(id_cargo_novo AS INT) AS sk_novo_cargo,
        CAST(salario_anterior AS FLOAT) AS salario_anterior,
        CAST(salario_novo AS FLOAT) AS salario_novo,
        CAST(perc_aumento AS FLOAT) AS percentual_aumento,
        CAST(ganho_efetivo AS FLOAT) AS ganho_efetivo
    FROM source
)
SELECT *
FROM renamed_and_casted
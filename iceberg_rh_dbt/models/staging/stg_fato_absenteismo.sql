{{  config(materialized = 'view') }}

WITH source AS (
    SELECT *
    FROM {{  source('hr_bronze', 'Fato_Absenteismo_Historico') }}
),
renamed_and_casted AS (
    SELECT 
        MD5(CONCAT(CAST(id_contrato AS STRING), '-', data_inicio, '-', tipo_afastamento)) AS sk_absenteismo,
        competencia AS mes_competencia,
        CAST(id_contrato as INT) AS sk_contrato,
        CAST(data_inicio as DATE) AS data_inicio,
        CAST(data_fim AS DATE) AS data_fim,
        CAST(qtd_dias AS INT) AS qtd_dias,
        tipo_afastamento,
        cid_simulado
    FROM source
)
SELECT *
FROM renamed_and_casted
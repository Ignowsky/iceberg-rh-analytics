{{ config(materialized = 'view') }}
WITH source AS(
    SELECT *
    FROM {{ source('hr_bronze', 'Fato_Snapshot_Mensal')}}
),
renamed_and_casted AS (
    SELECT
        FARM_FINGERPRINT(CONCAT(CAST(id_contrato AS STRING),'-', competencia)) AS sk_snapshot,
        competencia AS mes_competencia,
        CAST(id_contrato AS INT64) AS sk_contrato,
        CAST(id_cargo AS INT64) AS sk_cargo,
        CAST(id_area AS INT64) AS sk_area,
        CAST(salario_vigente AS FLOAT64) AS salario_vigente,
        enps_group AS grupo_enps,
        CAST(desempenho AS INT64) AS desempenho_nine_box,
        CAST(potencial AS INT64) AS potencial_nine_box
    FROM source
)
SELECT *
FROM renamed_and_casted
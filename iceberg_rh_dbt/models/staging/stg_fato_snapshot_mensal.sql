{{ config(materialized = 'view') }}
WITH source AS(
    SELECT *
    FROM {{ source('hr_bronze', 'Fato_Snapshot_Mensal')}}
),
renamed_and_casted AS (
    SELECT
        MD5(CONCAT(CAST(id_contrato AS STRING),'-', competencia)) AS sk_snapshot,
        competencia AS mes_competencia,
        CAST(id_contrato AS INT) AS sk_contrato,
        CAST(id_cargo AS INT) AS sk_cargo,
        CAST(id_area AS INT) AS sk_area,
        CAST(salario_vigente AS DOUBLE) AS salario_vigente,
        enps_group AS grupo_enps,
        CAST(desempenho AS INT) AS desempenho_nine_box,
        CAST(potencial AS INT) AS potencial_nine_box
    FROM source
)
SELECT *
FROM renamed_and_casted
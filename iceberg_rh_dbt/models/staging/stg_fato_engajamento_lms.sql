{{ config(materialized = 'view') }}

WITH source AS (
    SELECT *
    FROM {{ source('hr_bronze', 'Fato_Engajamento_LMS') }}
),
renamed_and_casted AS (
    SELECT 
        MD5(CONCAT(CAST(id_contrato AS STRING), '-', CAST(id_curso AS STRING), '-', data_matricula)) AS sk_engajamento,
        competencia_registro AS mes_competencia,
        CAST(id_contrato AS INT) AS sk_contrato,
        CAST(id_curso AS INT) AS sk_curso,
        CAST(data_matricula AS DATE) AS data_matricula,
        CAST(data_conclusao AS DATE) AS data_conclusao,
        status AS status_curso,
        CAST(nota_final AS DOUBLE) AS nota_final,
        CAST(total_modulos AS INT) AS total_modulos,
        CAST(modulos_concluidos AS INT) AS modulos_concluidos,
        CAST(horas_consumidas AS INT) AS horas_consumidas
    FROM source
)
SELECT *
FROM renamed_and_casted
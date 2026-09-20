{{  config(materialized = 'view') }}

WITH source AS (
    SELECT *
    FROM {{  source('hr_bronze', 'Fato_Vidas_Beneficios') }}
),
renamed_and_casted AS (
    SELECT 
        MD5(CONCAT(chave_familia, '-', nome_beneficiario, '-', competencia)) AS sk_vida_faturada,
        competencia AS mes_competencia,
        CAST(id_contrato AS INT) AS sk_contrato,
        chave_familia,
        nome_titular,
        nome_beneficiario,
        parentesco,
        CAST(idade_vigente AS INT) AS idade_vigente_ans,
        CAST(custo_saude AS DOUBLE) AS custo_saude_faturado,
        CAST(custo_odonto AS DOUBLE) AS custo_odonto_faturado
    FROM source
)
SELECT *
FROM renamed_and_casted
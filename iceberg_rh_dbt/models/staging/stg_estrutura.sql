{{ config(materialized = 'view') }}

WITH source AS (
    SELECT *
    FROM {{ source('hr_bronze', 'Dim_Estrutura')}}
),
renamed_and_casted AS (
    SELECT
      CAST(id_area AS INT) AS sk_area,
      diretoria,
      departamento,
      centro_de_custo,
      estado_sigla,
      cidade_escritorio,
      CAST(lat AS FLOAT) AS latitude,
      CAST(lon AS FLOAT) AS longitude,
      CAST(probabilidade_alocacao AS FLOAT) AS probabilidade_alocacao
    FROM source
)
SELECT *
FROM renamed_and_casted
{{  config(materialized = 'view') }}

WITH source AS (
    SELECT *
    FROM {{  source('hr_bronze', 'Fato_ATS_Funil') }}
),
renamed_and_casted AS (
    SELECT 
        CAST (id_requisicao as INT) AS sk_requisicao,
        competencia_fechamento AS mes_competencia,
        CAST(id_contrato AS INT) AS sk_contrato_gerado,
        origem_contratacao,
        CAST(sla_dias_fechamento AS INT) AS sla_dias_fechamento,
        CAST(qtd_aplicacoes AS INT) AS qtd_aplicacoes,
        CAST(qtd_triagem AS INT) AS qtd_triagem,
        CAST(qtd_entrevistas_rh AS INT) AS qtd_entrevistas_rh,
        CAST(qtd_entrevistas_gestor AS INT) AS qtd_entrevistas_gestor,
        CAST(qtd_ofertas_aceitas AS INT) AS qtd_ofertas_aceitas 
    FROM source
)
SELECT *
FROM renamed_and_casted
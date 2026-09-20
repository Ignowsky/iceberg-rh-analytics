{{ config(materialized = 'table', tags = ['silver', 'financeiro']) }}
with beneficios as (
    select *
    from {{ ref('stg_fato_custo_beneficios') }}
)
select 
    sk_fatura_mensal,
    sk_contrato,
    mes_competencia,
    custo_saude_titular,
    custo_saude_dependentes,
    (custo_saude_titular + custo_saude_dependentes) as custo_saude_total,
    custo_odonto,
    custo_vale_alimentacao,
    custo_total_beneficios,
    case
        when custo_saude_dependentes > (custo_saude_titular * 2) then 1
        else 0
    end as flag_alto_custo_dependente
from beneficios
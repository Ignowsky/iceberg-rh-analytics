{{ config(materialized = 'table', tags = ['silver', 'transacional']) }}

with mov as (
    select *
    from {{ ref('stg_movimentacoes') }}
)
select 
    sk_contrato,
    data_evento,
    tipo_evento,
    sk_cargo_anterior,
    sk_novo_cargo,
    salario_anterior,
    salario_novo,
    percentual_aumento,
    ganho_efetivo,
    case
        when tipo_evento = 'Promoção' and percentual_aumento < 0.10 then 'Promoção Baixo Impacto Financeiro'
        when tipo_evento = 'Promoção' and percentual_aumento >= 0.10 then 'Promoção Alto Impacto Financeiro'
        else 'Movimentação Lateral / Mérito'
    end as analise_movimentacao
from mov
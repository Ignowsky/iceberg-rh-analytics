{{ config(materialized = 'table', tags = ['silver', 'transacional']) }}

with ponto as (
    select *
    from {{ ref('stg_fato_ponto_mensal') }}
),
colaboradores as (
    select 
        sk_contrato,
        salario_base
    from {{ ref('silver__dim_colaboradores') }}
)
select 
    p.sk_ponto_mensal,
    c.sk_contrato,
    p.mes_competencia,
    p.horas_trabalhadas,
    p.horas_extras,
    p.horas_faltas,
    -- valor base da hora (considerando 200h mensais clt (5/2))
    cast(
        c.salario_base / 200 as double
    ) as valor_hora_base,
    cast(
        (c.salario_base / 200) * 1.5 * p.horas_extras as double
    ) as custo_hora_extra,
    case
        when p.horas_extras > 40 then 'Risco de Burnout / Passivo'
        else 'Dentro da Margem'
    end as alerta_jornada
from ponto p
inner join colaboradores c
    on p.sk_contrato = c.sk_contrato
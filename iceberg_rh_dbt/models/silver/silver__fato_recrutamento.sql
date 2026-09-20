{{ config(materialized = 'table', tags = ['silver', 'recrutamento']) }}
with requisicoes as (
    select *
    from {{ ref('stg_fato_requisicoes_vagas') }}
),
funil as (
    select *
    from {{ ref('stg_fato_ats_funil') }}
)
select
    r.sk_requisicao,
    r.sk_area,
    r.sk_cargo,
    r.data_abertura,
    r.data_fechamento,
    r.tipo_vaga,
    r.status as status_requisicao,
    f.origem_contratacao,
    f.sla_dias_fechamento,

    -- calculo do time to fill
    cast(datediff(coalesce(r.data_fechamento, current_date()), r.data_abertura) as int) as dias_em_aberto,
    -- flag de aderencia ao sla
    case
        when cast(
            datediff(r.data_fechamento, r.data_abertura) as int
        ) <= f.sla_dias_fechamento then 1
        else 0
    end as flag_sla_cumprido,
    f.qtd_aplicacoes,
    f.qtd_triagem,
    f.qtd_entrevistas_rh,
    f.qtd_entrevistas_gestor,
    f.qtd_ofertas_aceitas,
    -- taxa de conversão
    case
        when f.qtd_aplicacoes > 0 then cast(f.qtd_ofertas_aceitas as double) / f.qtd_aplicacoes
        else 0
    end as taxa_conversao_funil
from requisicoes r
left join funil f
    on r.sk_requisicao = f.sk_requisicao

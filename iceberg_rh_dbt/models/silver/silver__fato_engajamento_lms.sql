{{ config(materialized = 'table', tags = ['silver', 'desenvolvimento']) }}

with lms as (
    select *
    from {{ ref('stg_fato_engajamento_lms') }}
),
cursos as (
    select *
    from {{ ref('stg_cursos') }}
)
select 
    l.sk_engajamento,
    l.sk_contrato,
    l.sk_curso,
    l.mes_competencia,
    l.data_matricula,
    l.data_conclusao,
    l.status_curso,
    l.nota_final,
    l.modulos_concluidos,
    l.horas_consumidas,
    c.nome_curso,
    c.trilha_conhecimento,
    -- CAlculo de progresso do colaborador
    cast(
        l.modulos_concluidos as double
    ) / cast (
        l.total_modulos as double
    ) as percentual_conclusao
from lms l
inner join cursos c
    on l.sk_curso = c.sk_curso
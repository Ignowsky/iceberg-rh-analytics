{{  config(materialized = 'table', tags = ['silver', 'perfomance']) }}

with avaliacao as (
    select *
    from {{ ref('stg_fato_avaliacao') }}
)
select 
    sk_avaliacao,
    sk_contrato,
    ano_avaliacao,
    nota_desempenho,
    nota_potencial,
    eixo_desempenho,
    eixo_potencial,
    quadrante_9box,
    -- Identificação de talentos
    case
        when eixo_desempenho = 'Alto' and eixo_potencial = 'Alto' then 1
        else 0
    end as flag_high_achiever
from avaliacao
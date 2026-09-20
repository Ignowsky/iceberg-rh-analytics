{{ config(materialized = 'table', tags = ['silver', 'clima']) }}

with clima as (
    select *
    from {{ ref('stg_fato_pesquisa_clima') }}
)
select 
    sk_pesquisa_clima,
    sk_contrato,
    data_pesquisa_clima,
    nota_enps,
    grupo as classificacao_enps,
    case
        when grupo = 'Promotor' then 1
        when grupo = 'Detrator' then -1
        else 0
    end as score_enps_calculos
from clima
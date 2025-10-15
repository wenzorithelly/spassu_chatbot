
/*
1. Quais os 5 piores/melhores resultados de venda por loja 
2. Qual o produto com pior resultado de venda (comparar com forecast e também com A-1 <<<>>> Talvez seja interessante já trazer a 
    hierarquia desse produto, considerando DPTO > Secao > Categoria > Subcat)
3. Qual a receita bruta do dia? (Talvez trazer mais indicadores, como Custo, Lucro Bruto, Cupom, %Margem)
4. Quais são os piores/melhores resultados de ruptura por loja? Ou por produto.
5. Quais os produtos com maior/menor margem para a CIA. 
6. Como está o resultado do mês em comparação com o mês passado? E em comparação ao mesmo mês do ano passado?
7. Compare o resultado de ontem, com o mesmo dia da semana para o ano anterior. (Exemplo: 02/09/2025 terça vs 03/09/2024 terça)
8. FICARÁ PARA A PROXIMA VERSAO - Quem compra esse produto compra o que também?
9. FICARÁ PARA A PROXIMA VERSAO - Esse produto está presente em quantas cestas?
10. FICARÁ PARA A PROXIMA VERSAO - Quanto de receita bruta esse produto carrega?
*/

select top 3 * from [4_TMP].REL_CHATBOT; -- Receita item
select top 3 * from [4_TMP].TMP_ORCAMENTO_DIGITAL_CHATBOT;
select top 3 * from [4_TMP].TMP_RUPTURA_CHATBOT;
select top 3 * from [4_TMP].TMP_FORECAST_CHATBOT; -- Forcast Loja Dia
select top 3 * from [3_REF].DIM_TEMPO;

----------------------------------------------------------------------
-- Questão 1) Quais os 5 piores/melhores resultados de venda por loja 
----------------------------------------------------------------------

-- 5 melhores lojas em vendas
select top 5 
COD_NOM_LOJA,
    SUM(VLR_RECEITA_BRUTA) AS RECEITA_BRUTA
from [4_TMP].REL_CHATBOT
group by COD_NOM_LOJA
order by RECEITA_BRUTA desc;


-- 5 piores lojas em vendas
select top 5 
COD_NOM_LOJA,
    SUM(VLR_RECEITA_BRUTA) AS RECEITA_BRUTA
from [4_TMP].REL_CHATBOT
group by COD_NOM_LOJA
order by RECEITA_BRUTA;

----------------------------------------------------------------------
-- Questão 2) Qual o produto com pior resultado de venda
----------------------------------------------------------------------

-- Pior produto de vendas comparado com forecast
select top 1 
    NOM_DEPARTAMENTO, 
    NOM_SECAO, NOM_CATEGORIA, 
    NOM_SUBCATEGORIA, PRODUTO, 
    SUM(c.VLR_RECEITA_BRUTA) AS RECEITA_BRUTA, 
    SUM(f.VLR_RECEITA_BRUTA) AS FORECAST 
from [4_TMP].REL_CHATBOT c 
    left join [4_TMP].TMP_FORECAST_CHATBOT f 
    on c.SK_TEMPO = f.SK_TEMPO 
    AND c.SK_LOJA = f.SK_LOJA 
    AND c.SK_CATEGORIA_HIERQ_MERCADOLOGICA = f.SK_CATEGORIA_HIERQ_MERCADOLOGICA 
where c.VLR_RECEITA_LIQUIDA > 0 
group by NOM_DEPARTAMENTO, NOM_SECAO, NOM_CATEGORIA, NOM_SUBCATEGORIA, PRODUTO 
order by RECEITA_BRUTA;

-- Pior produto de vendas comparado com o ano anterior
WITH vendas AS (
    SELECT 
        c.PRODUTO,
        t.DAT_ANO as ANO,
        SUM(c.VLR_RECEITA_BRUTA) AS RECEITA_BRUTA
    FROM [4_TMP].REL_CHATBOT c
    JOIN [3_REF].DIM_TEMPO t
        ON t.SK_TEMPO = c.SK_TEMPO
    WHERE c.VLR_RECEITA_BRUTA > 0
    GROUP BY c.PRODUTO, t.DAT_ANO
)
SELECT 
    v1.PRODUTO,
    v1.RECEITA_BRUTA AS VENDAS_ATUAIS,
    v2.RECEITA_BRUTA AS VENDAS_ANTERIORES,
    (v1.RECEITA_BRUTA - v2.RECEITA_BRUTA) AS DIFERENCA
FROM vendas v1
LEFT JOIN vendas v2
    ON v1.PRODUTO = v2.PRODUTO
   AND v1.ANO = v2.ANO + 1   -- compara ano com o anterior
ORDER BY DIFERENCA ASC;   -- ou pelo menor resultado do ano atual


----------------------------------------------------------------------
-- Questão 3) Qual a receita bruta do dia
----------------------------------------------------------------------

-- Receita bruta do dia
SELECT 
    t.DATA,
    SUM(VLR_RECEITA_BRUTA) AS SOMA_RECEITA_BRUTA,
    SUM(VLR_LUCRO_BRUTO) AS SOMA_LUCRO_BRUTO,
    SUM(QTD_ITEM_CUPOM) AS SOMA_QTD_CUPOM,
    CONVERT(INT, SUM(VLR_CUSTO)) SOMA_CUSTO,
    SUM(c.VLR_LUCRO_BRUTO) / NULLIF(SUM(c.VLR_RECEITA_LIQUIDA), 0) AS MARGEM
FROM [4_TMP].REL_CHATBOT c
LEFT JOIN [3_REF].DIM_TEMPO t
ON t.SK_TEMPO = c.SK_TEMPO
WHERE t.DATA = GETDATE()  -- filtra o dia atual
GROUP BY t.DATA

-- Receita bruta de um dia específico (NAO SEI SE VAI PRECISAR DESSA QUERY)
DECLARE @DATA_ALVO DATE = '2025-09-01'; -- coloque a data desejada
SELECT 
    t.DATA,
    SUM(VLR_RECEITA_BRUTA) AS SOMA_RECEITA_BRUTA,
    SUM(VLR_LUCRO_BRUTO) AS SOMA_LUCRO_BRUTO,
    SUM(QTD_ITEM_CUPOM) AS SOMA_QTD_CUPOM,
    CONVERT(INT, SUM(VLR_CUSTO)) SOMA_CUSTO,
    SUM(c.VLR_LUCRO_BRUTO) / NULLIF(SUM(c.VLR_RECEITA_LIQUIDA), 0) AS MARGEM
FROM [4_TMP].REL_CHATBOT c
LEFT JOIN [3_REF].DIM_TEMPO t
ON t.SK_TEMPO = c.SK_TEMPO
WHERE t.DATA = @DATA_ALVO
GROUP BY t.DATA;


-------------------------------------------------------------------------------------------
-- Questão 4) Quais são os piores/melhores resultados de ruptura por loja? Ou por produto.
-------------------------------------------------------------------------------------------

-- TOP 10 melhores LOJA por ruptura
SELECT TOP 10 
    COD_NOM_LOJA,
    SUM(FLG_RUPTURA) AS TOTAL_RUPTURAS,
    COUNT(*) AS TOTAL_REGISTROS,
    CAST(100.0 * SUM(FLG_RUPTURA) / COUNT(*) AS DECIMAL(5,2)) AS PCT_RUPTURA
FROM [4_TMP].TMP_RUPTURA_CHATBOT
GROUP BY COD_NOM_LOJA
ORDER BY PCT_RUPTURA

-- TOP 10 piores LOJA por ruptura
SELECT TOP 10 
    COD_NOM_LOJA,
    SUM(FLG_RUPTURA) AS TOTAL_RUPTURAS,
    COUNT(*) AS TOTAL_REGISTROS,
    CAST(100.0 * SUM(FLG_RUPTURA) / COUNT(*) AS DECIMAL(5,2)) AS PCT_RUPTURA
FROM [4_TMP].TMP_RUPTURA_CHATBOT
GROUP BY COD_NOM_LOJA
ORDER BY PCT_RUPTURA DESC

-- TOP 10 melhores produtos
SELECT TOP 10 
    PRODUTO,
    SUM(FLG_RUPTURA) AS TOTAL_RUPTURAS,
    COUNT(*) AS TOTAL_REGISTROS,
    CAST(100.0 * SUM(FLG_RUPTURA) / COUNT(*) AS DECIMAL(5,2)) AS PCT_RUPTURA
FROM [4_TMP].TMP_RUPTURA_CHATBOT
GROUP BY PRODUTO
ORDER BY PCT_RUPTURA 

-- TOP 10 piores produtos
SELECT TOP 10 
    PRODUTO,
    SUM(FLG_RUPTURA) AS TOTAL_RUPTURAS,
    COUNT(*) AS TOTAL_REGISTROS,
    CAST(100.0 * SUM(FLG_RUPTURA) / COUNT(*) AS DECIMAL(5,2)) AS PCT_RUPTURA
FROM [4_TMP].TMP_RUPTURA_CHATBOT
GROUP BY PRODUTO
ORDER BY TOTAL_RUPTURAS DESC

-- ruptura por produto e dia (validacao da query apenas)
SELECT
    SK_TEMPO,
    PRODUTO,
    SUM(FLG_RUPTURA) AS TOTAL_RUPTURAS,
    COUNT(*) AS TOTAL_REGISTROS,
    CAST(100.0 * SUM(FLG_RUPTURA) / COUNT(*) AS DECIMAL(5,2)) AS PCT_RUPTURA
FROM [4_TMP].TMP_RUPTURA_CHATBOT
WHERE SK_TEMPO LIKE '202509%'
AND PRODUTO LIKE '123198%'
GROUP BY SK_TEMPO, PRODUTO
ORDER BY PCT_RUPTURA DESC;


----------------------------------------------------------------------
-- Questão 5) Quais os produtos com maior/menor margem para a CIA
----------------------------------------------------------------------

-- Top 10 produtos com mais margem
SELECT TOP 10
    c.PRODUTO,
    SUM(c.VLR_LUCRO_BRUTO) / NULLIF(SUM(c.VLR_RECEITA_LIQUIDA), 0) AS MARGEM
FROM [4_TMP].REL_CHATBOT c
LEFT JOIN [3_REF].DIM_TEMPO t
    ON t.SK_TEMPO = c.SK_TEMPO
WHERE c.VLR_LUCRO_BRUTO > 0 AND c.VLR_RECEITA_LIQUIDA > 0
GROUP BY c.PRODUTO
ORDER BY MARGEM DESC;

-- Top 10 produtos com menor margem
SELECT TOP 10
    c.PRODUTO,
    c.VLR_LUCRO_BRUTO,
    c.VLR_RECEITA_LIQUIDA,
    SUM(c.VLR_LUCRO_BRUTO) / NULLIF(SUM(c.VLR_RECEITA_LIQUIDA), 0) AS MARGEM
FROM [4_TMP].REL_CHATBOT c
LEFT JOIN [3_REF].DIM_TEMPO t
    ON t.SK_TEMPO = c.SK_TEMPO
WHERE c.VLR_LUCRO_BRUTO > 0 AND c.VLR_RECEITA_LIQUIDA > 0
GROUP BY c.PRODUTO, c.VLR_LUCRO_BRUTO, c.VLR_RECEITA_LIQUIDA
ORDER BY MARGEM;

 
----------------------------------------------------------------------------
-- Questão 6) Como está o resultado do mês em comparação com o mês passado? 
-- E em comparação ao mesmo mês do ano passado?
----------------------------------------------------------------------------

-- Comparação de vendas
WITH VENDAS_MENSAL AS (
    SELECT
        t.DAT_ANO AS ANO,
        t.DAT_MES AS MES,
        SUM(VLR_RECEITA_BRUTA) AS RECEITA_BRUTA
    FROM [4_TMP].REL_CHATBOT c
        LEFT JOIN [3_REF].DIM_TEMPO t
        ON t.SK_TEMPO = c.SK_TEMPO
    GROUP BY t.DAT_ANO, t.DAT_MES
)
SELECT 
    v1.ANO,
    v1.MES,
    v1.RECEITA_BRUTA AS RECEITA_ATUAL,
    v2.RECEITA_BRUTA AS RECEITA_MES_PASSADO,
    v3.RECEITA_BRUTA AS RECEITA_MES_ANO_PASSADO,
    (v1.RECEITA_BRUTA - v2.RECEITA_BRUTA) AS DIFERENCA_MES_PASSADO,
    (v1.RECEITA_BRUTA - v3.RECEITA_BRUTA) AS DIFERENCA_ANO_PASSADO
FROM VENDAS_MENSAL v1
LEFT JOIN VENDAS_MENSAL v2 
    ON v2.ANO = CASE WHEN v1.MES = 1 THEN v1.ANO - 1 ELSE v1.ANO END
   AND v2.MES = CASE WHEN v1.MES = 1 THEN 12 ELSE v1.MES - 1 END
LEFT JOIN VENDAS_MENSAL v3 
    ON v3.ANO = v1.ANO - 1 
   AND v3.MES = v1.MES
WHERE v1.ANO = YEAR(GETDATE())
  --AND v1.MES = MONTH(GETDATE());  -- filtra só o mês atual (comentei pq não temos dados do mês atual ainda)

------------------------------------------------------------------------------------------
-- Questão 7) Compare o resultado de ontem, com o mesmo dia da semana para o ano anterior.
------------------------------------------------------------------------------------------
-- Hoje temos dados de 29/07 a 03/08/2024 e 01/08/2025 a 11/09/2025

WITH VENDAS_DIA AS (
    SELECT
        t.DATA,
        SUM(c.VLR_RECEITA_BRUTA) AS RECEITA_BRUTA
    FROM [4_TMP].REL_CHATBOT c
    LEFT JOIN [3_REF].DIM_TEMPO t
        ON t.SK_TEMPO = c.SK_TEMPO
    GROUP BY t.DATA
)
SELECT 
    v1.DATA AS DATA_ATUAL,
    v1.RECEITA_BRUTA AS RECEITA_ATUAL,
    v2.DATA AS DATA_ANO_PASSADO,
    v2.RECEITA_BRUTA AS RECEITA_ANO_PASSADO,
    (v1.RECEITA_BRUTA - v2.RECEITA_BRUTA) AS DIFERENCA_ABS,
    ((v1.RECEITA_BRUTA - v2.RECEITA_BRUTA) * 100.0 / NULLIF(v2.RECEITA_BRUTA,0)) AS DIFERENCA_PCT
FROM VENDAS_DIA v1
LEFT JOIN VENDAS_DIA v2 
       ON DATEPART(WEEKDAY, v2.DATA) = DATEPART(WEEKDAY, v1.DATA)
      AND v2.DATA BETWEEN DATEADD(DAY, -370, v1.DATA) AND DATEADD(DAY, -360, v1.DATA)
--WHERE v1.DATA = '2025-08-01';  





 
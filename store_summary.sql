CREATE OR REPLACE TABLE RETAIL_INTELLIGENCE.GOLD.STORE_SUMMARY AS
SELECT
    d.Store, d.StoreType, d.Assortment, d.CompetitionDistance,
    a.avg_sales,
    f.total_forecasted_sales_12mo,
    r.RiskTier
FROM RETAIL_INTELLIGENCE.GOLD.DIM_STORE d
LEFT JOIN (
    SELECT Store, AVG(Sales) AS avg_sales
    FROM RETAIL_INTELLIGENCE.STAGING.SILVER_TRAIN WHERE Open = 1
    GROUP BY Store
) a ON d.Store = a.Store
LEFT JOIN (
    SELECT Store, SUM(PredictedSales) AS total_forecasted_sales_12mo
    FROM RETAIL_INTELLIGENCE.STAGING.SALES_FORECAST
    GROUP BY Store
) f ON d.Store = f.Store
LEFT JOIN RETAIL_INTELLIGENCE.GOLD.FACT_STORE_RISK r ON d.Store = r.Store;
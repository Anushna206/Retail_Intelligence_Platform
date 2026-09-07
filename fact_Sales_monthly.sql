CREATE OR REPLACE TABLE RETAIL_INTELLIGENCE.GOLD.FACT_SALES_MONTHLY AS
SELECT
    Store,
    DATE_TRUNC('month', Date) AS month,
    SUM(Sales) AS Sales,
    FALSE AS IsForecast,
    NULL AS ConfidenceTier,
    AVG(Customers) AS AvgCustomers,
    SUM(CASE WHEN Promo = 1 THEN 1 ELSE 0 END) AS PromoDays,
    SUM(CASE WHEN StateHoliday != '0' THEN 1 ELSE 0 END) AS StateHolidayDays,
    SUM(CASE WHEN SchoolHoliday = 1 THEN 1 ELSE 0 END) AS SchoolHolidayDays
FROM RETAIL_INTELLIGENCE.STAGING.SILVER_TRAIN
WHERE Open = 1
GROUP BY Store, DATE_TRUNC('month', Date)
UNION ALL
SELECT
    Store,
    ForecastMonth AS month,
    PredictedSales AS Sales,
    TRUE AS IsForecast,
    ConfidenceTier,
    NULL AS AvgCustomers,
    NULL AS PromoDays,
    NULL AS StateHolidayDays,
    NULL AS SchoolHolidayDays
FROM RETAIL_INTELLIGENCE.STAGING.SALES_FORECAST;
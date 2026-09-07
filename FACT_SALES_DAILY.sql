CREATE OR REPLACE TABLE RETAIL_INTELLIGENCE.GOLD.FACT_SALES_DAILY AS
SELECT
    Store,
    Date,
    DayOfWeek,
    Sales,
    Customers,
    Open,
    Promo,
    StateHoliday,
    SchoolHoliday
FROM RETAIL_INTELLIGENCE.STAGING.SILVER_TRAIN
WHERE Open = 1;
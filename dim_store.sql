CREATE OR REPLACE TABLE RETAIL_INTELLIGENCE.GOLD.DIM_STORE AS
SELECT Store, StoreType, Assortment, CompetitionDistance,
       HasCompetitionInfo, CompetitionOpenSinceMonth, CompetitionOpenSinceYear,
       Promo2, PromoInterval
FROM RETAIL_INTELLIGENCE.STAGING.SILVER_STORE;
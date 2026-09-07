-- ============================================================
-- SETUP: Chat history table + stage for semantic model
-- Run this once in a Snowsight worksheet
-- ============================================================

USE DATABASE RETAIL_INTELLIGENCE;
USE SCHEMA GOLD;

-- 1. Chat history table
CREATE TABLE IF NOT EXISTS RETAIL_INTELLIGENCE.GOLD.CHAT_HISTORY (
    session_id       STRING,
    user_name        STRING DEFAULT CURRENT_USER(),
    question         STRING,
    answer           STRING,
    sql_generated    STRING,      -- the SQL Cortex Analyst ran, for auditing
    was_in_scope     BOOLEAN,     -- did it pass the guardrail check
    response_time_ms NUMBER,
    created_at       TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- 2. Stage to hold the semantic model YAML file
CREATE STAGE IF NOT EXISTS RETAIL_INTELLIGENCE.GOLD.SEMANTIC_MODELS
    DIRECTORY = (ENABLE = TRUE)
    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

-- After running this, upload semantic_model.yaml to the stage:
-- Snowsight -> Data -> Databases -> RETAIL_INTELLIGENCE -> GOLD -> Stages -> SEMANTIC_MODELS -> Upload
-- (or use SnowSQL PUT command from CLI)

-- 3. Quick sanity checks on categorical values (run once, verify against assumptions in semantic_model.yaml)
SELECT DISTINCT StoreType FROM RETAIL_INTELLIGENCE.GOLD.DIM_STORE ORDER BY 1;
SELECT DISTINCT Assortment FROM RETAIL_INTELLIGENCE.GOLD.DIM_STORE ORDER BY 1;
SELECT DISTINCT RiskTier FROM RETAIL_INTELLIGENCE.GOLD.FACT_STORE_RISK ORDER BY 1;
SELECT DISTINCT PromoInterval FROM RETAIL_INTELLIGENCE.GOLD.DIM_STORE ORDER BY 1;


LIST @RETAIL_INTELLIGENCE.GOLD.SEMANTIC_MODELS;
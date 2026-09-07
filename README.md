# 🏪 Retail Intelligence Platform

An end-to-end retail intelligence platform built using **AWS S3, Databricks, Snowflake, Machine Learning, Streamlit, and Snowflake Cortex Analyst**.

The platform transforms raw Rossmann retail data into clean, analytics-ready data and predictive insights that help answer:

- What happened?
- Why did it happen?
- What is likely to happen next?
- Which stores need attention?

---

## 📌 Project Overview

Retail businesses generate large amounts of data from sales, customers, promotions, holidays, stores, and competition.

The challenge is to transform this raw data into reliable information that can support business decisions.

This project builds a complete data and analytics platform that:

1. Ingests raw retail data into AWS S3
2. Processes and transforms data using Databricks
3. Implements a Bronze and Silver data architecture
4. Builds machine learning models for sales forecasting and store risk
5. Stores business-ready Gold data in Snowflake
6. Provides interactive analytics through Streamlit
7. Enables natural-language analytics using Snowflake Cortex Analyst

---

## 🎯 Objectives

- Build an end-to-end retail data pipeline
- Implement Medallion Architecture
- Clean and transform raw retail data
- Perform feature engineering
- Forecast store sales for the next 12 months
- Classify stores into High, Medium, and Low risk
- Build an analytics-ready Gold layer in Snowflake
- Develop an interactive Streamlit dashboard
- Enable natural-language querying using Snowflake Cortex Analyst

---

# 🏗️ Architecture

```text
                    ┌──────────────────┐
                    │   Raw CSV Data   │
                    │ Train / Test /   │
                    │ Store            │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     AWS S3       │
                    │  Raw Data Store  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │       Databricks       │
                    │                        │
                    │ Bronze → Silver        │
                    │                        │
                    │ Cleaning               │
                    │ Transformation         │
                    │ Feature Engineering    │
                    └───────────┬────────────┘
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
        ┌──────────────────┐          ┌──────────────────┐
        │ Sales Forecasting│          │ Store Risk       │
        │ Random Forest    │          │ Classification   │
        │ Regressor        │          │ Random Forest    │
        └─────────┬────────┘          └─────────┬────────┘
                  │                             │
                  └──────────────┬──────────────┘
                                 ▼
                       ┌──────────────────┐
                       │    Snowflake     │
                       │      Gold        │
                       │                  │
                       │ Facts / Dimension│
                       │ Store Summary    │
                       └────────┬─────────┘
                                │
                   ┌────────────┴────────────┐
                   │                         │
                   ▼                         ▼
          ┌─────────────────┐       ┌──────────────────┐
          │    Streamlit    │       │ Cortex Analyst   │
          │    Dashboard    │       │     AI Bot       │
          └─────────────────┘       └──────────────────┘
```

---

# 📊 Data

The project uses the **Rossmann Store Sales** dataset.

### Source datasets

| Dataset | Description |
|---|---|
| `train.csv` | Historical daily store sales |
| `test.csv` | Store records for the prediction period |
| `store.csv` | Store attributes, competition and promotion information |

### Key fields

- Store
- Date
- Sales
- Customers
- Open
- Promo
- StateHoliday
- SchoolHoliday
- StoreType
- Assortment
- CompetitionDistance
- Promo2
- PromoInterval

---

# 🥉 Bronze Layer

The Bronze layer stores the raw data ingested from the source files.

### Purpose

- Preserve raw source data
- Maintain the original structure
- Separate ingestion from transformation
- Provide a reliable starting point for downstream processing

---

# 🥈 Silver Layer

The Silver layer contains cleaned and enriched data prepared for analytics and machine learning.

### Transformations performed

- Null-value handling
- Duplicate validation
- Data validation
- Store attribute integration
- Date feature engineering
- Promotion feature engineering
- Competition feature engineering

### Engineered features

- Year
- Month
- Week
- Day
- Quarter
- IsWeekend
- IsPromo2Active
- CompetitionStartDate
- CompetitionAgeMonths
- HasCompetitionInfo

The Silver layer provides a clean and feature-ready dataset for the machine learning models.

---

# 🤖 Machine Learning

Two machine learning models were developed.

## 1. Next 12-Month Sales Forecasting

### Business Question

> How much sales can each store generate over the next year?

### Algorithm

**RandomForestRegressor**

### Process

```text
Silver Daily Sales
        ↓
Filter Open Stores
        ↓
Aggregate to Store-Month
        ↓
Create Time-Series Features
        ↓
Lag 1
Lag 12
Rolling Average 3
        ↓
Handle Missing History
        ↓
Time-Based Validation
        ↓
Random Forest Regressor
        ↓
Recursive 12-Month Forecast
```

### Features used

- Lag 1 month sales
- Lag 12 month sales
- 3-month rolling average
- Month
- Quarter
- Year
- StoreType
- Assortment
- CompetitionDistance
- HasCompetitionInfo
- CompetitionAgeMonths
- Promo2

### Handling Missing History

Some stores do not have enough historical data to calculate lag and rolling features.

Instead of dropping those records, missing historical feature values were filled using the **StoreType peer-group average**.

This preserves stores with limited history while avoiding the incorrect assumption that missing historical sales represent zero sales.

### Validation

A **time-based validation split** was used instead of a random split to preserve the chronological nature of the sales data.

### Evaluation Metrics

- MAE
- RMSE
- R²

### Forecast Period

The model generates a recursive 12-month forecast from:

**August 2015 → July 2016**

### Confidence Tier

Forecasts are assigned:

- **High**
- **Medium**
- **Low**

based on the forecast horizon.

The Confidence Tier is a business-oriented indicator of forecast horizon and is **not a statistical confidence interval**.

---

## 2. Store Risk Classification

### Business Question

> Which stores need attention?

### Algorithm

**RandomForestClassifier**

### Risk Categories

- High
- Medium
- Low

### Store-Level Features

The model uses features related to:

- Average sales
- Sales volatility
- Customer trends
- Sales trends
- Promotion behavior
- Weekend performance
- Peer performance
- Competition
- StoreType
- Assortment

### Risk Score

A composite risk score is created using:

- Sales trend
- Customer trend
- Peer performance
- Sales volatility

The resulting scores are divided into approximately equal High, Medium, and Low risk groups.

### Evaluation

The model uses:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion Matrix

---

# ❄️ Snowflake Gold Layer

The Gold layer contains business-ready data used by the dashboard and analytics applications.

## Gold Tables

### `DIM_STORE`

Contains descriptive store information and store attributes.

### `FACT_SALES_DAILY`

Contains sales at:

```text
Store + Day
```

grain.

This preserves detailed daily-level analysis.

### `FACT_SALES_MONTHLY`

Contains sales at:

```text
Store + Month
```

grain.

### Monthly Aggregations

| Measure | Aggregation |
|---|---|
| Sales | SUM |
| Customers | AVG |
| Promotion Days | COUNT |
| School Holiday Days | COUNT |
| State Holiday Days | COUNT |

The monthly fact also contains information that distinguishes actual and forecast records.

### `FACT_STORE_RISK`

Contains store-level machine learning risk predictions.

Includes:

- Risk Tier
- High-risk probability
- Medium-risk probability
- Low-risk probability

### `STORE_SUMMARY`

Contains store-level business metrics such as:

- Average Sales
- Average Customers
- 12-Month Forecasted Sales
- Risk Tier
- Store Type
- Assortment
- Competition Distance
- Peer Sales Performance

---

# 📈 Streamlit Dashboard

The Streamlit application provides a business-friendly interface over the Snowflake Gold layer.

## Dashboard Features

### Portfolio Overview

- Sales KPIs
- Actual vs Forecast Sales
- Store Risk Overview
- Store Type Analysis
- Assortment Analysis
- Date Filtering

### Store Detail Lookup

Users can select an individual store and view:

- Store Type
- Assortment
- Average Sales
- Average Customers
- 12-Month Forecast
- Risk Tier
- Competition Distance
- Peer Sales Performance

The dashboard allows business users to explore the data without directly writing SQL queries.

---

# 🤖 AI-Powered Analytics Bot

The platform includes a natural-language analytics bot powered by **Snowflake Cortex Analyst**.

Users can ask questions such as:

```text
Which stores have the highest sales?

Which stores are high risk?

What is the forecast for Store 3?

Which store type performs best?

How does promotion affect sales?
```

### How it works

```text
User Question
      ↓
Guardrail
      ↓
Cortex Analyst
      ↓
Semantic Model
      ↓
Generated SQL
      ↓
Snowflake
      ↓
Query Result
      ↓
Business-Friendly Response
      ↓
Streamlit
```

The semantic model provides business definitions and relationships to Cortex Analyst so that natural-language questions can be translated into SQL.

The application also maintains conversation context for follow-up questions.

---

# 🔄 End-to-End Data Flow

```text
Raw CSV Files
      ↓
AWS S3
      ↓
Databricks Bronze
      ↓
Databricks Silver
      ↓
Feature Engineering
      ↓
Machine Learning
      ↓
Snowflake Staging
      ↓
Snowflake Gold
      ↓
Streamlit Dashboard
      ↓
Business Insights
```

---

# 🛠️ Technology Stack

| Category | Technology |
|---|---|
| Cloud Storage | AWS S3 |
| Data Engineering | Databricks |
| Data Processing | PySpark / SQL |
| Architecture | Medallion Architecture |
| Machine Learning | Scikit-learn |
| Sales Forecasting | RandomForestRegressor |
| Risk Classification | RandomForestClassifier |
| Data Warehouse | Snowflake |
| AI Analytics | Snowflake Cortex Analyst |
| Dashboard | Streamlit |
| Visualization | Plotly |
| Programming | Python / SQL |

---

# 🎯 Business Value

The platform provides:

### 1. Faster Decision Making
Replaces fragmented analysis with centralized business insights.

### 2. Better Demand Planning
12-month sales forecasts support future planning.

### 3. Early Store Risk Detection
Identifies stores that may require management attention.

### 4. Promotion and Holiday Insights
Helps understand how promotions and holidays relate to sales.

### 5. Centralized Analytics
Provides a curated Gold layer for consistent reporting.

### 6. Self-Service Analytics
Allows users to explore business data through Streamlit and natural-language questions.

---

# 🚀 Future Enhancements

- Automated pipeline orchestration
- Automated model retraining
- Model monitoring
- More advanced forecasting models
- Statistical prediction intervals
- Automated anomaly detection
- Real-time data ingestion
- Additional business KPIs

---

# 👩‍💻 Author

**Anushna Tanniru**

Retail Intelligence Platform

**Data Engineering | Machine Learning | Analytics**

---

## ⭐ Project Summary

> From raw retail data to predictive intelligence — building an end-to-end platform that helps businesses understand what happened, what is happening, and what is likely to happen next.

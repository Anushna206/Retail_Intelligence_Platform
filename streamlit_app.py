"""
Retail Intelligence Dashboard + Chatbot
Run this as a Streamlit in Snowflake (SiS) app.
Snowsight -> Projects -> Streamlit -> + Streamlit App -> paste this in.
"""

import streamlit as st
import pandas as pd
import time
import uuid
import json
import _snowflake
from snowflake.snowpark.context import get_active_session

session = get_active_session()

st.set_page_config(page_title="Retail Intelligence", layout="wide")

# ---------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------
SEMANTIC_MODEL_PATH = "@RETAIL_INTELLIGENCE.GOLD.SEMANTIC_MODELS/semantic_model.yaml"

# Keywords/topics the bot is allowed to discuss. Used for the scope guardrail.
ALLOWED_TOPICS = (
    "store sales, revenue, forecasts, risk tiers, store type, assortment, "
    "competition distance and competitor open dates, promotions (Promo2 "
    "and promo intervals), and store performance metrics "
    "in the RETAIL_INTELLIGENCE dataset"
)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ---------------------------------------------------------------
# GUARDRAIL 1: Scope check before we ever call Cortex Analyst
# ---------------------------------------------------------------
def check_scope(question: str) -> bool:
    """Returns True if the question is in scope for this dataset."""
    prompt = f"""You are a scope classifier for a retail analytics chatbot.
The chatbot may ONLY answer questions about: {ALLOWED_TOPICS}.

Question: "{question}"

Reply with exactly one word: YES if this question is answerable using only
store sales/forecast/risk data, or NO if it asks about anything else
(general knowledge, other topics, personal advice, code, etc).
"""
    result = session.sql(
        "SELECT SNOWFLAKE.CORTEX.COMPLETE(?, ?) AS resp",
        params=["claude-sonnet-4-5", prompt]
    ).collect()
    verdict = result[0]["RESP"].strip().upper()
    return verdict.startswith("YES")


# ---------------------------------------------------------------
# GUARDRAIL 2: Call Cortex Analyst (answers ONLY from modeled tables)
# ---------------------------------------------------------------
def ask_cortex_analyst(question: str, history: list) -> dict:
    messages = []
    for m in history[-6:]:  # last few turns for multi-turn context
        messages.append({"role": m["role"], "content": [{"type": "text", "text": m["content"]}]})
    messages.append({"role": "user", "content": [{"type": "text", "text": question}]})

    request_body = {
        "messages": messages,
        "semantic_model_file": SEMANTIC_MODEL_PATH,
    }

    resp = _snowflake.send_snow_api_request(
        "POST",
        "/api/v2/cortex/analyst/message",
        {},
        {},
        request_body,
        {},
        30000,
    )

    if resp["status"] != 200:
        return {"error": f"Cortex Analyst request failed (status {resp['status']})"}

    content = json.loads(resp["content"])
    return content


def extract_answer(analyst_response: dict):
    """Pull out text answer + generated SQL (if any) from Cortex Analyst response."""
    text_parts = []
    sql = None
    for item in analyst_response.get("message", {}).get("content", []):
        if item.get("type") == "text":
            text_parts.append(item["text"])
        elif item.get("type") == "sql":
            sql = item["statement"]
    return " ".join(text_parts), sql


def log_history(question, answer, sql, in_scope, elapsed_ms):
    session.sql(
        """INSERT INTO RETAIL_INTELLIGENCE.GOLD.CHAT_HISTORY
           (session_id, question, answer, sql_generated, was_in_scope, response_time_ms)
           SELECT ?, ?, ?, ?, ?, ?""",
        params=[st.session_state.session_id, question, answer, sql, in_scope, elapsed_ms]
    ).collect()


# ---------------------------------------------------------------
# LAYOUT: two tabs — Dashboard and Chat
# ---------------------------------------------------------------
tab_dashboard, tab_chat = st.tabs(["📊 Dashboard", "💬 Ask the Data"])

# ---------------- DASHBOARD TAB ----------------
with tab_dashboard:
    st.title("Retail Store Intelligence")

    df = session.table("RETAIL_INTELLIGENCE.GOLD.STORE_SUMMARY").to_pandas()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Stores", f"{df['STORE'].nunique():,}")
    col2.metric("High Risk Stores", f"{(df['RISKTIER'] == 'High').sum():,}")
    col3.metric("Avg 12mo Forecast", f"${df['TOTAL_FORECASTED_SALES_12MO'].mean():,.0f}")

    st.divider()

    f1, f2 = st.columns(2)
    with f1:
        store_type_filter = st.multiselect(
            "Store Type", options=sorted(df["STORETYPE"].dropna().unique()), default=None
        )
    with f2:
        risk_filter = st.multiselect(
            "Risk Tier", options=sorted(df["RISKTIER"].dropna().unique()), default=None
        )

    filtered = df.copy()
    if store_type_filter:
        filtered = filtered[filtered["STORETYPE"].isin(store_type_filter)]
    if risk_filter:
        filtered = filtered[filtered["RISKTIER"].isin(risk_filter)]

    st.dataframe(filtered, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Avg Sales by Store Type")
        st.bar_chart(filtered.groupby("STORETYPE")["AVG_SALES"].mean())
    with c2:
        st.subheader("Store Count by Risk Tier")
        st.bar_chart(filtered["RISKTIER"].value_counts())

# ---------------- CHAT TAB ----------------
with tab_chat:
    st.title("Ask the Data")
    st.caption(f"I can only answer questions about {ALLOWED_TOPICS}.")

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    question = st.chat_input("Ask about store sales, risk, or forecasts...")

    if question:
        st.session_state.chat_messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            start = time.time()
            with st.spinner("Checking question..."):
                in_scope = check_scope(question)

            if not in_scope:
                answer = (
                    "I can only answer questions about store sales, forecasts, "
                    "risk tiers, and related store attributes in this dataset. "
                    "Could you rephrase your question around that?"
                )
                st.write(answer)
                sql_used = None
            else:
                with st.spinner("Querying data..."):
                    result = ask_cortex_analyst(question, st.session_state.chat_messages)

                if "error" in result:
                    answer = "Sorry, I ran into an error answering that. Try rephrasing."
                    sql_used = None
                    st.write(answer)
                else:
                    answer, sql_used = extract_answer(result)
                    st.write(answer)
                    if sql_used:
                        with st.expander("See SQL used"):
                            st.code(sql_used, language="sql")
                        try:
                            result_df = session.sql(sql_used).to_pandas()
                            st.dataframe(result_df, use_container_width=True)
                        except Exception as e:
                            st.caption(f"(Could not preview results: {e})")

            elapsed_ms = int((time.time() - start) * 1000)
            log_history(question, answer, sql_used, in_scope, elapsed_ms)
            st.session_state.chat_messages.append({"role": "assistant", "content": answer})

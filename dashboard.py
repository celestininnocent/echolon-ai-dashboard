# Echolon AI Dashboard (Enhanced Modular Structure)
# -- Built for Streamlit, Demo Data/Placeholders Upgraded Per User Request --
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Echolon AI Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- Theme ---
st.markdown(
    """
    <style>
    body, .stApp, .css-1d391kg, .css-14xtw13 {background-color: #181C24!important; color: #F3F6F9!important;}
    .st-emotion-cache-2trqyj {color: #3ECF8E!important;}
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-1p66bqe {background: #111217 !important;}
    header {background: none!important;}
    .urgent {color:red; font-weight: bold;}
    .owner {color:#3ECF8E!important;}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- SIDEBAR --
with st.sidebar:
    st.title('🧊 Echolon AI')
    st.markdown('---')
    nav = st.radio("Navigation", [
        "Executive Summary",
        "Upload & Data Integration",
        "Industry Benchmarking",
        "What If? Scenario Modeling",
        "Goal Tracking",
        "AI Insights & Recommendations",
        "Collaboration Notes"
    ])
    st.markdown('---')
    notes = st.text_area("💬 Session Notes", "", height=100)
    st.caption('Demo prototype | All data is local/sample only')

st.markdown("# 🧠 Echolon AI Dashboard")
st.caption('Prototyped modular business intelligence dashboard')
st.markdown('---')

# ---- Demo Data ----
np.random.seed(9)
dates = pd.date_range(start="2024-01-01", periods=7)
user_revenue = np.random.randint(90000, 130000, 7)
user_expenses = np.random.randint(50000, 90000, 7)
industry_avg_revenue = user_revenue * np.random.uniform(0.85, 0.95, 7)
industry_avg_expenses = user_expenses * np.random.uniform(1.07, 1.14, 7)
user_customers = np.random.randint(1000, 6000, 7)

industry_ranking = [2,2,1,2,1,1,2]  # Fake ranks

df = pd.DataFrame({
    "Date": dates,
    "Your Revenue": user_revenue,
    "Your Expenses": user_expenses,
    "Industry Revenue": industry_avg_revenue.round(0),
    "Industry Expenses": industry_avg_expenses.round(0),
    "Customers": user_customers,
    "% Diff Revenue": ((user_revenue-industry_avg_revenue)/industry_avg_revenue*100).round(1),
    "% Diff Expenses": ((user_expenses-industry_avg_expenses)/industry_avg_expenses*100).round(1),
    "Revenue Rank": industry_ranking,
})

# --- Executive Summary ---
if nav == "Executive Summary":
    with st.expander("📈 Executive Summary", expanded=True):
        st.markdown(
            "**Overall AI Insight (Demo): Sales growth remains strong; revenue outpaces industry for 4/7 periods. Predict improvement in retention, margin by Q2.**"
        )
        st.metric("Current Revenue ($K)", f"{user_revenue[-1]:,.0f}", delta=f"+{df['% Diff Revenue'].iloc[-1]:.1f}% vs industry")
        st.metric("Current Expenses ($K)", f"{user_expenses[-1]:,.0f}", delta=f"{df['% Diff Expenses'].iloc[-1]:.1f}% vs industry", delta_color="inverse")
        st.metric("Customers", f"{user_customers[-1]:,.0f}")
        st.markdown('---')

# --- Upload Demo (for other modules if user wants) ---
if nav == "Upload & Data Integration":
    st.subheader("📁 Upload & Data Integration")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    try:
        if uploaded_file:
            upload_df = pd.read_csv(uploaded_file)
            st.dataframe(upload_df, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Data preview unavailable. Demo data shown. Reason: {str(e)}")

# --- Industry Benchmarking ---
if nav == "Industry Benchmarking":
    with st.expander("🎯 Industry Benchmarking", expanded=True):
        st.subheader("Revenue & Expenses vs. Industry Averages")
        st.info("AI insight: Your revenue outpaces the industry by {:.1f}% for latest period. Expenses are competitive.".format(df["% Diff Revenue"].iloc[-1]))
        bar_chart = go.Figure()
        bar_chart.add_trace(go.Bar(x=df['Date'], y=df['Your Revenue'], name="Your Revenue", marker_color='#3ECF8E'))
        bar_chart.add_trace(go.Bar(x=df['Date'], y=df['Industry Revenue'], name="Industry Revenue", marker_color="#6781C5"))
        bar_chart.add_trace(go.Bar(x=df['Date'], y=df['Your Expenses'], name="Your Expenses", marker_color='#E86A92'))
        bar_chart.add_trace(go.Bar(x=df['Date'], y=df['Industry Expenses'], name="Industry Expenses", marker_color='#FFD166'))
        bar_chart.update_layout(barmode="group", title="Historical Revenue/Expenses", xaxis_title="Date")
        st.plotly_chart(bar_chart, use_container_width=True)
        pie_chart = go.Figure(go.Pie(
            labels=["Your Revenue","Industry Revenue","Your Expenses","Industry Expenses"],
            values=[user_revenue[-1], industry_avg_revenue[-1], user_expenses[-1], industry_avg_expenses[-1]],
            marker=dict(colors=['#3ECF8E','#6781C5','#E86A92','#FFD166']),
            hole=.3,
            textinfo="label+percent",
        ))
        pie_chart.update_layout(title="Latest Period Revenue/Expense Mix")
        st.plotly_chart(pie_chart, use_container_width=True)
        color_map = df['% Diff Revenue'].map(lambda x: 'background-color: #3ecf8e80;' if x>0 else ('background-color: #FFC30080;' if x>-5 else 'background-color: #e86a9280;'))
        styled_df = df.style.apply(lambda s: color_map if s.name == '% Diff Revenue' else '', axis=0)
        st.dataframe(df.style.background_gradient(subset=["% Diff Revenue","% Diff Expenses"], cmap="Greens"))
        for i in range(len(df)):
            st.markdown(f"<details><summary>🔎 {df['Date'].iloc[i].date()} Commentary</summary><div>"
                f"<b>AI Suggestion:</b> Revenue {'exceeded' if df['% Diff Revenue'].iloc[i]>0 else 'underperformed'} industry by {abs(df['% Diff Revenue'].iloc[i]):.1f}%. "
                f"Ranked {df['Revenue Rank'].iloc[i]} for this period. Expense deviation: {df['% Diff Expenses'].iloc[i]:+.1f}%. "
                "Consider optimizing ad spend or pricing for periods under average. "
                "</div></details>", unsafe_allow_html=True)

# --- What If Scenario Modeling ---
if nav == "What If? Scenario Modeling":
    with st.expander("🤔 What If? Scenario Modeling", expanded=True):
        st.subheader("Interactively Model Revenue & Expenses")
        ad_spend = st.slider("Ad Spend (% of current)", 80, 120, 100, 1)
        price = st.slider("Average Price ($)", 99, 129, 109, 1)
        churn = st.slider("Churn Rate (%)", 1, 20, 7, 1)
        sim_customers = int(user_customers[-1]*(1-churn/100))
        sim_revenue = int(sim_customers * price)
        sim_expenses = int(user_expenses[-1]*ad_spend/100)
        profit = sim_revenue - sim_expenses
        roi = round(100*profit/sim_expenses, 1) if sim_expenses else 0
        st.metric("Simulated Revenue", f"${sim_revenue:,.0f}", delta=f"{sim_revenue-user_revenue[-1]:+,}")
        st.metric("Simulated Expenses", f"${sim_expenses:,.0f}", delta=f"{sim_expenses-user_expenses[-1]:+,}")
        st.metric("Profit", f"${profit:,.0f}")
        st.metric("ROI", f"{roi:.1f}%")
        st.metric("Customer Retention", f"{sim_customers:,}", delta=f"{-churn}% churn")
        chart = go.Figure()
        chart.add_trace(go.Bar(name="Current Revenue", x=["Current", "Simulated"], y=[user_revenue[-1], sim_revenue], marker_color='#3ECF8E'))
        chart.add_trace(go.Bar(name="Current Expenses", x=["Current", "Simulated"], y=[user_expenses[-1], sim_expenses], marker_color='#FFD166'))
        chart.update_layout(barmode="group", title="Current vs Simulated Revenue/Expenses")
        st.plotly_chart(chart, use_container_width=True)
        st.line_chart(pd.DataFrame({"Current": [user_revenue[-1], user_expenses[-1]], "Simulated": [sim_revenue, sim_expenses]}, index=["Revenue","Expenses"]))
        st.markdown(f"<details><summary>🔎 AI Analysis</summary>
            <div>Ad Spend at {ad_spend}% lifts expenses to ${sim_expenses:,.0f}. Price @${price} yields projected revenue ${sim_revenue:,.0f}. Higher churn reduces retention to {sim_customers}, but ROI remains strong at {roi:.1f}%. <br>
            <b>Strategic Suggestion:</b> Boosting ad spend <u>above</u> 110% only yields diminishing ROI unless price raised. Consider balancing churn reduction efforts with pricing strategy.</div></details>",unsafe_allow_html=True)

# --- Goal Tracking ---
if nav == "Goal Tracking":
    with st.expander("🏆 Goal Tracking", expanded=True):
        st.subheader("Monthly KPI Goals & Milestones")
        goal = 120000  # Demo goal for revenue
        achieved = user_revenue[-1]
        st.metric("Revenue Goal ($)", f"{goal:,.0f}", delta=f"{achieved-goal:+,}")
        percent = min(achieved/goal*100, 100)
        delta_days = max(0, int((goal - achieved)/2000)) # fake: $2k/day pace
        pred_date = (dates[-1] + timedelta(days=delta_days)).date()
        st.progress(percent/100, text=f"{percent:.1f}% of revenue goal")
        st.caption(f"Predicted achievement date: {pred_date}")
        st.markdown(f"<b>Milestone:</b> {'Goal MET!' if achieved>=goal else 'In Progress - keep momentum.'}")
        st.line_chart(pd.DataFrame({"Revenue":user_revenue,"Goal":[goal]*7},index=dates))

# --- AI Insights & Recommendations ---
if nav == "AI Insights & Recommendations":
    with st.expander("🧠 AI Insights & Recommendations", expanded=True):
        st.subheader("Strategic Guidance and Contextual Analytics")
        st.caption("Automated review of business health (sample data)")
        st.markdown("<ul><li><b>Revenue growth outpaces industry for recent periods.</b></li>
        <li>Retention is trending up—proactive churn management recommended.</li>
        <li>Pricing could be tested with lower churn segment.</li>
        <li>Ad spend allocation optimal at 100-105% range for best ROI.</li>
        <li>Historical patterns: Q1 weakest for expenses, Q3/Q4 surge in margin.</li></ul>",unsafe_allow_html=True)
        st.markdown('<details><summary>See improvement guides & past decisions</summary><ul><li>Read strategic pricing playbook (link)</li><li>Review Q2 retention initiative results (link)</li></ul></details>',unsafe_allow_html=True)

# --- Collaboration Notes ---
if nav == "Collaboration Notes":
    with st.expander("💬 Collaboration Notes", expanded=True):
        st.subheader("Comment Feed & Task Checklist")
        comment_feed = [
            {"text": "Finish Q2 retention deep-dive by Friday.", "urgent": True, "owner": "Alice", "due": "2025-11-08", "status": "In Progress"},
            {"text": "Review ad spend reallocation strategy.", "urgent": False, "owner": "Bob", "due": "2025-11-15", "status": "To Do"},
            {"text": "Present benchmarking results to board.", "urgent": True, "owner": "Dana", "due": "2025-11-09", "status": "In Progress"},
        ]
        for c in comment_feed:
            st.markdown(f"<div class='{'urgent' if c['urgent'] else ''}'>• {c['text']} <span class='owner'>[{c['owner']}]</span> <i>Status: {c['status']}, Due: {c['due']}</i></div>",unsafe_allow_html=True)
        st.markdown("---")
        # Task Checklist (fake)
        checklist = [
            {"task": "Upload October revenue data", "done": True},
            {"task": "Benchmark against top 3 competitors", "done": False},
            {"task": "Update board deck", "done": False},
        ]
        for t in checklist:
            st.checkbox(t["task"], t["done"])
        note = st.text_input("Add new urgent note:")
        if note:
            st.markdown(f"<div class='urgent'>New urgent note: {note}</div>",unsafe_allow_html=True)

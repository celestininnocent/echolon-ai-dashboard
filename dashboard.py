# Echolon AI Dashboard (Screenshot-Driven Redesign)
# Enhanced: All modules with visible, prominent interactive graphs (no expanders), dark UI, responsive layout
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Echolon AI Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- Custom Dark Theme Styling ---
st.markdown(
    """
    <style>
    body, .stApp {background-color: #181C24!important; color: #F3F6F9!important;}
    .st-emotion-cache-2trqyj {color: #3ECF8E!important;}
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-1p66bqe {background: #111217 !important;}
    header {background: none!important;}
    .urgent {color:red; font-weight: bold;}
    .owner {color:#3ECF8E!important;}
    .metric-card {background: #202634; border-radius: 16px; padding: 24px 8px; text-align: center; margin:8px; color:#F3F6F9}
    .kpiIcon {font-size:32px; margin-bottom:8px;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Demo/sample Data ----
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

# --- CSV Upload Top Bar ---
with st.container():
    up_col, prev_col = st.columns([.3,.7])
    with up_col:
        uploaded_file = st.file_uploader("📁 Upload CSV Data", type=["csv"])
    with prev_col:
        if uploaded_file:
            upload_df = pd.read_csv(uploaded_file)
            st.dataframe(upload_df, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

st.markdown("---")

# --- KPI Metric Cards Row ---
met1, met2, met3 = st.columns(3)
with met1:
    st.markdown('<div class="metric-card"><span class="kpiIcon">💰</span><br><b>Total Revenue</b><br>${:,.0f}</div>'.format(user_revenue[-1]),unsafe_allow_html=True)
with met2:
    st.markdown('<div class="metric-card"><span class="kpiIcon">💸</span><br><b>Total Expenses</b><br>${:,.0f}</div>'.format(user_expenses[-1]),unsafe_allow_html=True)
with met3:
    st.markdown('<div class="metric-card"><span class="kpiIcon">👥</span><br><b>Customers</b><br>{:,}</div>'.format(user_customers[-1]),unsafe_allow_html=True)

# --- Main Revenue/Expense Time-Series Chart ---
rexp_fig = go.Figure()
rexp_fig.add_trace(go.Scatter(x=df['Date'], y=df['Your Revenue'], mode='lines+markers', name='Your Revenue', line=dict(color='#3ECF8E', width=4)))
rexp_fig.add_trace(go.Scatter(x=df['Date'], y=df['Industry Revenue'], mode='lines+markers', name='Industry Revenue', line=dict(color='#6666FF', dash='dash', width=2)))
rexp_fig.add_trace(go.Scatter(x=df['Date'], y=df['Your Expenses'], mode='lines+markers', name='Your Expenses', line=dict(color='#E86A92', width=4)))
rexp_fig.add_trace(go.Scatter(x=df['Date'], y=df['Industry Expenses'], mode='lines+markers', name='Industry Expenses', line=dict(color='#FFD166', dash='dot', width=2)))
rexp_fig.update_layout(title='Revenue & Expenses Over Time', paper_bgcolor='#181C24',plot_bgcolor='#181C24',font_color='#F3F6F9',xaxis_title='Date',yaxis_title='Amount ($)',legend=dict(orientation='h'))
st.plotly_chart(rexp_fig, use_container_width=True)

# --- Industry Benchmarking Section (side-by-side) ---
bench_col, bar_col = st.columns((3,2))
with bench_col:
    cdf = df[["Date", "% Diff Revenue", "% Diff Expenses", "Revenue Rank"]].set_index("Date")
    st.markdown("**Industry Benchmarking (vs. Avg)**")
    st.dataframe(
        cdf.style.background_gradient(subset=["% Diff Revenue"], cmap="Greens")
                  .background_gradient(subset=["% Diff Expenses"], cmap="Reds")
                  .format({"% Diff Revenue":"{:+.1f}%", "% Diff Expenses":"{:+.1f}%"})
    )
with bar_col:
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(x=['Your Revenue','Industry Revenue','Your Expenses','Industry Expenses'],
        y=[user_revenue[-1], industry_avg_revenue[-1], user_expenses[-1], industry_avg_expenses[-1]],
        marker_color=['#3ECF8E','#6666FF','#E86A92','#FFD166']))
    bar_fig.update_layout(title='Latest Period Grouped Metrics',paper_bgcolor='#181C24',plot_bgcolor='#181C24',font_color='#F3F6F9',yaxis_title='Amount ($)')
    st.plotly_chart(bar_fig, use_container_width=True)

st.markdown("---")

# --- What If? Scenario Modeling ---
st.markdown("**🤔 What If? Scenario Modeling**")
wcol, chartcol = st.columns([1,2])
with wcol:
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
with chartcol:
    whatif = go.Figure()
    whatif.add_trace(go.Bar(name="Current Revenue", x=["Current", "Simulated"], y=[user_revenue[-1], sim_revenue], marker_color='#3ECF8E'))
    whatif.add_trace(go.Bar(name="Current Expenses", x=["Current", "Simulated"], y=[user_expenses[-1], sim_expenses], marker_color='#FFD166'))
    whatif.update_layout(barmode="group", title="Current vs Simulated Revenue/Expenses", paper_bgcolor='#181C24',plot_bgcolor='#181C24',font_color='#F3F6F9')
    st.plotly_chart(whatif, use_container_width=True)

st.markdown("---")

# --- Goal Tracking Module ---
st.markdown("**🏆 Goal Tracking**")
goalcolA, goalcolB = st.columns((2,1))
goal = 120000  # Demo goal for revenue
achieved = user_revenue[-1]
percent = min(achieved/goal*100, 100)
delta_days = max(0, int((goal - achieved)/2000))
pred_date = (dates[-1] + timedelta(days=delta_days)).date()
with goalcolA:
    st.markdown(f"### Revenue Goal Progress ")
    st.progress(percent/100, text=f"{percent:.1f}% of revenue goal")
    st.caption(f"Predicted achievement date: {pred_date}")
    st.line_chart(pd.DataFrame({"Revenue":user_revenue,"Goal":[goal]*7},index=dates))
with goalcolB:
    st.metric("Goal ($)", f"{goal:,.0f}", delta=f"{achieved-goal:+,}")
    st.markdown(f"**Milestone:** {'Goal MET!' if achieved>=goal else 'In Progress - keep momentum.'}")

st.markdown("---")

# --- AI Insights With Trend & Pattern Visualizations ---
st.markdown("**🧠 AI Insights & Recommendations**")
ins_col, pat_col = st.columns(2)
with ins_col:
    st.caption("Automated review of business health (sample data)")
    st.markdown("""
<ul>
<li>Revenue growth outpaces industry for recent periods.</li>
<li>Retention is trending up—proactive churn management recommended.</li>
<li>Pricing could be tested with lower churn segment.</li>
<li>Ad spend allocation optimal at 100–105% range for best ROI.</li>
<li>Historical patterns: Q1 weakest for expenses, Q3/Q4 surge in margin.</li>
</ul>""", unsafe_allow_html=True)
with pat_col:
    trend_fig = go.Figure()
    trend_fig.add_trace(go.Scatter(x=df['Date'], y=df['Customers'], mode='lines+markers', name='Customers',line=dict(color='#81F3CE',width=3)))
    trend_fig.add_trace(go.Bar(x=df['Date'], y=df['Your Revenue']-df['Your Expenses'], name='Margin', marker_color='#444CF7',opacity=0.2))
    trend_fig.update_layout(title='Customer/Retention Trends & Margin',paper_bgcolor='#181C24',plot_bgcolor='#181C24',font_color='#F3F6F9')
    st.plotly_chart(trend_fig,use_container_width=True)

st.markdown("---")

# --- Collaboration Notes Activity Feed & Checklist ---
st.markdown("**💬 Collaboration Notes & Activity**")
feed, checklist = st.columns((2, 1))
with feed:
    st.markdown("###### Activity Timeline")
    comment_feed = [
        {"text": "Finish Q2 retention deep-dive by Friday.", "urgent": True, "owner": "Alice", "due": "2025-11-08", "status": "In Progress"},
        {"text": "Review ad spend reallocation strategy.", "urgent": False, "owner": "Bob", "due": "2025-11-15", "status": "To Do"},
        {"text": "Present benchmarking results to board.", "urgent": True, "owner": "Dana", "due": "2025-11-09", "status": "In Progress"},
    ]
    for c in comment_feed:
        urgent = ' urgent' if c['urgent'] else ''
        st.markdown(f"<div class='{urgent}'><b>{c['text']}</b> [<span class='owner'>{c['owner']}</span>] Status: {c['status']}, Due: {c['due']}</div>",unsafe_allow_html=True)
with checklist:
    st.markdown("###### Task Checklist")
    tasks = [
        {"task": "Upload October revenue data", "done": True},
        {"task": "Benchmark against top 3 competitors", "done": False},
        {"task": "Update board deck", "done": False},
    ]
    for t in tasks:
        st.checkbox(t["task"], t["done"])
    note = st.text_input("Add new urgent note:")
    if note:
        st.markdown(f"<div class='urgent'>New urgent note: {note}</div>",unsafe_allow_html=True)

# --- Footer ---
st.caption('Demo prototype | All data is local/sample only | Redesigned UI 2025')

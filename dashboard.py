import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime

# ---- DARK THEME ----
st.set_page_config(page_title="Echolon AI Dashboard", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
        body, .stApp, .css-1d391kg, .css-14xtw13 {background-color: #181C24!important; color: #F3F6F9!important;}
        .st-emotion-cache-2trqyj {color: #3ECF8E!important;}
        .st-emotion-cache-1v0mbdj, .st-emotion-cache-1p66bqe {background: #111217  !important;}
        header {background: none!important;}
        .stTextInput > div > div > input, .stTextInput textarea {color: #fafcff!important; background-color: #232836!important;}
        .kpi-card {background: #111217 !important; border-radius: 14px; padding: 28px 16px; text-align: center; color: #F3F6F9; font-size: 1.8rem; box-shadow: 0 2px 14px #22242A;} 
        .kpi-label {color: #3ECF8E!important; font-size: 1.1rem;}
        .industry-table th {background-color: #232836!important; color: #3ECF8E!important;}
        .industry-table td {background-color: #191b21!important; color: #F3F6F9!important;}
    </style>
""", unsafe_allow_html=True)

# ---- SIDEBAR ----
with st.sidebar:
    st.title('🧊 Echolon AI')
    st.caption('AI-powered BI for businesses')
    st.markdown('---')
    st.markdown('**Upload CSVs to get started**')
    st.markdown('---')
    login_mock = st.button('Sign in (Mock)', help='Simulated login for stretch goal')
    if login_mock:
        st.success('Logged in (simulated)')
    st.markdown('---')
    st.caption('Session Notes (local only)')
    notes = st.text_area("Notes", "", height=100)

# ---- Executive Summary ----
st.markdown("# Executive Summary 💡")
st.markdown("""Responsive, modular dashboard for business intelligence. Upload your CSV to begin analysis.""")
st.markdown("---")

# ---- CSV Upload & Data Integration ----
uploaded_file = st.file_uploader("Upload Business CSV", type=["csv"], help="Sales, marketing, or customer data")
data_preview = None
col_map = {}
error_message = ""

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.subheader('📋 Data Preview')
        st.dataframe(df.head(15))
        data_preview = df
        st.info("Auto-detecting column types and integrating metrics.")
        st.markdown('---')

        # Attempt to auto-detect column types
        for col in df.columns:
            cl = col.lower()
            if 'date' in cl or 'time' in cl:
                col_map['date'] = col
            elif 'revenue' in cl or 'sales' in cl:
                col_map['revenue'] = col
            elif 'expenses' in cl or 'expense' in cl:
                col_map['expenses'] = col
            elif 'customers' in cl or 'customer' in cl:
                col_map['customers'] = col
            elif 'orders' in cl or 'order' in cl:
                col_map['orders'] = col
            elif 'churn' in cl:
                col_map['churn'] = col
            elif 'conversion' in cl:
                col_map['conversion'] = col
        st.write("**Auto-detected columns:**", col_map)
        st.markdown('---')
    except Exception as e:
        error_message = f"Error reading file: {str(e)}"
        st.error(error_message)
        st.stop()
else:
    st.warning('Upload a CSV file to continue.')

# ---- Assign Missing Columns UI Overlay ----
required_cols = ['revenue', 'expenses', 'customers']
missing_cols = [col for col in required_cols if col not in col_map]
if data_preview is not None and missing_cols:
    st.error(f"Missing columns: {', '.join(missing_cols)}. Please assign or upload data with these columns.")
    st.stop()

# ---- KPI Summary Cards ----
if data_preview is not None:
    st.markdown("## Key Metrics")
    kpi_cols = st.columns(3)
    rev = float(data_preview[col_map['revenue']].sum()) if 'revenue' in col_map else 0
    exp = float(data_preview[col_map['expenses']].sum()) if 'expenses' in col_map else 0
    cust = int(data_preview[col_map['customers']].nunique()) if 'customers' in col_map else 0
    kpi_defs = [
        ("Revenue", rev),
        ("Expenses", exp),
        ("Customers", cust)
    ]
    for idx, kpi in enumerate(kpi_defs):
        kpi_cols[idx].markdown(f"<div class='kpi-card'><span class='kpi-label'>{kpi[0]}</span><br>${kpi[1]:,.0f}</div>", unsafe_allow_html=True)
    st.markdown("---")

# ---- Large Plotly Time-Series Chart ----
    # Requires date column (can default to index)
    time_col = col_map['date'] if 'date' in col_map else df.index
    # Revenue and Expenses over time
    revenue_df = df[[col_map['date'], col_map['revenue']]] if 'date' in col_map and 'revenue' in col_map else None
    expenses_df = df[[col_map['date'], col_map['expenses']]] if 'date' in col_map and 'expenses' in col_map else None

    st.subheader("📈 Revenue & Expenses Over Time")
    if revenue_df is not None and expenses_df is not None:
        revenue_df = revenue_df.groupby(col_map['date'])[col_map['revenue']].sum().reset_index()
        expenses_df = expenses_df.groupby(col_map['date'])[col_map['expenses']].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=revenue_df[col_map['date']], y=revenue_df[col_map['revenue']], name='Revenue', line=dict(color='#3ECF8E', width=3)))
        fig.add_trace(go.Scatter(x=expenses_df[col_map['date']], y=expenses_df[col_map['expenses']], name='Expenses', line=dict(color='#FF4B4B', width=3)))
        fig.update_layout(template="plotly_dark", xaxis_title="Date", yaxis_title="Amount", legend_title="Metric")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info('Upload data with revenue, expenses, and date columns for time-series visualization.')
    st.markdown('---')

# ---- Industry Benchmarking Section ----
    with st.expander('🏅 Industry Benchmarking', expanded=True):
        st.subheader("Industry Comparison Table")
        benchmark_data = pd.DataFrame({
            'Company': ['Your Biz', 'Industry Avg', 'Top Quartile'],
            'Revenue': [rev, rev*0.90, rev*1.18],
            'Expenses': [exp, exp*0.95, exp*0.80],
            'Customers': [cust, cust*0.85, cust*1.22]
        })
        st.markdown(benchmark_data.style.set_table_attributes('class="industry-table"').format({
            'Revenue': '{:,.0f}', 'Expenses': '{:,.0f}', 'Customers': '{:,.0f}'
        }).hide(axis='index').to_html(), unsafe_allow_html=True)
        st.markdown('---')
        st.subheader("Industry KPI Bar Chart")
        figb = go.Figure()
        for met in ['Revenue', 'Expenses', 'Customers']:
            figb.add_trace(go.Bar(
                x=benchmark_data['Company'], y=benchmark_data[met], name=met,
                marker_color={'Revenue':'#3ECF8E', 'Expenses':'#FF4B4B', 'Customers':'#2196f3'}[met]
            ))
        figb.update_layout(barmode='group', template="plotly_dark", title="Industry KPI Benchmark", xaxis_title="Company", yaxis_title="Value", legend_title="Metric")
        st.plotly_chart(figb, use_container_width=True)
        st.markdown('---')

# ---- Scenario Modeling ----
    with st.expander('🤔 Scenario Modeling', expanded=False):
        st.subheader('Run Simulations')
        st.write('Adjust Ad Spend, Price, and Churn to see projections.')
        ad_spend_pct = st.slider('Ad Spend % Change', -50, 100, 0, step=5, help="Range: -50% to +100%")
        price_pct = st.slider('Avg. Price % Change', -20, 40, 0, step=2, help="Range: -20% to +40%")
        churn_pct = st.slider('Churn Rate % Change', -50, 30, 0, step=5, help="Range: -50% to +30%")
        ad_spend_base = 10000
        churn_rate_base = 0.05
        sim_rev = rev * (1 + price_pct/100) * (1 - ((churn_rate_base + churn_pct/100)))
        sim_exp = exp * (1 + ad_spend_pct/100)
        sim_cust = cust * (1 - (churn_rate_base + churn_pct/100))
        current_metrics = {'Revenue': rev, 'Expenses': exp, 'Customers': cust}
        simulated_metrics = {
            'Revenue': sim_rev,
            'Expenses': sim_exp,
            'Customers': sim_cust
        }
        result_df = pd.DataFrame({
            'Metric': list(current_metrics.keys()),
            'Current': list(current_metrics.values()),
            'Simulated': [simulated_metrics[k] for k in current_metrics.keys()]
        })
        st.dataframe(result_df.set_index('Metric'), use_container_width=True)
        figsm = go.Figure()
        for metric in ['Revenue', 'Expenses', 'Customers']:
            figsm.add_trace(go.Bar(
                x=['Current', 'Simulated'], y=[current_metrics.get(metric,0), simulated_metrics.get(metric,0)], name=metric,
                marker_color=['#3ECF8E', '#FF4B4B'] if metric=='Revenue' else ['#2196f3', '#2196f3']
            ))
        figsm.update_layout(barmode='group', title='Scenario Metrics', template="plotly_dark", xaxis_title='Period', yaxis_title='Value', legend_title='Metric')
        st.plotly_chart(figsm, use_container_width=True)
        st.info(f"Revenue {'up' if sim_rev>=rev else 'down'} {((sim_rev-rev)/rev*100):,.1f}%. Customers adjusted for churn changes.")
        st.markdown('---')

# ---- Modular, Collapsible Expanders ----
    with st.expander('🎯 Goal Tracking', expanded=False):
        st.subheader('Monthly Goal Progress')
        revenue_target = st.number_input('Monthly Revenue Target', min_value=10000, value=rev if rev > 0 else 80000)
        cust_target = st.number_input('Customer Target', min_value=10, value=cust if cust > 0 else 1800)
        st.progress(min(rev/revenue_target, 1.0), f'Revenue Progress: {rev:,.0f}/{revenue_target:,.0f}')
        st.progress(min(cust/cust_target, 1.0), f'Customers Progress: {cust:,.0f}/{cust_target:,.0f}')
        st.info('AI Suggestion: Reallocate 10–15% ad spend from underperforming channels for better goal attainment.')
        st.markdown('---')

    with st.expander('🤖 AI Insights', expanded=False):
        st.subheader('Analysis & Suggestions')
        st.info('Customer retention issues, ad budget prioritization, and mock insights. Real AI integration coming.')
        st.markdown('---')

    with st.expander('📝 Collaboration & Notes', expanded=False):
        st.subheader('Session Notes (see sidebar for entry)')
        st.info('Cloud notes and dashboard history in future updates.')
        st.markdown('---')

    with st.expander('🗂️ Dashboard History & AI Summaries (Stretch)', expanded=False):
        st.write('Simulated dashboard history and mock AI-generated summaries will be added in future milestones.')
        st.markdown('---')

st.caption('Echolon AI Dashboard [Prototype v0.2] — All data is local and sample-only.')

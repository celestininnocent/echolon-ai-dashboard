import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime
import io

# ---- DARK THEME ----
st.set_page_config(page_title="Echolon AI Dashboard", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
        body, .stApp, .css-1d391kg, .css-14xtw13 {background-color: #181C24!important; color: #F3F6F9!important;}
        .st-emotion-cache-2trqyj {color: #3ECF8E!important;}
        .st-emotion-cache-1v0mbdj, .st-emotion-cache-1p66bqe {background: #111217  !important;}
        header {background: none!important;}
        .stTextInput > div > div > input, .stTextInput textarea {color: #fafcff!important; background-color: #232836!important;}
        .stDataFrame {background-color: #191b21!important;}
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

# ---- Main Dashboard Layout ----
st.header('Echolon AI Dashboard')
st.markdown('Responsive, modular dashboard for business intelligence.')
st.markdown('---')

# 1. CSV Upload & Data Integration
uploaded_file = st.file_uploader("Upload Business CSV", type=["csv"], help="Sales, marketing, or customer data")
data_preview = None
col_map = {}
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader('📋 Data Preview')
    st.dataframe(df.head(15))
    data_preview = df
    st.info("Auto-detecting column types and integrating metrics.")
    st.markdown('---')
    # Attempt to auto-detect column types
    lower_cols = [col.lower() for col in df.columns]
    for col in df.columns:
        cl = col.lower()
        if 'date' in cl or 'time' in cl:
            col_map['date'] = col
        elif 'revenue' in cl or 'sales' in cl:
            col_map['revenue'] = col
        elif 'orders' in cl or 'order' in cl:
            col_map['orders'] = col
        elif 'churn' in cl:
            col_map['churn'] = col
        elif 'conversion' in cl:
            col_map['conversion'] = col
    st.write("**Auto-detected columns:**", col_map)
    st.markdown('---')

# 2. Industry Benchmarking
with st.expander('🏆 Industry Benchmarking', expanded=False):
    st.subheader('Benchmark Your Metrics Against Industry Leaders')
    st.write('Compare revenue, orders, churn and more versus sample benchmarks.')
    # Sample industry benchmarks
    benchmark_data = {
        'Revenue': 100000,
        'Orders': 2000,
        'Churn Rate': 0.05,
    }
    if data_preview is not None and col_map:
        values = {}
        # Grab metrics from detected columns
        if 'revenue' in col_map:
            values['Revenue'] = data_preview[col_map['revenue']].sum()
        if 'orders' in col_map:
            values['Orders'] = data_preview[col_map['orders']].sum()
        if 'churn' in col_map:
            values['Churn Rate'] = data_preview[col_map['churn']].mean() if not data_preview[col_map['churn']].isnull().all() else None
        st.markdown("### Metrics Compared to Benchmark:")
        for metric, bench_val in benchmark_data.items():
            val = values.get(metric, None)
            if val is not None:
                pct = (val - bench_val)/bench_val * 100
                colour = 'red' if pct < 0 else 'green'
                st.markdown(f"<span style='color:{colour}'>**{metric}: {val:,.0f} ({pct:+.1f}% vs benchmark {bench_val:,.0f})**</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color:orange'>**{metric}: Not available in your data**</span>", unsafe_allow_html=True)
        st.markdown('---')
    else:
        st.info('Upload business data to enable benchmarking.')

# 3. What If? Scenario Modeling
with st.expander('🤔 Scenario Modeling', expanded=False):
    st.subheader('Run Simulations')
    st.write('Project impact by adjusting Ad Spend, Price, Churn.')
    ad_spend_pct = st.slider('Ad Spend % Change', -50, 50, 0, step=5)
    price_pct = st.slider('Avg. Price % Change', -20, 20, 0, step=2)
    churn_pct = st.slider('Churn Rate % Change', -50, 50, 0, step=5)
    if data_preview is not None and col_map:
        # Simulate results
        revenue = data_preview[col_map['revenue']].sum() if 'revenue' in col_map else 0
        orders = data_preview[col_map['orders']].sum() if 'orders' in col_map else 0
        base_churn = data_preview[col_map['churn']].mean() if 'churn' in col_map else 0.05
        proj_revenue = revenue * (1 + price_pct/100) * (1 - ((base_churn + churn_pct/100)))
        proj_profit = proj_revenue * (1 + ad_spend_pct/200) # increase from ad
        # Show plot
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Current', 'Projected'],
            y=[revenue, proj_profit],
            marker_color=['#3ECF8E','#F3F6F9']
        ))
        fig.update_layout(title="Projected Revenue/Profit", template="plotly_dark")
        st.plotly_chart(fig)
    else:
        st.info('Upload valid data for scenario projections.')
    st.markdown('---')

# 4. Goal Tracking
with st.expander('🎯 Goal Tracking', expanded=False):
    st.subheader('Monthly Goal Progress')
    revenue_target = st.number_input('Monthly Revenue Target', min_value=10000, value=80000)
    conv_target = st.number_input('Conversion Rate Target', min_value=0.0, max_value=1.0, value=0.08, format="%.2f")
    orders_target = st.number_input('Orders Target', min_value=10, value=1800)
    if data_preview is not None and col_map:
        actual_revenue = data_preview[col_map['revenue']].sum() if 'revenue' in col_map else 0
        actual_orders = data_preview[col_map['orders']].sum() if 'orders' in col_map else 0
        actual_conv = data_preview[col_map['conversion']].mean() if 'conversion' in col_map else 0
        # Progress bars
        st.progress(min(actual_revenue/revenue_target, 1.0), f'Revenue Progress: {actual_revenue:,.0f}/{revenue_target:,.0f}')
        st.progress(min(actual_orders/orders_target, 1.0), f'Orders Progress: {actual_orders:,.0f}/{orders_target:,.0f}')
        st.progress(min(actual_conv/conv_target, 1.0), f'Conversion Rate Progress: {actual_conv:.2%}/{conv_target:.2%}')
        # AI Suggestions for recovery
        st.info('AI Suggestion: Reallocate 10–15% ad spend from underperforming channels for better goal attainment.')
    else:
        st.info('Goals tracking available when valid business data is uploaded.')
    st.markdown('---')

# 5. AI Insights & Recommendations
with st.expander('🤖 AI Insights', expanded=False):
    st.subheader('Analysis & Suggestions')
    st.info('Customer retention last quarter dropped due to inconsistent purchase frequency.\nAd budget should prioritize high-LTV segments.\nMock insights only. Real AI integration coming.')
    st.markdown('---')

# 6. Collaboration/Notes
with st.expander('📝 Collaboration & Notes', expanded=False):
    st.subheader('Session Notes')
    st.write('Use the sidebar to add and read session notes. These are stored only locally for now.')
    st.info('Cloud notes and dashboard history in future updates.')
    st.markdown('---')

# --- Stretch Goals: Dashboard History / AI Summaries ---
with st.expander('🗂️ Dashboard History & AI Summaries (Stretch)', expanded=False):
    st.write('Simulated dashboard history and mock AI-generated summaries will be added here in future milestones.')
st.markdown('---')
st.caption('Echolon AI Dashboard [Prototype v0.1] — All data is local and sample-only.')

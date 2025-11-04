import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime
import io

# ---- DARK THEME ----
st.set_page_config(page_title="Echolon AI Dashboard", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <br>        body, .stApp, .css-1d391kg, .css-14xtw13 {background-color: #181C24!important; color: #F3F6F9!important;}<br>        .st-emotion-cache-2trqyj {color: #3ECF8E!important;}<br>        .st-emotion-cache-1v0mbdj, .st-emotion-cache-1p66bqe {background: #111217  !important;}<br>        header {background: none!important;}<br>        .stTextInput > div > div > input, .stTextInput textarea {color: #fafcff!important; background-color: #232836!important;}<br>        .stDataFrame {background-color: #191b21!important;}<br>    <br>""", unsafe_allow_html=True)

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

# ---- UPGRADED SCENARIO MODELING ----
with st.expander('🤔 Scenario Modeling', expanded=True):
    st.subheader('Run Simulations')
    st.write('Project impact by adjusting Ad Spend, Price, Churn.')
    # Sliders w/better ranges and labels
    def slider_component(label, minimum, maximum, default, step, available, disabled_msg):
        if available:
            return st.slider(f'{label} (%)', min_value=minimum, max_value=maximum, value=default, step=step, help=f"Range: {minimum}% to {maximum}%")
        else:
            st.slider(f'{label} (%)', min_value=minimum, max_value=maximum, value=default, step=step, disabled=True, help=disabled_msg)
            return default
    has_revenue = 'revenue' in col_map
    has_orders = 'orders' in col_map
    has_churn = 'churn' in col_map
    ad_spend_pct = slider_component('Ad Spend % Change', -50, 100, 0, 5, True, '')
    price_pct = slider_component('Avg. Price % Change', -20, 40, 0, 2, has_revenue, 'Upload business data for price impact projections.')
    churn_pct = slider_component('Churn Rate % Change', -50, 30, 0, 5, has_churn, 'Churn rate not found. Upload CSV with churn data.')

    # Prepare all metrics
    current_metrics = {}
    simulated_metrics = {}
    if data_preview is not None and col_map:
        current_metrics['Revenue'] = data_preview[col_map['revenue']].sum() if has_revenue else 0
        current_metrics['Orders'] = data_preview[col_map['orders']].sum() if has_orders else 0
        current_metrics['Churn Rate'] = data_preview[col_map['churn']].mean() if has_churn else 0.05
        n_customers = len(data_preview) if has_orders else 0
        ad_spend_base = 10000  # Mock: assume from business context or add as CSV column future
        current_metrics['Ad Spend'] = ad_spend_base
        current_metrics['Customers'] = n_customers
        # Projected calculation
        sim_rev = current_metrics['Revenue'] * (1 + price_pct/100) * (1 - ((current_metrics['Churn Rate'] + churn_pct/100)))
        sim_orders = current_metrics['Orders'] * (1 + price_pct/100) * (1 - ((current_metrics['Churn Rate'] + churn_pct/100)))
        sim_churn = current_metrics['Churn Rate'] + churn_pct/100
        sim_ad_spend = ad_spend_base * (1 + ad_spend_pct/100)
        sim_customers = n_customers * (1 - sim_churn)
        simulated_metrics['Revenue'] = sim_rev
        simulated_metrics['Orders'] = sim_orders
        simulated_metrics['Churn Rate'] = sim_churn
        simulated_metrics['Ad Spend'] = sim_ad_spend
        simulated_metrics['Customers'] = sim_customers

        # Live summary panel
        change_rev_pct = ((sim_rev-current_metrics['Revenue'])/current_metrics['Revenue']*100) if current_metrics['Revenue'] else 0
        st.info(f"Simulated: Revenue {'up' if change_rev_pct>=0 else 'down'} {change_rev_pct:,.1f}% at {ad_spend_pct:+.0f}% ad spend & {price_pct:+.0f}% price, churn {'flat' if churn_pct==0 else f'{sim_churn:,.2%}'}; see graphs below.")
        st.markdown('---')
        # Scenario result chart: Current vs Simulated, both bar + line
        st.markdown('#### Scenario Comparison: Current vs Simulated')
        summary_df = pd.DataFrame({
            'Metric': list(current_metrics.keys()),
            'Current': list(current_metrics.values()),
            'Simulated': [simulated_metrics[k] for k in current_metrics.keys()]
        })
        st.dataframe(summary_df.set_index('Metric'), use_container_width=True)

        # Main bar/line chart, group metrics
        main_fig = go.Figure()
        for metric in ['Revenue', 'Orders', 'Ad Spend', 'Customers', 'Churn Rate']:
            main_fig.add_trace(go.Bar(
                x=['Current', 'Simulated'], y=[current_metrics.get(metric,0), simulated_metrics.get(metric,0)], name=metric, text=[f'{current_metrics.get(metric,0):,.0f}', f'{simulated_metrics.get(metric,0):,.0f}'], textposition='auto'))
        main_fig.update_layout(barmode='group', title='Scenario Metrics: Current vs Simulated', template="plotly_dark", xaxis_title='Period', yaxis_title='Value', legend_title='Metric')
        st.plotly_chart(main_fig, use_container_width=True)
        # Small multiples / modular charts
        st.markdown('---')
        st.markdown('#### Small Multiples: Key Projections')
        cols = st.columns(4)
        col_metrics = ['Revenue', 'Ad Spend', 'Churn Rate', 'Customers']
        for i, met in enumerate(col_metrics):
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=['Current', 'Simulated'], y=[current_metrics.get(met, 0), simulated_metrics.get(met, 0)], marker_color=['#2bba74', '#f3f6f9']
            ))
            fig.add_trace(go.Scatter(
                x=['Current', 'Simulated'], y=[current_metrics.get(met, 0), simulated_metrics.get(met, 0)], marker_color='#3ECF8E', name='Line'
            ))
            fig.update_layout(title=f'{met}', template="plotly_dark", xaxis_title='Period', yaxis_title=met,
                              legend=dict(font=dict(color='white')), hovermode='x')
            cols[i].plotly_chart(fig, use_container_width=True)
        st.markdown('---')
    else:
        st.warning("Upload CSVs with Revenue, Orders, Churn columns to use all simulation controls & unlock live multiples.")
        st.markdown('---')
    # End Scenario Modeling

# 4. Goal Tracking (unchanged)
with st.expander('🎯 Goal Tracking', expanded=False):
    st.subheader('Monthly Goal Progress')
    revenue_target = st.number_input('Monthly Revenue Target', min_value=10000, value=80000)
    conv_target = st.number_input('Conversion Rate Target', min_value=0.0, max_value=1.0, value=0.08, format="%.2f")
    orders_target = st.number_input('Orders Target', min_value=10, value=1800)
    if data_preview is not None and col_map:
        actual_revenue = data_preview[col_map['revenue']].sum() if 'revenue' in col_map else 0
        actual_orders = data_preview[col_map['orders']].sum() if 'orders' in col_map else 0
        actual_conv = data_preview[col_map['conversion']].mean() if 'conversion' in col_map else 0
        st.progress(min(actual_revenue/revenue_target, 1.0), f'Revenue Progress: {actual_revenue:,.0f}/{revenue_target:,.0f}')
        st.progress(min(actual_orders/orders_target, 1.0), f'Orders Progress: {actual_orders:,.0f}/{orders_target:,.0f}')
        st.progress(min(actual_conv/conv_target, 1.0), f'Conversion Rate Progress: {actual_conv:.2%}/{conv_target:.2%}')
        st.info('AI Suggestion: Reallocate 10–15% ad spend from underperforming channels for better goal attainment.')
    else:
        st.info('Goals tracking available when valid business data is uploaded.')
    st.markdown('---')

# 5. AI Insights & Recommendations (unchanged)
with st.expander('🤖 AI Insights', expanded=False):
    st.subheader('Analysis & Suggestions')
    st.info('Customer retention last quarter dropped due to inconsistent purchase frequency.\nAd budget should prioritize high-LTV segments.\nMock insights only. Real AI integration coming.')
    st.markdown('---')

# 6. Collaboration/Notes (unchanged)
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

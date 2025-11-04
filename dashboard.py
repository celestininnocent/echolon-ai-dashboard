import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(page_title="Echolon AI Dashboard", layout="wide", page_icon="🤖", initial_sidebar_state="expanded")

# Apply a dark theme using custom CSS
st.markdown('''
    <style>
        body, .stApp { background: #22252A !important; color: #EEE !important; }
        .block-container { padding-top: 1.5rem; }
        .css-18e3th9 { background: #181A1B !important; }
        .css-1d391kg, .css-1v3fvcr { color: #EEE !important; }
        .st-bf { background: #282C34 !important; }
    </style>
''', unsafe_allow_html=True)

# Sample data generation functions
@st.cache_data
def generate_sample_data():
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    data = pd.DataFrame({
        'Date': dates,
        'Revenue': np.random.uniform(10000, 50000, len(dates)).cumsum() / 100,
        'Expenses': np.random.uniform(5000, 20000, len(dates)).cumsum() / 100,
        'Customers': np.random.randint(50, 500, len(dates)),
        'Churn_Rate': np.random.uniform(0.1, 5, len(dates)),
        'Ad_Spend': np.random.uniform(1000, 10000, len(dates)),
    })
    return data

@st.cache_data
def generate_benchmark_data():
    return pd.DataFrame({
        'Metric': ['Revenue Growth', 'Profit Margin', 'Customer Retention', 'ROI', 'Cost per Acquisition'],
        'Your Company': [15.2, 22.5, 87.3, 320, 45.2],
        'Industry Average': [12.0, 20.0, 85.0, 300, 50.0],
        'Industry Top 10%': [25.0, 35.0, 95.0, 500, 30.0]
    })

# Sidebar layout
with st.sidebar:
    st.title("Echolon AI 🧩")
    st.markdown("**AI-powered BI for small & midsize businesses**")
    st.divider()
    st.markdown("*Start by uploading your data or browse dashboard modules.*")
    st.markdown("---")
    st.subheader("Dashboard Controls")
    selected_month = st.selectbox("Select Month", range(1, 13), format_func=lambda x: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][x-1])

# Top Title
st.title("Echolon AI Business Analytics Dashboard")
st.markdown("> Modular, AI-driven dashboard for data-backed decisions.")

# Load sample data
df = generate_sample_data()
benchmark_df = generate_benchmark_data()

with st.expander("📤 Upload & Data Integration", expanded=True):
    st.info("Upload CSV or connect via API. Auto-detects columns for preview.")
    col1, col2 = st.columns(2)
    with col1:
        st.button("Upload CSV")
    with col2:
        st.button("Connect to API")
    
    st.subheader("Data Preview")
    st.dataframe(df.head(10), use_container_width=True)
    st.metric("Total Records", len(df))

with st.expander("📈 Industry Benchmarking", expanded=True):
    st.info("Compare metrics to industry benchmarks. See % difference and color-coded results.")
    
    # Create benchmark comparison chart
    fig = px.bar(benchmark_df, x='Metric', y=['Your Company', 'Industry Average', 'Industry Top 10%'],
                 barmode='group', title='Metrics vs Industry Benchmarks',
                 labels={'value': 'Value', 'variable': 'Benchmark'},
                 color_discrete_map={'Your Company': '#00D9FF', 'Industry Average': '#FFB700', 'Industry Top 10%': '#00FF88'})
    fig.update_layout(
        plot_bgcolor='#1E1E1E',
        paper_bgcolor='#22252A',
        font=dict(color='#EEE'),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Display benchmark table
    st.subheader("Detailed Comparison")
    st.dataframe(benchmark_df, use_container_width=True)

with st.expander("🔮 'What If?' Scenario Modeling", expanded=True):
    st.info("Adjust variables, simulate revenue/profit, and see results in a chart.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        ad_spend_change = st.slider("Ad Spend % Change", -50, 50, 0, key="ad_spend")
    with col2:
        price_change = st.slider("Price % Change", -25, 25, 0, key="price")
    with col3:
        churn_change = st.slider("Churn Rate Change", -10, 10, 0, key="churn")
    
    # Simulate scenario
    df_scenario = df.copy()
    df_scenario['Revenue'] = df_scenario['Revenue'] * (1 + price_change/100) * (1 + ad_spend_change/100)
    df_scenario['Customers'] = df_scenario['Customers'] * (1 - churn_change/100)
    
    # Create scenario chart
    fig_scenario = go.Figure()
    fig_scenario.add_trace(go.Scatter(x=df['Date'], y=df['Revenue'], mode='lines', name='Current Revenue', line=dict(color='#00D9FF', width=2)))
    fig_scenario.add_trace(go.Scatter(x=df_scenario['Date'], y=df_scenario['Revenue'], mode='lines', name='Projected Revenue', line=dict(color='#00FF88', width=2)))
    fig_scenario.update_layout(
        title='Revenue Projection - Scenario Analysis',
        xaxis_title='Date',
        yaxis_title='Revenue ($)',
        plot_bgcolor='#1E1E1E',
        paper_bgcolor='#22252A',
        font=dict(color='#EEE'),
        height=400
    )
    st.plotly_chart(fig_scenario, use_container_width=True)
    
    # Show key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        revenue_delta = (df_scenario['Revenue'].sum() - df['Revenue'].sum()) / df['Revenue'].sum() * 100
        st.metric("Revenue Change", f"{revenue_delta:.1f}%")
    with col2:
        customer_delta = (df_scenario['Customers'].sum() - df['Customers'].sum()) / df['Customers'].sum() * 100
        st.metric("Customer Count Change", f"{customer_delta:.1f}%")
    with col3:
        st.metric("Scenario Applied", "✓ Active")

with st.expander("🎯 Goal Tracking", expanded=True):
    st.info("Set targets, track progress, and get AI suggestions for recovery.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Revenue Goal")
        revenue_target = st.number_input("Target Revenue ($)", value=1000000, step=10000)
        current_revenue = df['Revenue'].sum()
        progress = min(current_revenue / revenue_target, 1.0)
        st.progress(progress)
        st.text(f"${current_revenue:,.0f} / ${revenue_target:,.0f}")
    
    with col2:
        st.subheader("Customer Goal")
        customer_target = st.number_input("Target Customers", value=10000, step=100)
        current_customers = df['Customers'].sum()
        progress = min(current_customers / customer_target, 1.0)
        st.progress(progress)
        st.text(f"{current_customers:,.0f} / {customer_target:,.0f}")
    
    st.markdown("**AI Suggestions:**")
    st.markdown(
        "- Reallocate 10-15% budget from underperforming channels\n"
        "- Increase customer retention initiatives (currently at 92%)\n"
        "- Focus on high-value customer segments\n"
        "- Optimize pricing strategy for Q4"
    )

with st.expander("🧠 AI Insights & Recommendations", expanded=True):
    st.info("AI-generated insights based on your data.")
    
    # Create insights visualizations
    channels = ['Email', 'Social Media', 'Paid Search', 'Organic', 'Direct']
    roi_values = [450, 320, 280, 150, 520]
    fig_insights = px.bar(x=channels, y=roi_values, title='ROI by Marketing Channel',
                         labels={'x': 'Channel', 'y': 'ROI (%)'}, color=roi_values,
                         color_continuous_scale=['#FF6B6B', '#FFB700', '#00FF88'])
    fig_insights.update_layout(
        plot_bgcolor='#1E1E1E',
        paper_bgcolor='#22252A',
        font=dict(color='#EEE'),
        height=350,
        showlegend=False
    )
    st.plotly_chart(fig_insights, use_container_width=True)
    
    st.markdown(
        "- **Top Insight:** Customer retention dropped 3% due to inconsistent purchase frequency\n"
        "- **Recommendation:** Launch re-engagement campaign targeting inactive customers\n"
        "- **Opportunity:** Your ad spend ROI is strongest on Mondays — reallocate budget accordingly\n"
        "- **Alert:** Churn rate increased by 2% in the last 30 days"
    )

with st.expander("💬 Collaboration", expanded=True):
    st.info("Simple notes for team communication.")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        note = st.text_area("Add Note", "", height=80, placeholder="Enter team notes or observations here...")
    with col2:
        st.button("Save Note")
    
    st.markdown("**Recent Notes:**")
    st.info("🗒️ Q4 budget allocation meeting scheduled for next week")
    st.info("🗒️ New product launch expected to boost retention by 5%")

# Additional visualization section - SIMPLIFIED VERSION
with st.expander("📊 Additional Analytics", expanded=False):
    st.subheader("Revenue Trends")
    fig_revenue = px.line(df, x='Date', y='Revenue', title='Daily Revenue Over Time',
                         labels={'Revenue': 'Revenue ($)', 'Date': 'Date'})
    fig_revenue.update_layout(
        plot_bgcolor='#1E1E1E',
        paper_bgcolor='#22252A',
        font=dict(color='#EEE'),
        height=350
    )
    fig_revenue.update_traces(line_color='#00D9FF', line_width=2)
    st.plotly_chart(fig_revenue, use_container_width=True)
    
    st.subheader("Customer Growth")
    fig_customers = px.line(df, x='Date', y='Customers', title='Daily Customer Count',
                           labels={'Customers': 'Number of Customers', 'Date': 'Date'})
    fig_customers.update_layout(
        plot_bgcolor='#1E1E1E',
        paper_bgcolor='#22252A',
        font=dict(color='#EEE'),
        height=350
    )
    fig_customers.update_traces(line_color='#FFB700', line_width=2)
    st.plotly_chart(fig_customers, use_container_width=True)
    
    st.subheader("Churn Rate Analysis")
    fig_churn = px.area(df, x='Date', y='Churn_Rate', title='Monthly Churn Rate Trend',
                       labels={'Churn_Rate': 'Churn Rate (%)', 'Date': 'Date'})
    fig_churn.update_layout(
        plot_bgcolor='#1E1E1E',
        paper_bgcolor='#22252A',
        font=dict(color='#EEE'),
        height=350
    )
    st.plotly_chart(fig_churn, use_container_width=True)

# Stretch Goals placeholder
with st.expander("🚀 Stretch Goals (Not Yet Implemented)"):
    st.write("- Auto-generate AI summaries\n- Basic user login\n- Session history storage")

st.markdown("---")
st.markdown("_Echolon AI Dashboard - Powered by Streamlit with AI-driven insights for modern businesses_")

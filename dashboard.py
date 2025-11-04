import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(page_title="Echolon AI Dashboard", layout="wide", page_icon="🤖", initial_sidebar_state="expanded")
st.markdown('''    <br>body, .stApp { background: #22252A !important; color: #EEE !important; }    <br>.block-container { padding-top: 1.5rem; }    <br>.css-18e3th9 { background: #181A1B !important; }    <br>.css-1d391kg, .css-1v3fvcr { color: #EEE !important; }    <br>.st-bf { background: #282C34 !important; }
''', unsafe_allow_html=True)

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

def validate_columns(df, required):
    missing = [c for c in required if c not in df.columns]
    return len(missing) == 0, missing

# Sidebar
with st.sidebar:
    st.title("Echolon AI 🧩")
    st.markdown("**AI-powered BI for small & midsize businesses**")
    st.divider()
    st.markdown("*Start by uploading your data or browse dashboard modules.*")
    st.markdown("---")
    st.subheader("Dashboard Controls")
    selected_month = st.selectbox("Select Month", list(range(1, 13)), format_func=lambda x: ['January','February','March','April','May','June','July','August','September','October','November','December'][x-1])
    st.markdown("---")
    st.markdown("**[Stretch] Mock Login Placeholder**")
    st.text_input("Username", value="demo_user")
    st.text_input("Password", value="********", type="password")
    st.button("Login (Mock)")
    st.markdown("---")
    st.markdown("**[Stretch] Session Store/History Placeholder**")
    st.write("Session history will appear here.")

# Upload section
col1, col2 = st.columns([2, 1])
df_uploaded = None
df_sample = generate_sample_data()
required_cols = ['Date','Revenue','Expenses','Customers','Churn_Rate','Ad_Spend']
with col1:
    st.subheader("Upload business CSV data")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        try:
            df_uploaded = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Error reading file: {e}")
            df_uploaded = None
has_all, missing = validate_columns(df_uploaded if df_uploaded is not None else df_sample, required_cols)
if has_all and df_uploaded is not None:
    df = df_uploaded
    using_sample_data = False
    st.info("All required columns found. Full dashboard enabled!")
else:
    df = df_sample.copy()
    if df_uploaded is not None:
        for col in df_uploaded.columns:
            if col in df.columns:
                df[col].iloc[:len(df_uploaded)] = df_uploaded[col].values
        using_sample_data = 'partial'
        missing_columns_alerts = missing
    else:
        using_sample_data = True
        missing_columns_alerts = required_cols

with col2:
    st.subheader("Preview")
    st.dataframe(df.head(10), use_container_width=True)

if using_sample_data is True:
    st.info("ℹ️ Dashboard uses sample/demo data (upload CSV for real business metrics).")
elif using_sample_data == 'partial':
    st.warning(f"⚠️ Dashboard in hybrid mode. Sample data used for: {', '.join(missing_columns_alerts)}.")
else:
    st.success("✅ Full dashboard active with your uploaded data.")
st.markdown("---")

# DASHBOARD MODULES
with st.expander("📈 Industry Benchmarking", expanded=True):
    st.markdown("Compare business KPIs against industry/premium benchmarks.")
    benchmark_df = generate_benchmark_data()
    st.dataframe(benchmark_df, use_container_width=True)
    fig_bench = go.Figure()
    for col in ['Your Company', 'Industry Average', 'Industry Top 10%']:
        fig_bench.add_trace(go.Bar(x=benchmark_df['Metric'], y=benchmark_df[col], name=col))
    fig_bench.update_layout(barmode='group', title="Industry Benchmark Chart", template='plotly_dark')
    st.plotly_chart(fig_bench, use_container_width=True)

with st.expander("💹 Revenue Trend", expanded=True):
    if all([c in df.columns for c in ['Date','Revenue']]):
        fig_rev = px.line(df, x='Date', y='Revenue', title="Revenue Trend", template='plotly_dark')
        st.plotly_chart(fig_rev, use_container_width=True)
    else:
        st.warning("Revenue Trend chart requires 'Date' and 'Revenue' columns.")

with st.expander("🎯 Goal Tracking", expanded=True):
    st.markdown("Set monthly targets and track your progress towards goals.")
    revenue_target = st.number_input("Set Revenue Target", min_value=1000, max_value=1000000, value=50000, step=1000)
    current_revenue = df['Revenue'].iloc[-1] if 'Revenue' in df.columns else 0
    progress = min(current_revenue / revenue_target, 1) if revenue_target > 0 else 0
    st.progress(progress, text=f'{int(progress*100)}% towards goal')
    if progress < 1:
        st.caption("Consider increasing your ad spend or reducing churn rate to meet targets.")
    else:
        st.success("Goal achieved!")

with st.expander("🧮 ROI by Channel", expanded=True):
    if all([c in df.columns for c in ['Ad_Spend','Revenue']]):
        # For demo, mock separate channels, split Ad_Spend
        channels = ['Google', 'Meta', 'LinkedIn']
        n = len(df)
        ad_spend_split = np.array_split(df['Ad_Spend'].values, 3)
        roi_channels = [np.sum(s)/np.sum(df['Revenue'].values) for s in ad_spend_split]
        fig_roi = go.Figure([go.Bar(x=channels, y=roi_channels)])
        fig_roi.update_layout(title="ROI by Channel", template='plotly_dark', yaxis_title="ROI Ratio")
        st.plotly_chart(fig_roi, use_container_width=True)
    else:
        st.warning("ROI by Channel chart requires 'Ad_Spend' and 'Revenue' columns.")

with st.expander("🔮 Scenario Modeling", expanded=True):
    st.markdown("Use sliders to simulate changes in ad spend, price, churn, etc. Plots update below.")
    if all([c in df.columns for c in ['Date','Ad_Spend','Revenue','Churn_Rate']]):
        ad_spend_adj = st.slider("Ad Spend Adjustment", min_value=0.5, max_value=2.0, value=1.0, step=0.05)
        churn_adj = st.slider("Churn Rate Adjustment", min_value=0.5, max_value=2.0, value=1.0, step=0.05)
        scenario_revenue = df['Revenue'] * ad_spend_adj * (2-churn_adj)
        fig_proj = px.line(x=df['Date'], y=scenario_revenue, title=f"Scenario Revenue Projection (Ad Spend x{ad_spend_adj}, Churn x{churn_adj})", template='plotly_dark')
        st.plotly_chart(fig_proj, use_container_width=True)
    else:
        st.warning("Scenario modeling requires 'Date', 'Ad_Spend', 'Revenue', and 'Churn_Rate' columns.")

with st.expander("✅ Goal Progress", expanded=True):
    if 'Revenue' in df.columns:
        monthly = df.groupby(df['Date'].dt.month)['Revenue'].sum() if 'Date' in df.columns else df['Revenue']
        fig_goal = px.bar(x=monthly.index, y=monthly.values, labels={'x': 'Month', 'y':'Revenue'}, title="Goal Progress by Month", template='plotly_dark')
        st.plotly_chart(fig_goal, use_container_width=True)
    else:
        st.info("Goal progress chart requires 'Revenue' column.")

with st.expander("🧠 AI Insights & Recommendations", expanded=True):
    st.markdown("Example actionable insights and recommendations for SMB growth.")
    st.write("- Improve customer retention by 5% to increase lifetime value.", unsafe_allow_html=True)
    st.write("- Allocate additional $2000 to Ad Spend for projected 8% increase in revenue.", unsafe_allow_html=True)
    st.write("[Static/mock suggestions - Logic will be added in next steps]")

with st.expander("💬 Collaboration & Notes", expanded=True):
    st.markdown("Leave notes, comments and share feedback internally.")
    note = st.text_area("Team Notes", "")
    st.caption("[Placeholder: Notes stored locally/session only]")

st.markdown("---")
st.caption("Echolon AI Dashboard | Demo structure & robust data handling ready.")

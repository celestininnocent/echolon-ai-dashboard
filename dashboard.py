import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# --- Sample Data Generator ---
@st.cache_data
def generate_sample_data():
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    data = pd.DataFrame({
        'Date': dates,
        'Revenue': np.random.uniform(10000, 50000, len(dates)).cumsum() / 100,
        'Expenses': np.random.uniform(5000, 20000, len(dates)).cumsum() / 100,
        'Customers': np.random.randint(50, 500, len(dates)),
        'Churn_Rate': np.random.uniform(0.1, 5, len(dates)),
        'Ad_Spend': np.random.uniform(1000, 10000, len(dates))
    })
    return data

if 'data_sources' not in st.session_state:
    st.session_state['data_sources'] = []

# --- Sidebar ---
with st.sidebar:
    st.title("Echolon AI 🧩")
    st.markdown("**AI-powered BI for small & midsize businesses**")
    st.divider()
    st.markdown("*Start by uploading your data or browse dashboard modules.*")
    st.markdown("---")
    st.subheader("Dashboard Controls")
    selected_month = st.selectbox(
        "Select Month",
        list(range(1, 13)),
        format_func=lambda x: [
            'January','February','March','April','May','June',
            'July','August','September','October','November','December'][(x-1)]
    )
    st.markdown("---")
    st.markdown("**[Stretch] Mock Login Placeholder**")
    st.text_input("Username", value="demo_user")
    st.text_input("Password", value="********", type="password")
    st.button("Login (Mock)")
    st.markdown("---")
    st.markdown("**[Stretch] Session Store/History Placeholder**")
    st.write("Session history will appear here.")
    st.markdown("---")

# --- Multi-source selection ---
def get_main_df():
    # Use first mapped data source, else sample
    for ds in st.session_state['data_sources']:
        if ds.get('df_mapped') is not None:
            return ds['df_mapped']
    return generate_sample_data()

df = get_main_df()

# --- Metrics ---
classic_metrics = ['Date','Revenue','Expenses','Customers','Churn_Rate','Ad_Spend']
missing_metrics = [m for m in classic_metrics if m not in df.columns]

if missing_metrics:
    st.warning(f"Missing columns: {', '.join(missing_metrics)}. Showing sample/demo data.")

# --- 1. Revenue Trend (Line Chart) ---
if 'Date' in df.columns and 'Revenue' in df.columns:
    st.subheader("Revenue Trend")
    fig = px.line(df, x='Date', y='Revenue', title="Revenue Over Time")
    st.plotly_chart(fig, use_container_width=True)

# --- 2. Industry Benchmarking (Bar Chart) ---
if 'Revenue' in df.columns and 'Expenses' in df.columns:
    st.subheader("Industry Benchmarking")
    benchmarks = pd.DataFrame({
        'Category': ['Your Revenue', 'Benchmark Revenue', 'Your Expenses', 'Benchmark Expenses'],
        'Value': [df['Revenue'].mean(), 35000, df['Expenses'].mean(), 12000]
    })
    fig = px.bar(benchmarks, x='Category', y='Value', color='Category', title="Benchmark Comparison")
    st.plotly_chart(fig, use_container_width=True)

# --- 3. Goal Progress Bar ---
goal_revenue = 1200000
actual_revenue = df['Revenue'].sum() if 'Revenue' in df.columns else 0
if goal_revenue and actual_revenue:
    st.subheader("Goal Progress")
    progress = min(1.0, actual_revenue/goal_revenue)
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = actual_revenue,
        number = {"prefix": "$", "valueformat": ",.0f"},
        gauge = {
            "axis": {"range": [None, goal_revenue]},
            "bar": {"color": "green"},
            "steps": [
                {"range": [0, goal_revenue*0.5], "color": "lightgray"},
                {"range": [goal_revenue*0.5, goal_revenue], "color": "gray"},
            ],
            "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": goal_revenue}
        },
        title = {"text": "Revenue Goal Progress"}
    ))
    st.plotly_chart(fig, use_container_width=True)
    st.metric("Progress", f"{progress*100:.1f}% achieved")

# --- 4. ROI by Channel chart (Pie Chart Example) ---
if 'Ad_Spend' in df.columns and 'Revenue' in df.columns:
    st.subheader("ROI by Channel")
    channels = ['Search', 'Social', 'Direct', 'Referral']
    channel_spend = np.random.dirichlet(np.ones(len(channels)), 1)[0] * df['Ad_Spend'].sum()
    channel_revenue = np.random.dirichlet(np.ones(len(channels)), 1)[0] * df['Revenue'].sum()
    roi = channel_revenue / (channel_spend + 1e-6)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=channels,
        y=roi,
        marker_color=["royalblue","purple","orange","green"],
        name="ROI"
    ))
    fig.update_layout(title="ROI by Marketing Channel", xaxis_title="Channel", yaxis_title="ROI (Revenue/Ad Spent)")
    st.plotly_chart(fig, use_container_width=True)

# --- 5. Scenario Modeling (Interactive Slider) ---
if 'Customers' in df.columns and 'Revenue' in df.columns:
    st.subheader("Scenario Modeling: Revenue Impact of Customer Change")
    base_customers = df['Customers'].mean()
    base_revenue = df['Revenue'].mean()
    factor = st.slider("Change in Customers (%)", min_value=-50, max_value=100, value=0, step=5)
    modeled_customers = base_customers * (1 + factor/100)
    modeled_revenue = base_revenue * (modeled_customers/base_customers)
    fig = go.Figure([
        go.Bar(name="Base", x=["Customers","Revenue"], y=[base_customers, base_revenue]),
        go.Bar(name="Scenario", x=["Customers","Revenue"], y=[modeled_customers, modeled_revenue])
    ])
    fig.update_layout(barmode='group', title="Scenario Modeling")
    st.plotly_chart(fig, use_container_width=True)
    st.metric("Modeled Revenue", f"${modeled_revenue:,.0f}")

# --- Data Source/Column Mapping Management ---
st.markdown("---")
st.subheader("Upload & Column Mapping")
if st.session_state['data_sources']:
    for idx, ds in enumerate(st.session_state['data_sources']):
        st.markdown(f"### [{idx+1}] {ds['name']}")
        columns = ds['df'].columns.tolist()
        st.write("**Column Mapping**: Choose columns for each metric.")
        if 'column_map' not in ds:
            ds['column_map'] = {}
        for metric in classic_metrics:
            map_key = f"colmap_{ds['name']}_{metric}_{idx}"
            choice = st.selectbox(
                f"Map column for {metric} in {ds['name']}",
                ['(None)'] + columns,
                index=(columns.index(metric)+1 if metric in columns else 0),
                key=map_key
            )
            ds['column_map'][metric] = choice if choice != '(None)' else None
        # Remap columns for future use
        ds['df_mapped'] = ds['df'].rename(
            columns={v:k for k,v in ds['column_map'].items() if v}
        )
else:
    st.info("No data sources registered yet. Upload/connect to begin analysis.")

st.markdown("---\nEcholon AI Dashboard v2 – All classic modules restored.")

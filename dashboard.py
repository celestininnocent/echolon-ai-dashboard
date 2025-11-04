import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(page_title="Echolon AI Dashboard", layout="wide", page_icon="🤖", initial_sidebar_state="expanded")

st.markdown(
    '''<style>
    body, .stApp { background: #22252A !important; color: #EEE !important; }
    .block-container { padding-top: 1.5rem; }
    .css-18e3th9 { background: #181A1B !important; }
    .css-1d391kg, .css-1v3fvcr { color: #EEE !important; }
    .st-bf { background: #282C34 !important; }
    </style>''', unsafe_allow_html=True)

# Sample and demo data
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

# Sidebar (including stretch placeholders)
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

# Top Area: AI Summary (placeholder)
st.markdown("### 🤖 AI Summary\n> [Mock] High-level business summary and trends will appear here.")
st.markdown("---")

# UPLOAD SECTION
st.markdown("#### 📤 Upload & Data Integration")
df_sample = generate_sample_data()
df = df_sample.copy()
using_sample_data = True
missing_columns_alerts = []

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload your business CSV", type=["csv"])
    if uploaded_file:
        try:
            df_uploaded = pd.read_csv(uploaded_file)
            st.success(f"CSV uploaded: {len(df_uploaded)} rows.")
            # Detect required columns for all modules
            required_cols = ['Date','Revenue','Expenses','Customers','Churn_Rate','Ad_Spend']
            has_all, missing = validate_columns(df_uploaded, required_cols)
            if has_all:
                df = df_uploaded
                using_sample_data = False
                st.info("All required columns found. Full dashboard enabled!")
            else:
                st.warning(f"Missing columns: {', '.join(missing)}. Sections with missing columns will fallback to demo/sample data.")
                df = df_sample.copy()
                # Overwrite present columns from uploaded data
                for col in df_uploaded.columns:
                    if col in df.columns:
                        df[col].iloc[:len(df_uploaded)] = df_uploaded[col].values
                using_sample_data = 'partial'
                missing_columns_alerts = missing
        except Exception as e:
            st.error(f"Upload/read error: {e}. Using sample/demo data.")
            using_sample_data = True
with col2:
    st.subheader("Preview")
    st.dataframe(df.head(10), use_container_width=True)

# Alert/banner for upload status
if using_sample_data == True:
    st.info("ℹ️ Dashboard uses sample/demo data (upload CSV for real business metrics).")
elif using_sample_data == 'partial':
    st.warning(f"⚠️ Dashboard in hybrid mode. Sample data used for: {', '.join(missing_columns_alerts)}.")
else:
    st.success("✅ Full dashboard active with your uploaded data.")
st.markdown("---")

# DASHBOARD MODULES - EXPANDABLE<br>
with st.expander("📈 Industry Benchmarking", expanded=True):
    st.markdown("Compare business KPIs against industry/premium benchmarks.")
    benchmark_df = generate_benchmark_data()
    st.dataframe(benchmark_df, use_container_width=True)
    st.caption("[Placeholder] KPI % difference (colored) will show here.")

with st.expander("🎯 Goal Tracking", expanded=True):
    st.markdown("Set monthly targets and track your progress towards goals.")
    st.number_input("Set Revenue Target", min_value=1000, max_value=1000000, value=50000, step=1000)
    st.progress(0.5, text="[50% Sample Progress]")
    st.caption("[Placeholder] Suggestions for goal recovery will be shown here.")

with st.expander("🤔 'What If?' Scenario Modeling", expanded=True):
    st.markdown("Use sliders to simulate changes in ad spend, price, churn, etc. Plots update below.")
    st.slider("Ad Spend", min_value=1000, max_value=10000, value=5000)
    st.slider("Churn Rate", min_value=0.0, max_value=5.0, value=1.0, step=0.1)
    st.caption("[Placeholder] Interactive plot will go here.")

with st.expander("🧠 AI Insights & Recommendations", expanded=True):
    st.markdown("Example actionable insights and recommendations for SMB growth.")
    st.write("- Improve customer retention by <b>5%</b> to increase lifetime value.", unsafe_allow_html=True)
    st.write("- Allocate additional <b>$2000</b> to Ad Spend for projected 8% increase in revenue.", unsafe_allow_html=True)
    st.write("[Static/mock suggestions - Logic will be added in next steps]")

with st.expander("💬 Collaboration & Notes", expanded=True):
    st.markdown("Leave notes, comments and share feedback internally.")
    note = st.text_area("Team Notes", "")
    st.caption("[Placeholder: Notes stored locally/session only]")

st.markdown("---")
st.caption("Echolon AI Dashboard | Demo structure & robust data handling ready.")

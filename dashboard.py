import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime, timedelta
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(
    page_title="Echolon AI Dashboard",
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="expanded"
)
st.markdown('''
    body, .stApp { background: #22252A !important; color: #EEE !important; }
    .block-container { padding-top: 1.5rem; }
    .css-18e3th9 { background: #181A1B !important; }
    .css-1d391kg, .css-1v3fvcr { color: #EEE !important; }
    .st-bf { background: #282C34 !important; }
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

if 'data_sources' not in st.session_state:
    st.session_state['data_sources'] = [] # Each item: {'name': str, 'df': pd.DataFrame, 'column_map': dict, 'anomaly_flags': dict}

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
            'July','August','September','October','November','December'][x-1]
    )
    st.markdown("---")
    st.markdown("**[Stretch] Mock Login Placeholder**")
    st.text_input("Username", value="demo_user")
    st.text_input("Password", value="********", type="password")
    st.button("Login (Mock)")
    st.markdown("---")
    st.markdown("**[Stretch] Session Store/History Placeholder**")
    st.write("Session history will appear here.")

# --- Data Source Connectors ---
st.write("# Add Data Source")
conn_type = st.selectbox("Select Connector Type", ["CSV Upload", "Google Sheets", "API Connector"], key="connect_type")

if conn_type == "CSV Upload":
    uploaded_file = st.file_uploader("Upload new CSV Data Source", type=["csv"], key="new_csv")
    ds_name = st.text_input("Optional: Name this dataset", key='ds_name_csv')
    if uploaded_file is not None:
        df_new = pd.read_csv(uploaded_file)
        name = ds_name.strip() or uploaded_file.name
        st.success(f"Source added: {name}")
        st.dataframe(df_new.head(10))
        st.session_state['data_sources'].append({
            'name': name,
            'df': df_new,
            'column_map': {},
            'anomaly_flags': {}
        })

elif conn_type == "Google Sheets":
    sheet_url = st.text_input("Google Sheets URL", key="gs_url")
    ds_name = st.text_input("Optional: Name this dataset", key='ds_name_gs')
    if sheet_url:
        try:
            import gspread
            from gspread_dataframe import get_as_dataframe
            gc = gspread.service_account() # Assumes credentials file present
            sh = gc.open_by_url(sheet_url)
            worksheet = sh.get_worksheet(0)
            df_new = get_as_dataframe(worksheet)
            name = ds_name.strip() or "GoogleSheet"
            st.success(f"Source added: {name}")
            st.dataframe(df_new.head(10))
            st.session_state['data_sources'].append({
                'name': name,
                'df': df_new,
                'column_map': {},
                'anomaly_flags': {}
            })
        except Exception as e:
            st.error(f"Could not load Google Sheet: {e}")

elif conn_type == "API Connector":
    api_key = st.text_input("API Key", type="password", key="api_key")
    endpoint = st.text_input("API Endpoint URL", key="api_url")
    custom_headers = st.text_area("Additional Headers (JSON)", key="api_headers")
    ds_name = st.text_input("Optional: Name this dataset", key='ds_name_api')
    if endpoint and api_key:
        try:
            headers = {'Authorization': f'Bearer {api_key}'}
            if custom_headers:
                import json
                headers.update(json.loads(custom_headers))
            resp = requests.get(endpoint, headers=headers)
            if resp.status_code == 200:
                # Assume the result is CSV data for now
                from io import StringIO
                df_new = pd.read_csv(StringIO(resp.text))
                name = ds_name.strip() or "API_Data"
                st.success(f"Source added: {name}")
                st.dataframe(df_new.head(10))
                st.session_state['data_sources'].append({
                    'name': name,
                    'df': df_new,
                    'column_map': {},
                    'anomaly_flags': {}
                })
            else:
                st.error(f"API Error: {resp.status_code} {resp.text}")
        except Exception as e:
            st.error(f"API load failed: {e}")

# --- Data Source Listing & Validation ---
if st.session_state['data_sources']:
    st.write("## Registered Data Sources")
    for idx, ds in enumerate(st.session_state['data_sources']):
        st.markdown(f"### [{idx+1}] {ds['name']}")
        columns = ds['df'].columns.tolist()
        # --- Column Mapping UI ---
        st.write("**Column Mapping**: Choose columns for each metric.")
        metrics = ['Date','Revenue','Expenses','Customers','Churn_Rate','Ad_Spend']
        for metric in metrics:
            map_key = f"colmap_{ds['name']}_{metric}_{idx}"
            choice = st.selectbox(
                f"Map column for {metric} in {ds['name']}",
                ['(None)'] + columns,
                index=(columns.index(metric) + 1 if metric in columns else 0),
                key=map_key
            )
            ds['column_map'][metric] = choice if choice != '(None)' else None
        # --- Remap columns for future use ---
        df_mapped = ds['df'].rename(columns={v: k for k, v in ds['column_map'].items() if v})
        # --- Summary Statistics ---
        st.write("**Summary Statistics for Numeric Columns**")
        num_cols = df_mapped.select_dtypes(include=[np.number]).columns
        stats = df_mapped[num_cols].describe().T[['mean','std','min','max']]
        stats['missing_values'] = df_mapped[num_cols].isna().sum()
        st.dataframe(stats)
        # --- Data Anomalies Detection ---
        st.write("**Data Anomaly Warnings**")
        anomalies = {}
        # 1. Missing Date Range
        date_col = ds['column_map'].get('Date')
        if date_col:
            dates = pd.to_datetime(ds['df'][date_col], errors='coerce')
            missing_dates = dates.isna().sum()
            full_range = (dates.max() - dates.min()).days + 1 if len(dates) > 0 else 0
            if missing_dates > 0:
                anomalies['missing_dates'] = f"{missing_dates} rows have invalid/missing dates."
            if len(set(dates)) != full_range:
                anomalies['missing_range'] = f"Date range has missing days ({full_range-len(set(dates))} missing)."
        # 2. All Zeros/Nulls for columns
        for c in num_cols:
            if (ds['df'][c] == 0).all():
                anomalies[f'all_zero_{c}'] = f"Column '{c}' contains only zeros."
            if ds['df'][c].isna().all():
                anomalies[f'all_null_{c}'] = f"Column '{c}' contains only nulls."
        # 3. Outlier Detection (simple z-score >3)
        for c in num_cols:
            zscore = np.abs((ds['df'][c] - ds['df'][c].mean()) / (ds['df'][c].std() + 1e-9))
            outliers = (zscore > 3).sum()
            if outliers > 0:
                anomalies[f'outliers_{c}'] = f"Column '{c}' has {outliers} high-value outlier{'s' if outliers > 1 else ''}."
        ds['anomaly_flags'] = anomalies
        if anomalies:
            for key, msg in anomalies.items():
                st.warning(msg)
        else:
            st.success("No major anomalies detected in this dataset.")
        # --- Critical Columns Check ---
        missing_metrics = [m for m in metrics if not ds['column_map'].get(m)]
        if missing_metrics:
            st.error(f"Missing critical columns: {', '.join(missing_metrics)}")
        ds['df_mapped'] = df_mapped
else:
    st.info("No data sources registered yet. Upload/connect to begin analysis.")
# The rest of the dashboard's modules should reference: st.session_state['data_sources'][i]['df_mapped'],
# supporting multi-source aggregation and analysis as needed. Chart upgrades paused unless requested.

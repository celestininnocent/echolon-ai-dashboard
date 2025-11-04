# Echolon AI Dashboard (Screenshot-Driven Redesign)
# Enhanced: Flexible CSV upload - works with any column structure
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

default_df = pd.DataFrame({
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

# --- CSV Upload Top Bar with Flexible Column Handling ---
st.markdown("## 📊 Data Upload & Preview")

with st.container():
    up_col, info_col = st.columns([.3,.7])
    with up_col:
        uploaded_file = st.file_uploader("📁 Upload CSV Data (any structure)", type=["csv"])
    
    # Initialize working dataframe
    if uploaded_file:
        try:
            upload_df = pd.read_csv(uploaded_file)
            working_df = upload_df.copy()
            st.success(f"✅ CSV loaded successfully! {len(working_df)} rows, {len(working_df.columns)} columns.")
        except Exception as e:
            st.error(f"❌ Error loading CSV: {e}")
            working_df = default_df.copy()
    else:
        working_df = default_df.copy()
        st.info("Using demo data. Upload your own CSV to analyze custom data.")

# Display dataframe preview
st.markdown("### Data Preview")
st.dataframe(working_df, use_container_width=True)

# Show column information
st.markdown("### Available Columns")
col_info = st.columns(3)
with col_info[0]:
    st.write(f"**Total Columns:** {len(working_df.columns)}")
with col_info[1]:
    numeric_cols = working_df.select_dtypes(include=[np.number]).columns.tolist()
    st.write(f"**Numeric Columns:** {len(numeric_cols)}")
with col_info[2]:
    date_cols = working_df.select_dtypes(include=['datetime64', 'object']).columns.tolist()
    st.write(f"**Text/Date Columns:** {len(date_cols)}")

st.markdown("---")

# Check if we have numeric data to work with
if len(numeric_cols) == 0:
    st.error("⚠️ No numeric columns found in the data. Please upload a CSV with numeric data for analysis.")
    st.stop()

# --- Dynamic Column Selection for Visualizations ---
st.markdown("## 🎯 Interactive Data Analysis")

with st.expander("⚙️ Configure Chart Columns", expanded=True):
    sel_col1, sel_col2, sel_col3 = st.columns(3)
    
    with sel_col1:
        # Select columns for KPI metrics
        kpi_cols = st.multiselect(
            "Select columns for KPI cards (up to 3)",
            options=numeric_cols,
            default=numeric_cols[:3] if len(numeric_cols) >= 3 else numeric_cols,
            max_selections=3
        )
    
    with sel_col2:
        # Select columns for time series
        chart_cols = st.multiselect(
            "Select columns for time-series chart",
            options=numeric_cols,
            default=numeric_cols[:4] if len(numeric_cols) >= 4 else numeric_cols
        )
    
    with sel_col3:
        # Select date/index column
        potential_date_cols = ['Date'] + [col for col in working_df.columns if 'date' in col.lower() or 'time' in col.lower()]
        date_col = st.selectbox(
            "Select date/time column (optional)",
            options=[None] + working_df.columns.tolist(),
            index=0 if 'Date' not in working_df.columns else working_df.columns.tolist().index('Date') + 1
        )

st.markdown("---")

# --- KPI Metric Cards Row (Dynamic) ---
if kpi_cols:
    st.markdown("### 📊 Key Metrics")
    kpi_columns = st.columns(len(kpi_cols))
    
    for idx, col_name in enumerate(kpi_cols):
        with kpi_columns[idx]:
            latest_value = working_df[col_name].iloc[-1] if len(working_df) > 0 else 0
            # Calculate change if possible
            if len(working_df) > 1:
                prev_value = working_df[col_name].iloc[-2]
                delta = latest_value - prev_value
                st.metric(label=col_name, value=f"{latest_value:,.2f}", delta=f"{delta:,.2f}")
            else:
                st.metric(label=col_name, value=f"{latest_value:,.2f}")

st.markdown("---")

# --- Main Time-Series Chart (Dynamic) ---
if chart_cols:
    st.markdown("### 📈 Time-Series Visualization")
    
    # Prepare x-axis
    if date_col and date_col in working_df.columns:
        try:
            x_axis = pd.to_datetime(working_df[date_col])
        except:
            x_axis = working_df.index
    else:
        x_axis = working_df.index
    
    # Create figure
    chart_fig = go.Figure()
    colors = ['#3ECF8E', '#6666FF', '#E86A92', '#FFD166', '#81F3CE', '#444CF7']
    
    for idx, col_name in enumerate(chart_cols):
        color = colors[idx % len(colors)]
        chart_fig.add_trace(
            go.Scatter(
                x=x_axis, 
                y=working_df[col_name], 
                mode='lines+markers', 
                name=col_name, 
                line=dict(color=color, width=3)
            )
        )
    
    chart_fig.update_layout(
        title='Multi-Column Time Series',
        paper_bgcolor='#181C24',
        plot_bgcolor='#181C24',
        font_color='#F3F6F9',
        xaxis_title='Index' if not date_col else date_col,
        yaxis_title='Value',
        legend=dict(orientation='h'),
        height=500
    )
    st.plotly_chart(chart_fig, use_container_width=True)

st.markdown("---")

# --- Statistical Summary ---
st.markdown("### 📊 Statistical Summary")
if numeric_cols:
    summary_df = working_df[numeric_cols].describe().T
    summary_df['range'] = summary_df['max'] - summary_df['min']
    st.dataframe(summary_df, use_container_width=True)

st.markdown("---")

# --- Correlation Heatmap (if multiple numeric columns) ---
if len(numeric_cols) > 1:
    st.markdown("### 🔥 Correlation Heatmap")
    corr_matrix = working_df[numeric_cols].corr()
    
    heatmap_fig = go.Figure(
        data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        )
    )
    
    heatmap_fig.update_layout(
        title='Column Correlation Matrix',
        paper_bgcolor='#181C24',
        plot_bgcolor='#181C24',
        font_color='#F3F6F9',
        height=500
    )
    st.plotly_chart(heatmap_fig, use_container_width=True)

st.markdown("---")

# --- Comparison Bar Chart ---
if numeric_cols:
    st.markdown("### 📊 Latest Values Comparison")
    
    # Get latest values for all numeric columns
    latest_values = [working_df[col].iloc[-1] if len(working_df) > 0 else 0 for col in numeric_cols]
    
    bar_fig = go.Figure()
    bar_fig.add_trace(
        go.Bar(
            x=numeric_cols,
            y=latest_values,
            marker_color=['#3ECF8E', '#6666FF', '#E86A92', '#FFD166', '#81F3CE', '#444CF7'][:len(numeric_cols)]
        )
    )
    
    bar_fig.update_layout(
        title='Latest Period - All Numeric Columns',
        paper_bgcolor='#181C24',
        plot_bgcolor='#181C24',
        font_color='#F3F6F9',
        yaxis_title='Value',
        height=400
    )
    st.plotly_chart(bar_fig, use_container_width=True)

st.markdown("---")

# --- Data Export ---
st.markdown("### 💾 Export Options")
export_col1, export_col2 = st.columns(2)

with export_col1:
    if st.button("📥 Download Processed Data as CSV"):
        csv = working_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="processed_data.csv",
            mime="text/csv"
        )

with export_col2:
    st.write(f"**Current Dataset:** {len(working_df)} rows × {len(working_df.columns)} columns")

st.markdown("---")

# --- Footer ---
st.caption('✨ Flexible Dashboard | Supports any CSV structure | Updated 2025')
st.caption('Upload your CSV with any columns - the dashboard will automatically adapt!')

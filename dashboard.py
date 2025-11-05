# Echolon AI Dashboard (Screenshot-Driven Redesign)
# Enhanced: Flexible CSV upload - works with any column structure
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime, timedelta
st.set_page_config(page_title="Echolon AI Dashboard", layout="wide", initial_sidebar_state="expanded")
# --- 📋 Echolon vs Visa Analytics/Business Dashboards: How We’re Different ---
st.markdown(
    """
    ### 🆚 **Echolon AI Dashboard vs. Visa's Analytics Dashboards**
    
    **Echolon AI Dashboard brings unique value for startups & SMBs:**
    - **Data Flexibility:** Handles any CSV, any columns—no locked data models.
    - **Customization:** Choose your metrics, upload your data, personalize the workflow.
    - **AI-Powered Insights:** AI tips (not just static charts) guide your decisions.
    - **Startup/SMB Focus:** Built for lean teams, not just enterprise giants—understand & grow fast.
    - **Open Platform:** No vendor lock-in—use it your way.
    - **Gamification:** Engaging charts, metrics, and feedback make analysis fun, not tiring.
    - **Low Cost:** No premium licensing fees—accessible innovation for all.
    
    """,
    unsafe_allow_html=True
)
# --- Custom Dark Theme Styling ---
st.markdown(
    """
    body, .stApp {background-color: #181C24!important; color: #F3F6F9!important;}
    .st-emotion-cache-2trqyj {color: #3ECF8E!important;}
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-1p66bqe {background: #111217 !important;}
    header {background: none!important;}
    .urgent {color:red; font-weight: bold;}
    .owner {color:#3ECF8E!important;}
    .metric-card {background: #202634; border-radius: 16px; padding: 24px 8px; text-align: center; margin:8px; color:#F3F6F9}
    .kpiIcon {font-size:32px; margin-bottom:8px;}
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
# --- NEW: Column Selection Section ---
st.markdown("### 🛠️ Select Columns for Analysis")
columns_selected = st.multiselect(
    "Select data columns to view and analyze:", working_df.columns.tolist(), default=working_df.columns.tolist()
)
filtered_df = working_df[columns_selected]
st.dataframe(filtered_df, use_container_width=True)
# --- NEW: AI-Powered Insights Section ---
def ai_insights(df):
    insights = []
    if 'Your Revenue' in df.columns and 'Industry Revenue' in df.columns:
        rev_gap = df['Your Revenue'].mean() - df['Industry Revenue'].mean()
        if rev_gap > 0:
            insights.append("Your revenue consistently exceeds industry average! Keep leveraging your current growth strategies.")
        else:
            insights.append("Industry average revenue is higher. Consider reviewing pricing or marketing strategies.")
    if 'Customers' in df.columns:
        if df['Customers'].mean() > 4000:
            insights.append("Customer acquisition is strong. Time to focus on retention!")
        else:
            insights.append("Explore new lead generation strategies for customer growth.")
    if not insights:
        insights.append("Upload more data for actionable insights.")
    return insights
st.markdown("### 🤖 AI-Powered Insights & Recommendations")
for tip in ai_insights(filtered_df):
    st.info(tip)
# --- NEW: Interactive Charting & Gamification ---
st.markdown("### 📈 Interactive Charts & Gamification")
if len(numeric_cols) >= 2:
    st.plotly_chart(
        go.Figure([
            go.Bar(
                x=filtered_df['Date'] if 'Date' in filtered_df.columns else filtered_df.index,
                y=filtered_df[numeric_cols[0]],
                name=numeric_cols[0]
            ),
            go.Bar(
                x=filtered_df['Date'] if 'Date' in filtered_df.columns else filtered_df.index,
                y=filtered_df[numeric_cols[1]],
                name=numeric_cols[1]
            )
        ]),
        use_container_width=True
    )
    achievement = None
    if 'Revenue Rank' in filtered_df.columns and filtered_df['Revenue Rank'].min() == 1:
        achievement = "🏆 Top Industry Performer!"
    if achievement:
        st.success(f"**Achievement: {achievement}**")
    completion_ratio = min(100, int(len(filtered_df)/10*100))  # Gamified metric
    st.progress(completion_ratio, text=f"Data Analysis Progress: {completion_ratio}%")
else:
    st.warning("Not enough numeric columns for charting/gamification.")
# --- NEW: No-Cost Section ---
st.markdown("### 🎁 100% No-Cost Platform")
st.info("Echolon AI Dashboard is completely free: No licensing fees, no premium paywalls. Built for startups and SMBs.")

# Echolon AI Dashboard (Screenshot-Driven Redesign)
# Major dashboard upgrade: dynamic AI insights, richer gamification, feedback, improved UX
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Echolon AI Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- <span style='font-size:1.3em'>📋 Echolon vs Visa Analytics/Business Dashboards</span>: How We’re Different ---
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

# ----------- DEMO/sample Data ------------
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

# --------- Onboarding / help popup for first time users ----------
if 'help_shown' not in st.session_state:
    st.session_state['help_shown'] = False

def show_onboarding():
    st.markdown("""
    ### 👋 Welcome to Echolon AI Dashboard!
    - 📁 <b>Upload your CSV</b> (any columns) at the top left<br>
    - 🧠 <b>See AI insights</b> and outlier detection for your data<br>
    - 🏅 <b>Earn achievements & see your progress</b> below charts<br>
    - 💬 <b>Rate your session</b> for feedback/tips at the end
    """, unsafe_allow_html=True)
    st.info("You can always click the ❓ icon (top-right) for help.")

with st.sidebar:
    st.markdown("<span style='font-size:1.4em'>❓ Help</span>", unsafe_allow_html=True)
    if st.button("Show onboarding / help") or not st.session_state['help_shown']:
        show_onboarding()
        st.session_state['help_shown'] = True

# ---------- 📊 Data Upload & Preview ----------
st.markdown("## 📁 <span style='font-size:1.3em'>Data Upload & Preview</span>", unsafe_allow_html=True)
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

# --------- Data Preview & Columns -----------
st.markdown("### 👀 <span style='font-size:1.2em'>Data Preview</span>", unsafe_allow_html=True)
st.dataframe(working_df, use_container_width=True)
st.markdown("### 📋 Available Columns", unsafe_allow_html=True)
col_info = st.columns(3)
with col_info[0]:
    st.write(f"**Total Columns:** {len(working_df.columns)}")
with col_info[1]:
    numeric_cols = working_df.select_dtypes(include=[np.number]).columns.tolist()
    st.write(f"**Numeric Columns:** {len(numeric_cols)}")
with col_info[2]:
    date_cols = working_df.select_dtypes(include=['datetime64', 'object']).columns.tolist()
    st.write(f"**Text/Date Columns:** {len(date_cols)}")

# --- 🛠️ Column Selection ---
st.markdown("### 🛠️ <span style='font-size:1.1em'>Select Columns to Analyze</span>", unsafe_allow_html=True)
columns_selected = st.multiselect(
    "Select data columns to view and analyze:", working_df.columns.tolist(), default=working_df.columns.tolist())
filtered_df = working_df[columns_selected]
st.dataframe(filtered_df, use_container_width=True)

# ----------- 🤖 AI-Powered Insights & Recommendations (Dynamic) -----------
def dynamic_ai_insights(df):
    insights = []
    # ----- Revenue Metrics -----
    if 'Your Revenue' in df.columns and 'Industry Revenue' in df.columns:
        your_rev_mean = df['Your Revenue'].mean()
        industry_rev_mean = df['Industry Revenue'].mean()
        rev_gap = your_rev_mean - industry_rev_mean
        revenue_trend = df['Your Revenue'].pct_change().mean()*100 if len(df['Your Revenue'])>1 else None
        if revenue_trend is not None:
            if revenue_trend > 5:
                insights.append(f"🚀 Revenue is trending up (+{revenue_trend:.1f}%). Keep the momentum!")
            elif revenue_trend < -5:
                insights.append(f"📉 Revenue is trending down ({revenue_trend:.1f}%). Investigate possible causes.")
        if rev_gap > 0:
            insights.append("✅ Your average revenue outperforms the industry. Great job!")
        else:
            insights.append("⚠️ Industry revenue is higher. Explore changes to pricing, marketing, or products.")
        # Outlier detection for revenue drops
        if df['Your Revenue'].min() < your_rev_mean*0.7:
            insights.append("🧐 Unusually low revenue detected in some period(s). Review those for anomalies.")
    # ----- Expenses Metrics -----
    if 'Your Expenses' in df.columns and 'Your Revenue' in df.columns:
        expense_ratio = df['Your Expenses'].sum() / df['Your Revenue'].sum() if df['Your Revenue'].sum()>0 else None
        if expense_ratio is not None:
            if expense_ratio < 0.7:
                insights.append("🎯 Excellent expense control: Expenses < 70% of revenue.")
            elif expense_ratio < 0.8:
                insights.append("👍 Expenses under 80% of revenue. Maintain or improve efficiency.")
            elif expense_ratio > 1:
                insights.append("⚠️ Expenses exceed revenue! Immediate cost review recommended.")
        if 'Industry Expenses' in df.columns:
            ind_exp_mean = df['Industry Expenses'].mean()
            if df['Your Expenses'].mean() < ind_exp_mean:
                insights.append("💡 Your expenses are below industry average. Well done!")
            else:
                insights.append("🔎 Your expenses are above industry average. Look for cost savings.")
    # ---- Customers ----
    if 'Customers' in df.columns:
        cust_trend = df['Customers'].pct_change().mean()*100 if len(df['Customers'])>1 else None
        avg_cust = df['Customers'].mean()
        if cust_trend is not None:
            if cust_trend > 5:
                insights.append(f"📈 Growing customer base (+{cust_trend:.1f}%). Continue strong outreach.")
            elif cust_trend < -5:
                insights.append(f"⚠️ Customer #s declining ({cust_trend:.1f}%). Check retention/lead gen.")
        if avg_cust > 4000:
            insights.append("🌟 High customer base. Maybe segment for personalized offers.")
        elif avg_cust < 1500:
            insights.append("📢 Relatively low customer base—prioritize acquisition tactics.")
    # ----- General -----
    if not insights:
        insights.append("Upload more data for actionable, dynamic insights.")
    return insights

st.markdown("### 🤖 <span style='font-size:1.3em'>AI Insights & Recommendations</span>", unsafe_allow_html=True)
for tip in dynamic_ai_insights(filtered_df):
    st.info(tip)

# ----------- 📈 Interactive Charting & Gamification -----------
st.markdown("### 📊 <span style='font-size:1.2em'>Charts & Business Gamification</span>", unsafe_allow_html=True)
achievements = []
if len(numeric_cols) >= 2:
    main_fig = go.Figure([
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
    ])
    st.plotly_chart(main_fig, use_container_width=True)
    # -- Achievements Gamification/BADGES --
    if 'Revenue Rank' in filtered_df.columns and filtered_df['Revenue Rank'].min() == 1:
        achievements.append(("🏆 Top Industry Performer!", "#FFD700"))
    # Revenue Growth badge
    if 'Your Revenue' in filtered_df.columns:
        if filtered_df['Your Revenue'].pct_change().mean() > 0.1:
            achievements.append(("📈 10%+ Revenue Growth Streak!", "#4caf50"))
    # Outstanding cost control
    if 'Your Expenses' in filtered_df.columns and 'Your Revenue' in filtered_df.columns:
        expense_ratio = filtered_df['Your Expenses'].sum()/filtered_df['Your Revenue'].sum() if filtered_df['Your Revenue'].sum()>0 else 2
        if expense_ratio < 0.8:
            achievements.append(("🎯 Expenses under 80% of Revenue", "#2196f3"))
        elif expense_ratio > 1:
            achievements.append(("🚩 Expenses exceed revenue (monitor!)", "#e53935"))
    # Customer growth
    if 'Customers' in filtered_df.columns and filtered_df['Customers'].pct_change().mean() > 0.1:
        achievements.append(("🤝 10%+ Customer Growth", "#ff9800"))

    # Show achievements
    if achievements:
        for badge, color in achievements:
            st.markdown(f'<div style="display:inline-block;background:{color};color:black;padding:4px 18px;margin:4px;border-radius:16px;font-weight:bold;">{badge}</div>', unsafe_allow_html=True)
    completion_ratio = min(100, int(len(filtered_df)/10*100))  # Gamified metric (example logic)
    st.progress(completion_ratio, text=f"Data Analysis Progress: {completion_ratio}%")
else:
    st.warning("Not enough numeric columns for charting/gamification.")

# ----------- 🎮 Feedback & Next Steps -----------
st.markdown("### 💬 <span style='font-size:1.2em'>Rate Your Session & Get Next Steps</span>", unsafe_allow_html=True)
feedback_col1, feedback_col2 = st.columns([.3, .7])
with feedback_col1:
    rating = st.radio("How was your dashboard session?", ["👍 Great", "👌 Good", "😐 Okay", "👎 Needs work"])
with feedback_col2:
    if rating == "👍 Great":
        st.success("🎉 Awesome! Keep uploading new data for more insights. Check achievements below!")
    elif rating == "👌 Good":
        st.info("Glad you found it helpful! Try expanding your dataset for even richer insights.")
    elif rating == "😐 Okay":
        st.warning("Thanks for your honesty—see the help popup for tips or try uploading new data.")
    elif rating == "👎 Needs work":
        st.error("We'll keep improving. Please leave detailed feedback for us on GitHub!")

# ----------- 🎁 Free forever blurb -----------
st.markdown("### 🎁 100% <span style='font-size:1.2em'>No-Cost Platform</span>", unsafe_allow_html=True)
st.info("Echolon AI Dashboard is completely free: No licensing fees, no premium paywalls. Built for startups and SMBs.")

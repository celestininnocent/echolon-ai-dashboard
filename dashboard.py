import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime, timedelta

# Custom dark theme styling
st.markdown(
    '''
    body, .stApp {background-color: #181C24!important; color: #F3F6F9!important;}
    .st-emotion-cache-2trqyj {color: #3ECF8E!important;}
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-1p66bqe {background: #111217 !important;}
    header {background: none!important;}
    .urgent {color:red; font-weight: bold;}
    .owner {color:#3ECF8E!important;}
    .metric-card {background: #202634; border-radius: 16px; padding: 24px 8px; text-align: center; margin:8px; color:#F3F6F9}
    .kpiIcon {font-size:32px; margin-bottom:8px;}
    ''' , unsafe_allow_html=True)
st.set_page_config(page_title="Echolon AI Dashboard", layout="wide", initial_sidebar_state="expanded")
#------------------ Module Scaffold Logic ------------------#
def overview_module():
    st.markdown("## 📋 Overview")
    with st.expander("Platform Features", expanded=True):
        st.markdown("""
        - Modular dashboard navigation (sidebar)
        - AI-driven tips and insights
        - Scenario modeling and benchmarking
        - Goal tracking and achievements
        - Collaboration tools and feedback
        """)
        st.info("Use the sidebar to navigate modules – each module is ready for future logic.")
    st.markdown("---")
    st.markdown(
        "### 🆚 **Echolon vs. Visa Analytics Dashboards**\n- Flexible data, no locked models\n- Personalization and AI\n- Gamified progress and achievements\n- **Free for startups/SMBs!**"
    )
def data_upload_module():
    st.markdown("## 📁 Data Upload & Integration")
    with st.expander("Upload your CSV file", expanded=True):
        uploaded = st.file_uploader("Upload CSV Data (any columns)", type=["csv"])
        if uploaded:
            try:
                df = pd.read_csv(uploaded)
                st.success(f"CSV loaded: {len(df)} rows, {len(df.columns)} columns.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.info("No file uploaded. Demo mode active.")
        st.markdown("- Sample data and preview will be shown here.")
        st.button("Reload data")
def industry_benchmark_module():
    st.markdown("## ⚖️ Industry Benchmarking")
    with st.expander("Compare your metrics to the industry", expanded=True):
        st.slider("Select industry peer group", min_value=1, max_value=5, value=3)
        st.text_input("Industry or segment", value="SaaS")
        st.markdown("- View comparative charts and KPIs here.")
        st.line_chart(np.random.randint(75000, 120000, 7))
def scenario_modeling_module():
    st.markdown("## 📊 Scenario Modeling")
    with st.expander("Simulate future business outcomes", expanded=True):
        # Data integration
        uploaded = st.session_state.get('uploaded_csv') if 'uploaded_csv' in st.session_state else None
        df = None
        if uploaded is None:
            uploaded = st.file_uploader("Upload CSV Data (any columns)", type=["csv"])
            if uploaded:
                try:
                    df = pd.read_csv(uploaded)
                    st.session_state['uploaded_csv'] = uploaded
                    st.session_state['df'] = df
                except Exception as e:
                    st.error(f"Error loading CSV: {e}")
            else:
                st.info("No file uploaded. Demo mode active.")
        else:
            df = st.session_state.get('df')

        # Defaults
        fallback = {'Revenue': 100000, 'Expenses': 60000, 'Customers': 800}
        last_revenue = fallback['Revenue']
        last_expenses = fallback['Expenses']
        last_customers = fallback['Customers']

        latest_date = None
        if isinstance(df, pd.DataFrame):
            # Flexible column name handling
            rev_col = next((c for c in df.columns if c.lower() in ['revenue', 'total_revenue', 'sales']), None)
            exp_col = next((c for c in df.columns if c.lower() in ['expenses', 'cost', 'total_expenses']), None)
            cust_col = next((c for c in df.columns if c.lower() in ['customers', 'num_customers', 'customer_count']), None)

            # Try to use the rightmost/latest row
            try:
                idx = -1
                last_revenue = float(df[rev_col].iloc[idx]) if rev_col else fallback['Revenue']
                last_expenses = float(df[exp_col].iloc[idx]) if exp_col else fallback['Expenses']
                last_customers = float(df[cust_col].iloc[idx]) if cust_col else fallback['Customers']
                latest_date = df.index[idx] if df.index.name else None
            except Exception as e:
                st.warning(f"Problem extracting data: using demo values. {e}")

        # Inputs
        rv_growth = st.slider("Expected Revenue Growth (%)", -20, 60, 10)
        exp_control = st.slider("Expense Control (%)", 40, 110, 80)
        cust_growth = st.slider("Customer Growth (%)", -10, 30, 5)

        periods = 12
        dates = [datetime.today() + timedelta(days=30 * i) for i in range(periods)]
        revenue_proj = [last_revenue * (1 + rv_growth / 100) ** i for i in range(periods)]
        expense_proj = [last_expenses * (exp_control / 100) ** i for i in range(periods)]
        customers_proj = [last_customers * (1 + cust_growth / 100) ** i for i in range(periods)]

        # Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=revenue_proj, mode='lines+markers', name='Revenue',
            line=dict(color='#3ECF8E', width=3), marker=dict(size=8),
            hovertemplate='Projected Revenue<br>%{x|%b %Y}: <b>$%{y:,.0f}</b>'
        ))
        fig.add_trace(go.Scatter(
            x=dates, y=expense_proj, mode='lines+markers', name='Expenses',
            line=dict(color='#e74c3c', width=3, dash='dash'), marker=dict(size=8),
            hovertemplate='Projected Expenses<br>%{x|%b %Y}: <b>$%{y:,.0f}</b>'
        ))
        fig.add_trace(go.Scatter(
            x=dates, y=customers_proj, mode='lines+markers', name='Customers',
            line=dict(color='#1f77b4', width=3, dash='dot'), marker=dict(size=8),
            hovertemplate='Projected Customers<br>%{x|%b %Y}: <b>%{y:,.0f}</b>'
        ))
        fig.update_layout(
            title='Business Projections (Data-Driven)',
            legend=dict(x=0, y=1.1, orientation="h"),
            xaxis_title='Date',
            yaxis_title='Amount/USD',
            template='plotly_dark',
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)

        # Table
        forecast_df = pd.DataFrame({
            'Date': [d.strftime('%b %Y') for d in dates],
            'Projected Revenue': revenue_proj,
            'Projected Expenses': expense_proj,
            'Projected Customers': customers_proj
        })
        st.dataframe(forecast_df.style.format({
            'Projected Revenue': "${:,.0f}",
            'Projected Expenses': "${:,.0f}",
            'Projected Customers': "{:,.0f}"
        }), use_container_width=True)
        st.markdown("### Monetizable Business Insight Summary")
        st.success(f"Projected annual revenue: ${revenue_proj[-1]:,.0f} (+{rv_growth}% growth scenario)")
        st.warning(f"Annual expenses could reach: ${expense_proj[-1]:,.0f} (Expense control: {exp_control}%)")
        st.info(f"Projected customer base: {customers_proj[-1]:,.0f} (+{cust_growth}% scenario)")
        st.markdown("Actionable recommendations: Invest in top-line growth, optimize expense ratios, and focus on customer acquisition for higher ROI.")
def goal_tracking_module():
    st.markdown("## 🎯 Goal Tracking")
    with st.expander("Set and view business goals", expanded=True):
        goal = st.text_input("Describe your KPI/metric goal", value="Increase revenue 15%")
        date_target = st.date_input("Target Date", datetime.today())
        st.progress(0.2, text="Progress toward goal: 20% (demo)")
        st.markdown("- Automatic reminders, achievement badges, and progress soon!")
def ai_insights_module():
    st.markdown("## 🤖 AI Insights & Recommendations")
    with st.expander("Dynamic tips for your data", expanded=True):
        st.markdown("_Upload data for actionable AI analysis._")
        st.info("Industry average is higher. Explore pricing, marketing, or product changes.")
        st.warning("Low customer base detected: prioritize acquisition tactics.")
        st.success("Your expenses are below industry average. Well done!")
        st.markdown("- Outlier alerts and explanations go here.")
def collaboration_module():
    st.markdown("## 📝 Collaboration & Notes")
    with st.expander("Share & annotate dashboard findings", expanded=True):
        st.text_area("Type notes, ideas, or action items", value="")
        st.button("Share note with team")
        st.markdown("- Multi-user, chat, annotation features incoming!")
        st.markdown("---")
        st.info("Future stretch: @mention teammates, assign goals, history view.")
def stretch_goals_module():
    st.markdown("## 🚀 Stretch Goals & Roadmap")
    with st.expander("Planned advanced features", expanded=True):
        st.markdown("- Predictive analytics\n- Real user feedback integration\n- Automated report generation\n- Many more (see GitHub issues)")
# ---------------- Sidebar Navigation -------------------
modules = {
    "Overview": overview_module,
    "Data Upload/Integration": data_upload_module,
    "Industry Benchmarking": industry_benchmark_module,
    "Scenario Modeling": scenario_modeling_module,
    "Goal Tracking": goal_tracking_module,
    "AI Insights & Recommendations": ai_insights_module,
    "Collaboration (Notes)": collaboration_module,
    "Stretch Goals": stretch_goals_module,
}
sidebar_choice = st.sidebar.radio("Navigate Modules", list(modules.keys()), index=0)
st.sidebar.markdown("---")
st.sidebar.info("Use this list to switch modules. Each page is a feature placeholder and ready for further logic/coding!")
modules[sidebar_choice]()

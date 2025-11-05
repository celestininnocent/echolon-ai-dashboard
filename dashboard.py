import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime, timedelta

# Custom dark theme styling
st.markdown(
    """
    <br>    body, .stApp {background-color: #181C24!important; color: #F3F6F9!important;}<br>    .st-emotion-cache-2trqyj {color: #3ECF8E!important;}<br>    .st-emotion-cache-1v0mbdj, .st-emotion-cache-1p66bqe {background: #111217 !important;}<br>    header {background: none!important;}<br>    .urgent {color:red; font-weight: bold;}<br>    .owner {color:#3ECF8E!important;}<br>    .metric-card {background: #202634; border-radius: 16px; padding: 24px 8px; text-align: center; margin:8px; color:#F3F6F9}<br>    .kpiIcon {font-size:32px; margin-bottom:8px;}<br>
    """,
    unsafe_allow_html=True,
)
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

# ---------------------------------------------------------- #
def industry_benchmark_module():
    st.markdown("## ⚖️ Industry Benchmarking")
    with st.expander("Compare your metrics to the industry", expanded=True):
        st.slider("Select industry peer group", min_value=1, max_value=5, value=3)
        st.text_input("Industry or segment", value="SaaS")
        st.markdown("- View comparative charts and KPIs here.")
        st.line_chart(np.random.randint(75000, 120000, 7))

# ---------------------------------------------------------- #
def scenario_modeling_module():
    st.markdown("## 📊 Scenario Modeling")
    with st.expander("Simulate future business outcomes", expanded=True):
        # Inputs
        rv_growth = st.slider("Expected Revenue Growth (%)", -20, 60, 10)
        exp_control = st.slider("Expense Control (%)", 40, 110, 80)
        cust_growth = st.slider("Customer Growth (%)", -10, 30, 5)

        # Demo starting values (could load from file/data input)
        revenue_now = 100000
        expense_now = 50000
        customers_now = 500
        periods = 12
        dates = pd.date_range(datetime.today(), periods=periods, freq='M')
        # Project future KPIs
        revenue_proj = [revenue_now]
        expense_proj = [expense_now]
        customers_proj = [customers_now]
        for t in range(1, periods):
            revenue_proj.append(revenue_proj[-1] * (1 + rv_growth / 100.0))
            expense_proj.append(expense_proj[-1] * (exp_control / 100.0))
            customers_proj.append(customers_proj[-1] * (1 + cust_growth / 100.0))
        revenue_proj = np.array(revenue_proj)
        expense_proj = np.array(expense_proj)
        customers_proj = np.array(customers_proj)
        # --------------- Graph 1: Time-series projections ---------------- #
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=dates, y=revenue_proj, mode='lines+markers',
                                  name='Projected Revenue', line=dict(color='#3ECF8E', width=3)))
        fig1.add_trace(go.Scatter(x=dates, y=expense_proj, mode='lines+markers',
                                  name='Projected Expenses', line=dict(color='#EC4848', width=3)))
        fig1.add_trace(go.Scatter(x=dates, y=customers_proj, mode='lines+markers',
                                  name='Projected Customers', line=dict(color='#8293F7', width=3)))
        fig1.update_layout(title='12-Month Business KPI Projections', xaxis_title='Date', yaxis_title='Value',
                          hovermode='x unified', legend=dict(orientation='h', x=0, y=1.1))
        st.plotly_chart(fig1, use_container_width=True)
        # --------------- Graph 2: Sensitivity Analysis ------------------- #
        sens_labels = ['Revenue Growth (%)', 'Expense Control (%)', 'Customer Growth (%)']
        sens_values = [rv_growth, exp_control, cust_growth]
        base_revenue = revenue_now * (1 + rv_growth / 100.0)
        base_expense = expense_now * (exp_control / 100.0)
        base_customers = customers_now * (1 + cust_growth / 100.0)
        sens_kpi = [base_revenue - revenue_now, expense_now - base_expense, base_customers - customers_now]
        fig2 = go.Figure([go.Bar(x=sens_labels, y=sens_kpi, text=[f'{x:,.0f}' for x in sens_kpi],
                                 marker_color=['#3ECF8E', '#EC4848', '#8293F7'],
                                 hovertemplate='%{x}: %{y:,.2f}<extra></extra>')])
        fig2.update_layout(title='Sensitivity Analysis: KPI Impact per Variable', yaxis_title='Change from Current', xaxis_title='',
                          plot_bgcolor='#181C24', paper_bgcolor='#181C24', font=dict(color='#F3F6F9'))
        st.plotly_chart(fig2, use_container_width=True)
        # --------------- Graph 3: Current vs Projected ------------------- #
        current_labels = ['Revenue', 'Expenses', 'Customers']
        current_values = [revenue_now, expense_now, customers_now]
        proj_values = [revenue_proj[-1], expense_proj[-1], customers_proj[-1]]
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=current_labels, y=current_values, name='Current', marker_color='#636EFA'))
        fig3.add_trace(go.Bar(x=current_labels, y=proj_values, name='Projected (12mo)', marker_color='#3ECF8E'))
        fig3.update_layout(barmode='group', title='Current vs Projected KPI Comparison', yaxis_title='Value',
                          plot_bgcolor='#181C24', paper_bgcolor='#181C24', font=dict(color='#F3F6F9'))
        st.plotly_chart(fig3, use_container_width=True)
        # --------------- Forecast Table & Summary ------------------------ #
        forecast_df = pd.DataFrame({
            'Date': dates,
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

# ---------------------------------------------------------- #
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

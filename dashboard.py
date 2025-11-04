import streamlit as st
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

# Sidebar layout
with st.sidebar:
    st.title("Echolon AI 🧩")
    st.markdown("**AI-powered BI for small & midsize businesses**")
    st.divider()
    st.markdown("*Start by uploading your data or browse dashboard modules.*")

# Top Title
st.title("Echolon AI Business Analytics Dashboard")
st.markdown(
    "> Modular, AI-driven dashboard for data-backed decisions."
)

with st.expander("📤 Upload & Data Integration", expanded=True):
    st.info("Upload CSV or connect via API. Auto-detects columns for preview.")
    st.button("Upload CSV")
    st.write("Sample data preview here.")

with st.expander("📈 Industry Benchmarking", expanded=True):
    st.info("Compare metrics to industry benchmarks. See % difference and color-coded results.")
    st.write("(Benchmarking table will appear here)")

with st.expander("🔮 'What If?' Scenario Modeling", expanded=True):
    st.info("Adjust variables, simulate revenue/profit, and see results in a chart.")
    st.slider("Ad Spend % Change", -50, 50, 0)
    st.slider("Price % Change", -25, 25, 0)
    st.slider("Churn Rate Change", -10, 10, 0)
    st.write("(Projected revenue/profit chart placeholder)")

with st.expander("🎯 Goal Tracking", expanded=True):
    st.info("Set targets, track progress, and get AI suggestions for recovery.")
    st.write("Monthly Target Setup")
    st.progress(0)
    st.markdown("**AI Suggestions:** Reallocate 10-15% from underperforming channels.")

with st.expander("🧠 AI Insights & Recommendations", expanded=True):
    st.info("Mock AI suggestions will show here.")
    st.markdown(
        "- Customer retention dropped due to inconsistent purchase frequency.\n"
        "- Your ad spend ROI is strongest on Mondays — consider reallocating."
    )

with st.expander("💬 Collaboration", expanded=True):
    st.info("Simple notes for team communication.")
    st.text_area("Add Note", "", height=80)
    st.button("Save Note")

# Stretch Goals placeholder
with st.expander("🚀 Stretch Goals (Not Yet Implemented)"):
    st.write("- Auto-generate AI summaries\n- Basic user login\n- Session history storage")

st.markdown("---")
st.markdown("_Start by setting up the Streamlit structure for this dashboard, including the sidebar and placeholders for each module. Then we’ll add logic step by step._")

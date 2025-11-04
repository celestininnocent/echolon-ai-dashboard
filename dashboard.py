import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import io
import requests

# ---- THEME ----
st.set_page_config(page_title="Echolon AI Dashboard", layout="wide", initial_sidebar_state="expanded")
st.markdown("""    body, .stApp, .css-1d391kg, .css-14xtw13 {background-color: #181C24!important; color: #F3F6F9!important;}
    .st-emotion-cache-2trqyj {color: #3ECF8E!important;}
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-1p66bqe {background: #111217  !important;}
    header {background: none!important;}
    .stTextInput > div > div > input, .stTextInput textarea {color: #fafcff!important; background-color: #232836!important;}
    .stDataFrame {background-color: #191b21!important;}""", unsafe_allow_html=True)

# ---- SESSION STATE ----
SS = st.session_state
if 'notes' not in SS:
    SS['notes'] = ''
if 'targets' not in SS:
    SS['targets'] = {'Revenue': 80000, 'ConvRate': 0.08, 'Orders': 1800}
if 'csv_files' not in SS:
    SS['csv_files'] = []
if 'data' not in SS:
    SS['data'] = None
if 'mapping' not in SS:
    SS['mapping'] = {}
if 'all_colnames' not in SS:
    SS['all_colnames'] = set()
if 'ready' not in SS:
    SS['ready'] = False

REQUIRED = ['Date', 'Revenue', 'Expenses', 'Customers', 'Churn_Rate', 'Ad_Spend']
ICON = {'Date':'📆','Revenue':'💰','Expenses':'💸','Customers':'👥','Churn_Rate':'📉','Ad_Spend':'📢'}
BENCHMARKS = {'Revenue': 92000, 'Expenses': 29500, 'Customers': 1950, 'Churn_Rate':0.045, 'Ad_Spend':6700}

# ---- CONTEXT VAULT INTEGRATION ----
BACKEND_URL = "https://context-vault-backend-URL/vault"  # <-- replace with env for prod
MOCK_USER_ID = "test_user"  # Placeholder, replace for authentication integration in real deployment

def save_context(user_id, targets, notes, business_stats):
    payload = {
        "user_id": user_id,
        "business_stats": business_stats,
        "goals": targets,
        "notes": notes
    }
    try:
        resp = requests.post(f"{BACKEND_URL}/save", json=payload, timeout=6)
        if resp.status_code != 200:
            st.warning("Could not save latest context to backend.")
        return resp.ok
    except Exception as e:
        st.warning("Context Vault backend unreachable. Changes not saved.")
        return False

def get_latest_context(user_id):
    try:
        resp = requests.get(f"{BACKEND_URL}/context", params={"user_id": user_id}, timeout=6)
        if resp.status_code == 200:
            return resp.json()
        st.warning("Could not retrieve latest context from backend.")
    except Exception as e:
        st.warning("Context Vault backend unreachable. Context could not be loaded.")
    return None

# ---- HELPERS ----
def auto_map_cols(df):
    c = {col.lower().replace('_','').replace(' ',''):col for col in df.columns}
    out = {}
    for req in REQUIRED:
        for k in c:
            if req.lower().replace('_','').replace(' ','') in k:
                out[req]=c[k]
                break
    return out

# ---- SIDEBAR ----
with st.sidebar:
    st.title('🧊 Echolon AI')
    st.caption('AI-powered BI for businesses')
    st.markdown('---')
    tdf = pd.DataFrame({
        'Date': pd.date_range('2025-01-01','2025-01-10'),
        'Revenue':[50000,52000,48000,55000,53000,51000,54000,56000,49000,57000],
        'Expenses':[30000,31000,29000,32000,30500,31500,32500,33000,28000,34000],
        'Customers':[1200,1250,1180,1300,1270,1230,1290,1320,1190,1350],
        'Churn_Rate':[0.05,0.04,0.06,0.03,0.04,0.05,0.04,0.03,0.06,0.03],
        'Ad_Spend':[5000,5200,4800,5500,5300,5100,5400,5600,4900,5700]
    })
    buf = io.StringIO()
    tdf.to_csv(buf, index=False)
    st.download_button('⬇️ Download CSV Template',buf.getvalue(),'sample_data.csv',help='Sample file with correct headers')
    st.markdown('---')
    st.markdown('**Upload your CSVs** below')
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        SS['csv_files'].append(uploaded_file.name)
        df = pd.read_csv(uploaded_file)
        mapped = auto_map_cols(df)
        df = df.rename(columns=mapped)
        SS['data'] = df
        SS['all_colnames'] = set(df.columns)
        SS['ready'] = True
        # Save context after upload
        business_stats = {
            "stats": {k:df[k].mean() if k in df else None for k in REQUIRED if k != 'Date'}
        }
        save_context(MOCK_USER_ID, SS['targets'], SS['notes'], business_stats)
        st.success("CSV uploaded and context saved to backend!")

# ---- MAIN DASHBOARD ----
if SS['ready'] and SS['data'] is not None:
    df = SS['data']
    c1,c2,c3 = st.columns(3)
    c1.metric('💰 Total Revenue',f"${df['Revenue'].sum():.0f}")
    c2.metric('💸 Total Expenses',f"${df['Expenses'].sum():.0f}")
    c3.metric('👥 Customers',f"{df['Customers'].mean():.0f}")
    st.line_chart(df.set_index('Date')[['Revenue','Expenses']], use_container_width=True)

    # ---- INDUSTRY BENCHMARKING ----
    with st.expander('🏆 Industry Benchmarking',expanded=True):
        st.markdown('Compare your metrics to industry benchmarks.')
        bm = BENCHMARKS
        dfm = {k:df[k].mean() for k in bm if k in df}
        col1,col2 = st.columns(2)
        with col1:
            st.write("### Metric vs. Benchmark")
            for k in bm:
                diff = 100*(dfm.get(k,0)-bm[k])/bm[k]
                arrow = "⬆️" if diff>0 else "⬇️"
                color = "green" if diff>0 else "red"
                st.markdown(f"{ICON[k]} **{k}**: {dfm.get(k,0):.2f} | Benchmark: {bm[k]:.2f} | <span style='color:{color}'>{arrow} {diff:.1f}%</span>", unsafe_allow_html=True)
        with col2:
            st.bar_chart(pd.DataFrame({'User Data':dfm,'Benchmark':bm}))

    # ---- WHAT IF? SCENARIO MODELING ----
    with st.expander('🤔 What If? Scenario Modeling',expanded=False):
        st.write('Adjust business levers and see impact projections.')
        ad_pct = st.slider('Ad Spend % Change',-50,50,0,step=5, help='Simulate raising/lowering ad spend')
        price_pct = st.slider('Avg. Price % Change',-20,20,0,step=2)
        churn_delta = st.slider('Churn Rate % Change',-50,50,0,step=5)
        scenario = df.copy()
        scenario['Ad_Spend'] *= (1+ad_pct/100)
        scenario['Revenue'] *= (1+price_pct/100)
        scenario['Churn_Rate'] *= (1+churn_delta/100)
        st.line_chart(scenario.set_index('Date')[['Revenue','Ad_Spend','Churn_Rate']])
        st.caption('Projections based on simple proportional adjustment.')

    # ---- GOAL TRACKING ----
    with st.expander('🎯 Goal Tracking',expanded=False):
        st.write('Set monthly goals. See progress and suggestions.')
        colA, colB, colC = st.columns(3)
        t = SS['targets']
        t['Revenue']=colA.number_input('Monthly Revenue Target',min_value=10000,value=t['Revenue'],key='t_rev')
        t['ConvRate']=colB.number_input('Monthly Conversion Rate Target', min_value=0.0, max_value=1.0, value=t['ConvRate'], format="%.2f", key='t_conv')
        t['Orders']=colC.number_input('Monthly Orders Target',min_value=10,value=t['Orders'],key='t_ord')
        act_rev = df['Revenue'].sum()
        act_cr = (df['Customers'].sum()/max(df['Customers'].count(),1)) if not df.empty else 0
        act_ord = df['Customers'].sum()
        st.progress(min(act_rev/t["Revenue"],1.0),f'Revenue Progress: {act_rev:.0f} / {t["Revenue"]}')
        st.progress(min(act_cr/t["ConvRate"],1.0),f'Conversion Rate: {act_cr:.2%} / {t["ConvRate"]:.2%}')
        st.progress(min(act_ord/t["Orders"],1.0),f'Orders: {act_ord:.0f} / {t["Orders"]}')
        # Save context after goals change
        save_context(MOCK_USER_ID, t, SS['notes'], {"stats": {k:df[k].mean() for k in REQUIRED if k != 'Date'}})
        with st.expander('💡 AI Suggestions',expanded=False):
            st.write("To recover your goals, consider reducing churn and re-engaging lost customers through targeted campaigns.")

    # ---- AI INSIGHTS ----
    # Fetch Context Vault context before generating AI advice
    user_context = get_latest_context(MOCK_USER_ID)
    advice_text = "Customer retention dropped due to inconsistent purchase frequency last quarter.\nChurn increased as advertising wasn't sustained.\nTop suggestion: Focus ad budget on top 2 high-LTV segments."
    if user_context:
        advice_text += f"\n\nContext Vault notes: {user_context.get('notes','')}\nBusiness goals: {user_context.get('goals','')}"

    with st.expander('🤖 AI Insights & Recommendations',expanded=False):
        st.info(advice_text)
        st.caption('This section will support OpenAI/LLM hooks in the future.')

    # ---- COLLABORATION NOTES ----
    with st.expander('📝 Collaboration / Notes',expanded=False):
        notes = st.text_area("Add collaboration notes, observations, or ideas here:",SS['notes'])
        if notes != SS['notes']:
            SS['notes'] = notes
            save_context(MOCK_USER_ID, SS['targets'], notes, {"stats": {k:df[k].mean() for k in REQUIRED if k != 'Date'}})
            st.success('Notes updated & context saved!')

# --- SECURITY & API KEY INTEGRATION COMMENTS: ---
# In production:
#   - Use secure env variables for BACKEND_URL and any API key, not hardcoded!
#   - Integrate user authentication, replace MOCK_USER_ID with real user identity.
#   - Use HTTPS endpoints only.
#   - Validate backend response data and sanitize user inputs.
#   - Do not log/store sensitive info insecurely.

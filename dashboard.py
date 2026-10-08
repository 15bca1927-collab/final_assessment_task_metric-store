import streamlit as st
import pandas as pd
from engine.executor import SemanticEngine

st.set_page_config(page_title="Metric Store Explorer", layout="wide")
st.title("📊 Wealth Management Metric Store")

engine = SemanticEngine()
available = engine.catalog.list_available_metrics()
metric_names = [m["name"] for m in available]

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Query Configuration")
    selected_metrics = st.multiselect("Select Metrics", metric_names, default=["total_aum"])
    
    dim_options = ["client_tier", "advisor_id"]
    selected_dims = st.multiselect("Dimensions (Group By)", dim_options, default=["client_tier"])
    
    tier_filter = st.selectbox("Filter Client Tier", ["All", "Retail", "Affluent", "HighNetWorth", "UltraHighNetWorth"])
    filters = {"client_tier": tier_filter} if tier_filter != "All" else {}
    
    run_btn = st.button("Run Semantic Query", type="primary")

with col2:
    if run_btn and selected_metrics:
        sql = engine.get_sql(metrics=selected_metrics, dimensions=selected_dims, filters=filters)
        st.subheader("Compiled SQL (Audit Trail)")
        st.code(sql, language="sql")
        
        df = engine.query(metrics=selected_metrics, dimensions=selected_dims, filters=filters)
        st.subheader("Results")
        st.dataframe(df, use_container_width=True)
        
        if selected_dims and len(selected_metrics) == 1:
            st.bar_chart(data=df.set_index(selected_dims[0])[selected_metrics[0]])

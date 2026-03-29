import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Setup the page
st.set_page_config(page_title="LEGO Portfolio Tracker", layout="wide")

st.title("🧱 Xiaoqi's LEGO Portfolio Dashboard")
st.markdown("Real-time valuation and ROI tracking")

# 1. FETCH DATA FROM YOUR FASTAPI
try:
    stats_res = requests.get("http://127.0.0.1:8000/portfolio/stats").json()
    sets_res = requests.get("http://127.0.0.1:8000/sets").json()

    # 2. TOP METRICS
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sets", stats_res['total_sets'])
    col2.metric("Total Invested", stats_res['summary']['total_investment'])
    col3.metric("Current Value", stats_res['summary']['current_market_value'])
    # The 'delta' shows the change. In our case, it's just the profit!
    col4.metric("Net Profit", stats_res['summary']['net_profit'], delta=stats_res['summary']['net_profit'])

    # 3. DATA TABLE
    st.subheader("Collection Breakdown")
    df = pd.DataFrame(sets_res)

    # Clean up the dataframe for display
    display_df = df[['set_name', 'set_number', 'theme', 'purchase_price', 'quantity']]
    st.dataframe(display_df, use_container_width=True)

    # 4. VISUALS: Theme Distribution
    st.subheader("Portfolio Composition by Theme")
    fig = px.pie(df, names='theme', title="Sets per Theme", hole=0.4)
    st.plotly_chart(fig)

except Exception as e:
    st.error(f"Could not connect to the API. Make sure uvicorn is running! Error: {e}")

with st.sidebar:
    st.header("➕ Add New Set")
    with st.form("add_set_form"):
        name = st.text_input("Set Name")
        num = st.text_input("Set Number")
        theme = st.selectbox("Theme", ["Botanical", "Icons", "Star Wars", "Ideas"])
        price = st.number_input("Purchase Price", min_value=0.0)
        qty = st.number_input("Quantity", min_value=1)

        submit = st.form_submit_button("Add to Collection")
        if submit:
            payload = {
                "set_name": name, "set_number": num, "theme": theme,
                "purchase_price": price, "quantity": qty,
                "estimated_market_value": price, "condition": "New",
                "is_sealed": True, "notes": ""
            }
            requests.post("http://127.0.0.1:8000/add-set", json=payload)
            st.success("Set Added!")
            st.rerun() # Refresh the dashboard
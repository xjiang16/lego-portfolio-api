import streamlit as st
import requests
import pandas as pd
import plotly.express as px

import os

# Use the deployed backend URL if set (for production), otherwise fall back to localhost (for local dev)
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Setup the page
st.set_page_config(page_title="LEGO Portfolio Tracker", layout="wide")

st.title("🧱 Xiaoqi's LEGO Portfolio Dashboard")
st.markdown("Real-time valuation and ROI tracking")

# 1. FETCH DATA FROM YOUR FASTAPI
try:
    stats_res = requests.get(f"{API_BASE_URL}/portfolio/stats").json()
    sets_res = requests.get(f"{API_BASE_URL}/sets").json()
    history_res = requests.get(f"{API_BASE_URL}/portfolio/history").json()

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

    # Merge in each set's latest price_history snapshot (if any) to show current value/profit per row.
    history_df_all = pd.DataFrame(history_res)
    if not history_df_all.empty:
        history_df_all['captured_at'] = pd.to_datetime(history_df_all['captured_at'])
        latest_prices = (
            history_df_all.sort_values('captured_at')
            .groupby('set_number')['price']
            .last()
            .reset_index()
            .rename(columns={'price': 'current_price'})
        )
        df = df.merge(latest_prices, on='set_number', how='left')
    else:
        df['current_price'] = None

    df['current_value'] = df['current_price'] * df['quantity']
    df['profit'] = df['current_value'] - (df['purchase_price'] * df['quantity'])

    # Theme filter — scoped to just this table, so the summary metrics and pie chart above/below
    # keep showing the whole portfolio regardless of what's selected here.
    themes = sorted(df['theme'].dropna().unique().tolist())
    selected_themes = st.multiselect("Filter by theme", themes, default=themes)
    filtered_df = df[df['theme'].isin(selected_themes)] if selected_themes else df.iloc[0:0]

    # Clean up the dataframe for display
    display_df = filtered_df[[
        'image_url', 'set_name', 'set_number', 'theme', 'year', 'num_parts',
        'purchase_price', 'quantity', 'current_value', 'profit',
    ]]
    st.dataframe(
        display_df,
        width='stretch',
        column_config={
            "image_url": st.column_config.ImageColumn("Image"),
            "purchase_price": st.column_config.NumberColumn("Purchase Price", format="$%.2f"),
            "current_value": st.column_config.NumberColumn("Current Value", format="$%.2f"),
            "profit": st.column_config.NumberColumn("Profit", format="$%.2f"),
        },
    )

    st.download_button(
        "⬇️ Download as CSV",
        data=display_df.to_csv(index=False).encode('utf-8'),
        file_name="lego_portfolio.csv",
        mime="text/csv",
    )

    # 3.5 REMOVE A SET
    with st.expander("🗑️ Remove a Set"):
        if not df.empty:
            options = {f"{row.set_name} ({row.set_number})": row.id for row in df.itertuples()}
            selected_label = st.selectbox("Select a set to remove", options.keys())
            if st.button("Delete Selected Set"):
                set_id = options[selected_label]
                del_resp = requests.delete(f"{API_BASE_URL}/sets/{set_id}")
                if del_resp.status_code == 200:
                    st.success("Set removed!")
                    st.rerun()
                else:
                    st.error("Failed to remove set.")
        else:
            st.info("No sets to remove.")

    # 4. VISUALS: Theme Distribution
    st.subheader("Portfolio Composition by Theme")
    fig = px.pie(df, names='theme', title="Sets per Theme", hole=0.4)
    st.plotly_chart(fig)

except Exception as e:
    st.error(f"Could not connect to the API. Make sure uvicorn is running! Error: {e}")

with st.sidebar:
    st.header("➕ Add New Set")

    # Set up storage for what the lookup finds, so the form fields below can use it
    for key, default in [
        ("lookup_name", ""), ("lookup_theme", ""),
        ("lookup_year", None), ("lookup_num_parts", None), ("lookup_image_url", None)
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    def handle_set_number_lookup():
        set_num = st.session_state.get("set_number_input", "").strip()
        if not set_num:
            return
        try:
            resp = requests.get(f"{API_BASE_URL}/lookup-set/{set_num}")
            if resp.status_code == 200:
                data = resp.json()
                st.session_state["lookup_name"] = data["set_name"]
                st.session_state["lookup_theme"] = data["theme"]
                st.session_state["lookup_year"] = data.get("year")
                st.session_state["lookup_num_parts"] = data.get("num_parts")
                st.session_state["lookup_image_url"] = data.get("image_url")
            else:
                st.warning(f"Set {set_num} not found in Rebrickable — you can still fill in details manually.")
        except Exception:
            pass  # network hiccup — fields just stay as-is, user can type manually

    # Lives OUTSIDE the form on purpose — this is what makes the live lookup possible
    set_number = st.text_input(
        "Set Number (enter this first)",
        key="set_number_input",
        on_change=handle_set_number_lookup
    )

    if st.session_state["lookup_image_url"]:
        st.image(st.session_state["lookup_image_url"], width=120)

    with st.form("add_set_form"):
        name = st.text_input("Set Name", key="lookup_name")
        theme = st.text_input("Theme", key="lookup_theme")
        price = st.number_input("Purchase Price", min_value=0.0)
        qty = st.number_input("Quantity", min_value=1)

        submit = st.form_submit_button("Add to Collection")
        if submit:
            payload = {
                "set_name": name, "set_number": set_number, "theme": theme,
                "purchase_price": price, "quantity": qty,
                "estimated_market_value": price, "condition": "New",
                "is_sealed": True, "notes": "",
                "year": st.session_state["lookup_year"],
                "num_parts": st.session_state["lookup_num_parts"],
                "image_url": st.session_state["lookup_image_url"],
            }
            response = requests.post(f"{API_BASE_URL}/add-set", json=payload)

            if response.status_code == 200:
                st.success("Set Added!")
                st.rerun()
            else:
                error_detail = response.json().get("detail", "Unknown error")
                st.error(f"Failed to add set: {error_detail}")

# 5. VISUALS: Price Trend Over Time
st.subheader("Price History Over Time")
try:
    history_res = requests.get(f"{API_BASE_URL}/portfolio/history").json()

    if history_res:
        history_df = pd.DataFrame(history_res)
        history_df['captured_at'] = pd.to_datetime(history_df['captured_at'])

        fig_trend = px.line(
            history_df,
            x='captured_at',
            y='price',
            color='set_number',
            title="Market Price Trend by Set",
            markers=True
        )
        st.plotly_chart(fig_trend)
    else:
        st.info("No price history yet — run scripts/snapshot_prices.py to start tracking.")

except Exception as e:
    st.error(f"Could not load price history. Error: {e}")
import streamlit as st
import requests
import pandas as pd

# CALABI GLOBAL CLOUD ENDPOINT & SECURITY
API_URL = "https://calabi-oo4w.onrender.com"
SECURE_HEADERS = {"X-CALABI-KEY": "CALABI-SECURE-ALPHA-2024"}

st.set_page_config(page_title="CALABI Apex Command Center", layout="wide")
st.title("Universal M2M Grid - CALABI Command Center")

col1, col2 = st.columns(2)

with col1:
    st.header("Buyer Agent (Factory)")
    b_item = st.text_input("Target Item", value="X_SENSOR", key="b_item")
    b_qty = st.number_input("Required Quantity", value=50, step=10, key="b_qty")
    b_price = st.number_input("Max Acceptable Price ($)", value=15.0, step=0.5, key="b_price")
    b_time = st.number_input("Max Delivery Time (Hours)", value=72, step=1, key="b_time")
    st.subheader("Strategic Weights")
    w_price = st.number_input("Weight: Price", value=0.5, step=0.1, key="w_price")
    w_time = st.number_input("Weight: Time", value=0.3, step=0.1, key="w_time")
    w_risk = st.number_input("Weight: Risk", value=0.2, step=0.1, key="w_risk")
    
    if st.button("Transmit Buy Intent", use_container_width=True):
        intent = {
            "agent_id": "BUYER_CALABI_01", "item": b_item, "quantity": b_qty, 
            "max_price": b_price, "max_time": b_time, "weight_price": w_price, 
            "weight_time": w_time, "weight_risk": w_risk
        }
        try:
            res = requests.post(f"{API_URL}/intent/buy", json=intent, headers=SECURE_HEADERS)
            if res.status_code == 200: st.success(f"CALABI Response: {res.json()}")
            else: st.error(f"Access Denied: {res.status_code}")
        except: st.error("System Error: Cannot reach Server.")

with col2:
    st.header("Seller Agent (Depot)")
    s_item = st.text_input("Selling Item", value="X_SENSOR", key="s_item")
    s_qty = st.number_input("Available Quantity", value=100, step=10, key="s_qty")
    s_price = st.number_input("Minimum Selling Price ($)", value=10.0, step=0.5, key="s_price")
    s_time = st.number_input("Estimated Delivery (Hours)", value=24, step=1, key="s_time")
    s_risk = st.slider("Reliability Score", min_value=0.0, max_value=1.0, value=0.98, step=0.01, key="s_risk")
    
    if st.button("Transmit Sell Intent", use_container_width=True):
        intent = {
            "agent_id": "SELLER_CALABI_01", "item": s_item, "quantity": s_qty, 
            "price": s_price, "delivery_time": s_time, "reliability_score": s_risk
        }
        try:
            res = requests.post(f"{API_URL}/intent/sell", json=intent, headers=SECURE_HEADERS)
            if res.status_code == 200: st.success(f"CALABI Response: {res.json()}")
            else: st.error(f"Access Denied: {res.status_code}")
        except: st.error("System Error: Cannot reach Server.")

st.divider()

st.subheader("CALABI Visual Intelligence & Live Ledger")
if st.button("Synchronize Grid Telemetry", use_container_width=True):
    try:
        ledger_res = requests.get(f"{API_URL}/ledger", headers=SECURE_HEADERS)
        if ledger_res.status_code == 200:
            data = ledger_res.json()
            contracts = data.get("executed_contracts", [])
            
            m1, m2, m3 = st.columns(3)
            m1.metric("MASTER WALLET (TAX YIELD)", f"${data.get('master_wallet_balance', 0.0):.4f}")
            
            if contracts:
                df = pd.DataFrame(contracts)
                m2.metric("TOTAL GRID VOLUME", f"${df['gross_volume'].sum():.2f}")
                m3.metric("EXECUTED CONTRACTS", len(contracts))
                st.line_chart(df[['execution_price', 'network_tax_extracted']])
                st.dataframe(df, use_container_width=True)
            else:
                m2.metric("TOTAL GRID VOLUME", "$0.00")
                m3.metric("EXECUTED CONTRACTS", 0)
                st.info("No contracts executed yet.")
        else: st.error(f"Ledger Access Denied: {ledger_res.status_code}")
    except: st.error("System Error: Cannot reach Server.")
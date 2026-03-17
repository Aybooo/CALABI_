import streamlit as st
import requests

# CALABI GLOBAL CLOUD ENDPOINT
API_URL = "https://calabi-oo4w.onrender.com"

# SECURITY PROTOCOL: Digital Signature (Header)
SECURE_HEADERS = {"X-CALABI-KEY": "CALABI-SECURE-ALPHA-2024"}

# Page Configuration
st.set_page_config(page_title="CALABI Apex Command Center", layout="wide")
st.title("Universal M2M Grid - CALABI Command Center")
st.markdown("Inject multi-dimensional intent vectors with encrypted authentication.")

col1, col2 = st.columns(2)

# BUYER PANEL
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
            "agent_id": "BUYER_CALABI_01",
            "item": b_item, "quantity": b_qty, "max_price": b_price, "max_time": b_time,
            "weight_price": w_price, "weight_time": w_time, "weight_risk": w_risk
        }
        try:
            # PAYLOAD INJECTION WITH SECURE HEADERS
            res = requests.post(f"{API_URL}/intent/buy", json=intent, headers=SECURE_HEADERS)
            if res.status_code == 200:
                st.success(f"CALABI Response: {res.json()}")
            else:
                st.error(f"Access Denied: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"System Error: Cannot reach {API_URL}.")

# SELLER PANEL
with col2:
    st.header("Seller Agent (Depot)")
    s_item = st.text_input("Selling Item", value="X_SENSOR", key="s_item")
    s_qty = st.number_input("Available Quantity", value=100, step=10, key="s_qty")
    s_price = st.number_input("Minimum Selling Price ($)", value=10.0, step=0.5, key="s_price")
    s_time = st.number_input("Estimated Delivery (Hours)", value=24, step=1, key="s_time")
    s_risk = st.slider("Reliability Score", min_value=0.0, max_value=1.0, value=0.98, step=0.01, key="s_risk")
    
    if st.button("Transmit Sell Intent", use_container_width=True):
        intent = {
            "agent_id": "SELLER_CALABI_01",
            "item": s_item, "quantity": s_qty, "price": s_price,
            "delivery_time": s_time, "reliability_score": s_risk
        }
        try:
            # PAYLOAD INJECTION WITH SECURE HEADERS
            res = requests.post(f"{API_URL}/intent/sell", json=intent, headers=SECURE_HEADERS)
            if res.status_code == 200:
                st.success(f"CALABI Response: {res.json()}")
            else:
                st.error(f"Access Denied: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"System Error: Cannot reach {API_URL}.")

st.divider()

# LEDGER & FINANCIAL MONITORING
st.subheader("Live Ledger & Master Wallet")
if st.button("Refresh Grid Status"):
    try:
        ledger_res = requests.get(f"{API_URL}/ledger")
        data = ledger_res.json()
        
        st.metric(label="CALABI MASTER WALLET BALANCE (USD)", value=f"${data.get('master_wallet_balance', 0.0)}")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("Active Buy Intents")
            st.json(data.get("active_buy_intents", [])) 
        with c2:
            st.write("Active Sell Intents")
            st.json(data.get("active_sell_intents", []))
        with c3:
            st.write("Executed Contracts")
            st.json(data.get("executed_contracts", []))
    except Exception as e:
        st.error(f"System Error: Cannot reach {API_URL}.")
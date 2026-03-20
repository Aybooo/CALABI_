import streamlit as st
import requests
import pandas as pd
import random

# --- 1. CORE CONFIGURATION ---
st.set_page_config(page_title="CALABI V7 - Tokenized Economy", layout="wide")
API_URL = "https://calabi-oo4w.onrender.com"
HEADERS = {"X-CALABI-KEY": "CALABI-SECURE-ALPHA-2024"}

st.title("CALABI V7 - Otonom Ekonomi Komuta Merkezi")
st.markdown("---")

# --- 2. INTENT INJECTION (Niyet Vektörleri) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🔵 Alıcı Enjeksiyonu")
    b_agent = st.text_input("Ajan ID (Alıcı)", value=f"BUYER-{random.randint(100,999)}")
    b_item = st.text_input("Varlık (Alıcı)", value="A-TYPE-DATA")
    b_qty = st.number_input("Miktar (Alıcı)", min_value=1, value=10)
    b_price = st.number_input("Maks. Fiyat", min_value=0.01, value=15.00, step=0.1)
    b_time = st.number_input("Maks. Bekleme (sn)", min_value=1, value=60)
    
    if st.button("Fırlat (Alım Vektörü)"):
        payload = {
            "agent_id": b_agent, "item": b_item, "quantity": b_qty,
            "max_price": b_price, "max_time": b_time
        }
        res = requests.post(f"{API_URL}/intent/buy", json=payload, headers=HEADERS)
        st.code(res.text)

with col2:
    st.subheader("🔴 Satıcı Enjeksiyonu")
    s_agent = st.text_input("Ajan ID (Satıcı)", value=f"SELLER-{random.randint(100,999)}")
    s_item = st.text_input("Varlık (Satıcı)", value="A-TYPE-DATA")
    s_qty = st.number_input("Miktar (Satıcı)", min_value=1, value=10)
    s_price = st.number_input("Taban Fiyat", min_value=0.01, value=10.00, step=0.1)
    s_time = st.number_input("Teslimat (sn)", min_value=0, value=10)
    
    if st.button("Fırlat (Satım Vektörü)"):
        payload = {
            "agent_id": s_agent, "item": s_item, "quantity": s_qty,
            "price": s_price, "delivery_time": s_time
        }
        res = requests.post(f"{API_URL}/intent/sell", json=payload, headers=HEADERS)
        st.code(res.text)

with col3:
    st.subheader("⚡ İtibar Motoru")
    resolve_id = st.number_input("Sözleşme ID", min_value=1, step=1)
    resolve_status = st.selectbox("Sözleşme Sonucu", options=[1, 0], format_func=lambda x: "BAŞARILI (+0.01 Rs)" if x == 1 else "BAŞARISIZ (-0.05 Rs)")
    
    if st.button("Sözleşmeyi Kapat"):
        res = requests.post(f"{API_URL}/contract/resolve/{resolve_id}", json={"status": resolve_status}, headers=HEADERS)
        st.code(res.text)

st.markdown("---")

# --- 3. V7 FRACTAL LEDGER & TOKENOMICS ---
if st.button("Senkronize Et (Makro-Ekonomi Telemetrisi)", type="primary"):
    try:
        response = requests.get(f"{API_URL}/ledger", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            
            # Üst Metrikler (Ana Kasa ve Yetimler)
            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric("Ağ Vergisi (Master Wallet)", f"${data.get('master_wallet_balance', 0):.4f}")
            mcol2.metric("Aktif Alıcılar (Bekleyen)", data.get('active_orphans', {}).get('buyers', 0))
            mcol3.metric("Aktif Satıcılar (Bekleyen)", data.get('active_orphans', {}).get('sellers', 0))
            
            st.markdown("---")
            
            # V7 Liderlik Tablosu (En Zengin Ajanlar)
            top_agents = data.get("top_agents", [])
            if top_agents:
                st.subheader("🏆 Apex Ajanları (En Yüksek Likidite)")
                cols = st.columns(len(top_agents))
                for i, agent in enumerate(top_agents):
                    with cols[i]:
                        st.info(f"**{agent['agent_id']}**\n\nBakiye: **${agent['balance']:.2f}**\n\nRs: {agent['Rs']}")
            
            # Sözleşme Tablosu
            contracts = data.get("executed_contracts", [])
            if contracts:
                df = pd.DataFrame(contracts)
                st.subheader("Gerçekleşen Sözleşmeler (Son 50)")
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Defter-i Kebir şu an boş. Sisteme niyet vektörü fırlatın.")
                
        elif response.status_code == 403:
            st.error("ERİŞİM REDDEDİLDİ: API Anahtarı geçersiz.")
        else:
            st.error(f"SİSTEM HATASI: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Fiziksel Bağlantı Koptu: {e}")
import streamlit as st
import requests
import pandas as pd

# --- 1. CORE CONFIGURATION ---
st.set_page_config(page_title="CALABI V10.1 - Otonom Enerji ve Lojistik Matrisi", layout="wide")
API_URL = "https://calabi-oo4w.onrender.com"
HEADERS = {"X-CALABI-KEY": "CALABI-SECURE-ALPHA-2024"}

st.title("CALABI V10.1 - Endüstriyel Enerji & Lojistik Komuta Merkezi")
st.markdown("---")

# --- 2. INTENT, SYNTHESIS & MUTATION INJECTION ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🔵 Talep Enjeksiyonu (Şebeke/Kargo)")
    b_agent = st.text_input("Ajan ID (Alıcı/Tüketici)", value="BUYER-NODE-1", key="b_id")
    b_item = st.selectbox("Endüstriyel Varlık", ["MWh-ENERGY", "FREIGHT-TON"], key="b_item")
    b_qty = st.number_input("Talep Miktarı", min_value=1, value=100, key="b_qty")
    b_price = st.number_input("Maks. Birim Fiyat (USD)", min_value=0.01, value=15.00, step=0.1, key="b_price")
    b_time = st.number_input("Maks. SLA Süresi (sn)", min_value=1, value=60, key="b_time")
    
    if st.button("Fırlat (Talep)", key="btn_buy"):
        payload = {"agent_id": b_agent, "item": b_item, "quantity": b_qty, "max_price": b_price, "max_time": b_time}
        res = requests.post(f"{API_URL}/intent/buy", json=payload, headers=HEADERS)
        st.code(res.text)

with col2:
    st.subheader("⛏️ Kapasite Sentezi (Üretim/İntikal)")
    m_agent = st.text_input("Ajan ID (Üretici/Filo)", value="SELLER-NODE-1", key="m_id")
    m_qty = st.number_input("Sentezlenecek Kapasite", min_value=1, value=100, key="m_qty")
    st.caption("Üretim Maliyeti: Tier 1 ($2.0) | Tier 2 ($1.0)")
    
    if st.button("Kapasite Üret (Sentez)", key="btn_mine"):
        payload = {"agent_id": m_agent, "quantity": m_qty}
        res = requests.post(f"{API_URL}/intent/mine", json=payload, headers=HEADERS)
        st.code(res.text)

with col3:
    st.subheader("🔴 Arz Enjeksiyonu (Satış)")
    s_agent = st.text_input("Ajan ID (Satıcı)", value="SELLER-NODE-1", key="s_id")
    s_item = st.selectbox("Arz Edilen Varlık", ["MWh-ENERGY", "FREIGHT-TON"], key="s_item")
    s_qty = st.number_input("Arz Miktarı", min_value=1, value=100, key="s_qty")
    s_price = st.number_input("Taban Fiyat (USD)", min_value=0.01, value=10.00, step=0.1, key="s_price")
    s_time = st.number_input("Taahhüt Edilen Süre (sn)", min_value=0, value=10, key="s_time")
    
    if st.button("Fırlat (Arz)", key="btn_sell"):
        payload = {"agent_id": s_agent, "item": s_item, "quantity": s_qty, "price": s_price, "delivery_time": s_time}
        res = requests.post(f"{API_URL}/intent/sell", json=payload, headers=HEADERS)
        st.code(res.text)

st.markdown("---")

col4, col5 = st.columns(2)

with col4:
    st.subheader("🧬 Endüstriyel Mutasyon (Donanım Evrimi)")
    u_agent = st.text_input("Ajan ID (Yükseltilecek)", value="SELLER-NODE-1", key="u_id")
    st.caption("Maliyet: 1500 USD | Etki: Otonom Filo veya Katı Hal Bataryaya geçiş. Maliyet yarıya düşer.")
    
    if st.button("Evrimi Başlat (Tier 2 Upgrade)", key="btn_upgrade"):
        payload = {"agent_id": u_agent}
        res = requests.post(f"{API_URL}/intent/upgrade", json=payload, headers=HEADERS)
        st.code(res.text)

with col5:
    st.subheader("⚡ SLA ve İtibar Motoru")
    resolve_id = st.number_input("Sözleşme ID", min_value=1, step=1, key="r_id")
    resolve_status = st.selectbox("Teslimat Sonucu", options=[1, 0], format_func=lambda x: "BAŞARILI (+0.01 Rs)" if x == 1 else "SLA İHLALİ (-0.05 Rs)", key="r_status")
    
    if st.button("Sözleşmeyi Kapat", key="btn_resolve"):
        res = requests.post(f"{API_URL}/contract/resolve/{resolve_id}", json={"status": resolve_status}, headers=HEADERS)
        st.code(res.text)

st.markdown("---")

# --- 3. V10.1 MACRO-ECONOMY & INDUSTRIAL TELEMETRY ---
if st.button("Senkronize Et (Endüstriyel Telemetri)", type="primary"):
    try:
        response = requests.get(f"{API_URL}/ledger", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            
            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric("Merkez Bankası Kasası (USD)", f"${data.get('master_wallet_balance', 0):.4f}")
            mcol2.metric("Aktif Şebeke/Talep Düğümleri", data.get('active_orphans', {}).get('buyers', 0))
            mcol3.metric("Bekleyen Arz/Filo Düğümleri", data.get('active_orphans', {}).get('sellers', 0))
            
            st.markdown("---")
            
            top_agents = data.get("top_agents", [])
            if top_agents:
                st.subheader("🏆 Apex Düğümleri (Endüstriyel Hakimiyet)")
                cols = st.columns(len(top_agents))
                for i, agent in enumerate(top_agents):
                    with cols[i]:
                        tier_str = "⚙️ **TIER 2 (Otonom/Yeni Nesil)**" if agent.get('tier') == 2 else "⚙️ Tier 1 (Geleneksel)"
                        debt_str = f"🩸 Kredi Borcu: **${agent['debt']:.2f}**" if agent['debt'] > 0 else "🟢 Borç: $0.00"
                        inv_str = f"📦 Fiziksel Kapasite: **{agent.get('inventory', 0)} Birim**"
                        
                        st.info(f"**{agent['agent_id']}**\n\n{tier_str}\n\nSermaye: **${agent['balance']:.2f}**\n\n{debt_str}\n\n{inv_str}\n\nSLA İtibarı: {agent['Rs']}")
            
            contracts = data.get("executed_contracts", [])
            if contracts:
                df = pd.DataFrame(contracts)
                st.subheader("Kesinleşen Tedarik Sözleşmeleri (Son 50)")
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Endüstriyel Defter-i Kebir şu an boş.")
                
        elif response.status_code == 403:
            st.error("ERİŞİM REDDEDİLDİ: API Anahtarı geçersiz.")
        else:
            st.error(f"SİSTEM HATASI: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Fiziksel Bağlantı Koptu: {e}")
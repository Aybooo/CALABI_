import requests
import json
import threading

# Matrisin Evrensel Uç Noktası
API_URL = "https://calabi-oo4w.onrender.com/ingest/universal"
API_KEY = "CALABI-SECURE-ALPHA-2024"

def fire_tier_3_payload():
    """TİER 3 (KOBİ / Odoo Free): İlkel veri, eksik parametreler, şifre URL'de."""
    print("[TAARRUZ] Tier 3 (KOBİ) Odoo sinyali fırlatılıyor...")
    url_with_key = f"{API_URL}?key={API_KEY}"
    payload = [{
        "client": "ODOO-SME",
        "id": "7781",
        "product": "SOLAR-PANEL",
        "product_qty": "20" # max_price veya max_time yok, matris varsayılanı atamalı
    }]
    res = requests.post(url_with_key, json=payload)
    print(f"[SONUÇ TİER 3]: {res.status_code} - {res.text}\n")

def fire_tier_2_payload():
    """TİER 2 (Orta Ölçekli / Özel API): Karışık değişken isimleri, şifre Header'da."""
    print("[TAARRUZ] Tier 2 (Özel ERP) sinyali fırlatılıyor...")
    headers = {"X-CALABI-KEY": API_KEY, "Content-Type": "application/json"}
    payload = {
        "source": "CUSTOM-ERP",
        "order_id": "99A-X",
        "material": "MWh-ENERGY",
        "volume": 150,
        "budget": 14.5,
        "deadline": 2
    }
    res = requests.post(API_URL, json=payload, headers=headers)
    print(f"[SONUÇ TİER 2]: {res.status_code} - {res.text}\n")

def fire_tier_1_payload():
    """TİER 1 (Küresel SAP/Oracle): Kusursuz veri yapısı, şifre Header'da."""
    print("[TAARRUZ] Tier 1 (SAP Enterprise) sinyali fırlatılıyor...")
    headers = {"X-CALABI-KEY": API_KEY, "Content-Type": "application/json"}
    payload = {
        "origin": "SAP-GLOBAL",
        "uuid": "SAP-0000-1111",
        "item": "MWh-ENERGY",
        "quantity": 500,
        "max_price": 16.0,
        "time": 10
    }
    res = requests.post(API_URL, json=payload, headers=headers)
    print(f"[SONUÇ TİER 1]: {res.status_code} - {res.text}\n")

if __name__ == "__main__":
    print("--- EVRENSEL VERİ YUTMA (UNIVERSAL INGESTION) STRES TESTİ ---\n")
    
    # Üç farklı kurumsal sistem matrise aynı anda (Multi-threading) saldırıyor
    t1 = threading.Thread(target=fire_tier_3_payload)
    t2 = threading.Thread(target=fire_tier_2_payload)
    t3 = threading.Thread(target=fire_tier_1_payload)
    
    t1.start()
    t2.start()
    t3.start()
    
    t1.join()
    t2.join()
    t3.join()
    
    print("--- TAARRUZ TAMAMLANDI. DEFTER-İ KEBİR'İ KONTROL EDİN. ---")
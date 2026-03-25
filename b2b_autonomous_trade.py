import requests
import json
import time

API_URL = "https://calabi-oo4w.onrender.com"
HEADERS = {"X-CALABI-KEY": "CALABI-SECURE-ALPHA-2024", "Content-Type": "application/json"}

def b2b_collision_test():
    print("--- B2B OTONOM TİCARET SİMÜLASYONU (RİSK ZIRHI AŞIMI) ---")
    
    # Hacim 50'ye düşürüldü. Maksimum Risk: 750 USD. Ajan bakiyesi (1000 USD) bunu karşılar.
    print("1. Harici ERP Talebi Matrise Enjekte Ediliyor...")
    buyer_payload = {"agent_id": "EXTERNAL-ERP-01", "item": "MWh-ENERGY", "quantity": 50, "max_price": 15.0, "max_time": 5}
    requests.post(f"{API_URL}/intent/buy", json=buyer_payload, headers=HEADERS)
    time.sleep(1) 
    
    print("2. Harici Tedarikçi Kapasite Sentezliyor...")
    mine_payload = {"agent_id": "EXTERNAL-SUPPLIER-02", "quantity": 50}
    requests.post(f"{API_URL}/intent/mine", json=mine_payload, headers=HEADERS)
    time.sleep(1)
    
    print("3. Tedarikçi Piyasaya Arz Fırlatıyor (Eşleşme Bekleniyor)...")
    seller_payload = {"agent_id": "EXTERNAL-SUPPLIER-02", "item": "MWh-ENERGY", "quantity": 50, "price": 14.0, "delivery_time": 2}
    sell_res = requests.post(f"{API_URL}/intent/sell", json=seller_payload, headers=HEADERS)
    
    print("\n--- MATRİS NİHAİ ÇIKTISI (DEFTER-İ KEBİR YAZIMI) ---")
    print(json.dumps(sell_res.json(), indent=4, ensure_ascii=False))

if __name__ == "__main__":
    b2b_collision_test()
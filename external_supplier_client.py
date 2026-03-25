import requests
import json
import time

API_URL = "https://calabi-oo4w.onrender.com"
HEADERS = {
    "X-CALABI-KEY": "CALABI-SECURE-ALPHA-2024",
    "Content-Type": "application/json"
}

def supplier_integration_test():
    print("--- HARİCİ TEDARİKÇİ SİSTEMİ BAŞLATILDI ---")
    agent_id = "EXTERNAL-SUPPLIER-02"
    
    # FAZ 1: Üretim (Madencilik) - Termodinamik Kıtlık Yasasına Uyum
    print("1. Kapasite Sentezi (Üretim) Vektörü Fırlatılıyor...")
    mine_payload = {"agent_id": agent_id, "quantity": 100}
    mine_res = requests.post(f"{API_URL}/intent/mine", json=mine_payload, headers=HEADERS)
    
    if mine_res.status_code != 200:
        print(f"ÜRETİM REDDEDİLDİ: {mine_res.text}")
        return
        
    print(f"ÜRETİM ONAYLANDI: Ajan 100 birim fiziksel envanter kazandı. (Durum: {mine_res.json().get('status')})")
    time.sleep(1) # Matrisin işlemi sindirmesi için mikrosaniye bekleme
    
    # FAZ 2: Satış (Arz) - Havada bekleyen harici ERP talebine (EXTERNAL-ERP-01) saldırı
    print("\n2. Piyasaya Arz (Satış) Vektörü Fırlatılıyor...")
    sell_payload = {
        "agent_id": agent_id,
        "item": "MWh-ENERGY",
        "quantity": 100,
        "price": 14.0,  # ERP'nin max 15.0 limitinin altında (Rekabetçi fiyat)
        "delivery_time": 2 # ERP'nin max 5 limitinin altında (Hızlı teslimat)
    }
    
    sell_res = requests.post(f"{API_URL}/intent/sell", json=sell_payload, headers=HEADERS)
    
    print(f"\nHTTP Durum Kodu: {sell_res.status_code}")
    if sell_res.status_code == 200:
        print("MUTLAK BAŞARI: İki bağımsız dış yazılım, CALABI matrisi üzerinde otonom olarak eşleşti ve sözleşme imzaladı.")
        print("Matrisin Nihai Çıktısı:")
        print(json.dumps(sell_res.json(), indent=4, ensure_ascii=False))
    else:
        print(f"REDDEDİLDİ: Hata Detayı: {sell_res.text}")

if __name__ == "__main__":
    supplier_integration_test()
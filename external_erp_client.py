import requests
import json

# Dış yazılımın bağlanacağı hedef matris ve güvenlik anahtarı
API_URL = "https://calabi-oo4w.onrender.com"
HEADERS = {
    "X-CALABI-KEY": "CALABI-SECURE-ALPHA-2024",
    "Content-Type": "application/json"
}

def erp_integration_test():
    print("--- HARİCİ ERP SİSTEMİ BAŞLATILDI ---")
    print("1. CALABI Matrisine Dışarıdan Bağlantı Kuruluyor...\n")
    
    # Dış yazılımın matrise fırlattığı veri paketi (Payload)
    external_payload = {
        "agent_id": "EXTERNAL-ERP-01",
        "item": "MWh-ENERGY",
        "quantity": 100,
        "max_price": 15.0,
        "max_time": 5
    }
    
    # Dış yazılımın API'ye HTTP POST isteği atması
    try:
        response = requests.post(f"{API_URL}/intent/buy", json=external_payload, headers=HEADERS)
        
        print(f"HTTP Durum Kodu: {response.status_code}")
        
        if response.status_code == 200:
            print("BAŞARILI: Dış yazılım, otonom matris ile entegre oldu ve işlemi gerçekleştirdi.")
            print("Matrisin Çıktısı:")
            print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        else:
            print("REDDEDİLDİ: Matris dış yazılımın talebini engelledi.")
            print(f"Hata Detayı: {response.text}")
            
    except Exception as e:
        print(f"KRİTİK HATA: API'ye ulaşılamadı. {e}")

if __name__ == "__main__":
    erp_integration_test()
import requests
import random
import time

def calculate_algorithmic_bid(base_budget, urgency_factor):
    """
    Dinamik Alış Fiyatı Algoritması (HFT Modeli)
    Aciliyet arttıkça, ajan maksimum bütçeye daha çok yaklaşır.
    """
    market_volatility = random.uniform(0.9, 1.05) # Piyasa dalgalanma simülasyonu
    calculated_price = base_budget * urgency_factor * market_volatility
    return round(calculated_price, 2)

# Fabrikanın Anlık Durum Verileri
maksimum_butce = 12.0
aciliyet_katsayisi = 0.85 # 1.0 = Fabrika durmak üzere (Paniğe yakın)

# Algoritmik Karar
ai_price = calculate_algorithmic_bid(maksimum_butce, aciliyet_katsayisi)
ai_quantity = 50

intent = {
    "agent_id": "ALICI_FABRIKA_ALGO_01",
    "item": "X_SENSOR",
    "price": ai_price,
    "quantity": ai_quantity
}

url = "http://127.0.0.1:8000/intent/buy"
print(f"[ALICI AJAN] Algoritmik Fiyat Hesaplandı: ${ai_price}")
print(f"[ALICI AJAN] Piyasaya niyet iletiliyor: {ai_quantity} adet")

try:
    response = requests.post(url, json=intent)
    print(f"[ALICI AJAN] Ağ Yanıtı: {response.json()}")
except Exception as e:
    print("[SİSTEM HATASI] Otoyola bağlanılamadı.")
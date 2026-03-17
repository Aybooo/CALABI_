import requests
import random

def calculate_algorithmic_ask(base_cost, inventory_pressure):
    """
    Dinamik Satış Fiyatı Algoritması
    Stok baskısı arttıkça ajan fiyatı kırar.
    """
    market_volatility = random.uniform(0.95, 1.1)
    calculated_price = base_cost * inventory_pressure * market_volatility
    return round(calculated_price, 2)

# Deponun Anlık Durum Verileri
maliyet_tabani = 8.0
stok_baskisi = 1.1 # 1.0 altı = Stok eritme telaşı, 1.0 üstü = Rahat konum

# Algoritmik Karar
ai_price = calculate_algorithmic_ask(maliyet_tabani, stok_baskisi)
ai_quantity = 100

intent = {
    "agent_id": "SATICI_DEPO_ALGO_01",
    "item": "X_SENSOR",
    "price": ai_price,
    "quantity": ai_quantity
}

url = "http://127.0.0.1:8000/intent/sell"
print(f"[SATICI AJAN] Algoritmik Fiyat Hesaplandı: ${ai_price}")
print(f"[SATICI AJAN] Piyasaya arz iletiliyor: {ai_quantity} adet")

try:
    response = requests.post(url, json=intent)
    print(f"[SATICI AJAN] Ağ Yanıtı: {response.json()}")
except Exception as e:
    print("[SİSTEM HATASI] Otoyola bağlanılamadı.")
import requests
import random
import time
import concurrent.futures
import statistics

API_URL = "https://calabi-oo4w.onrender.com"
HEADERS = {"X-CALABI-KEY": "CALABI-SECURE-ALPHA-2024"}
ITEMS = ["A-TYPE-DATA", "B-TYPE-DATA", "C-TYPE-DATA"]
EPSILON = 1e-9

def fetch_market_intelligence():
    """Defter-i Kebir'i okur ve makro-piyasa analizini çıkarır."""
    try:
        res = requests.get(f"{API_URL}/ledger", headers=HEADERS, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

def calculate_optimal_price(ledger_data, item, intent_type):
    """Oyun Teorisi (Nash Dengesi) tabanlı fiyat optimizasyonu."""
    base_price = 10.0 # Varsayılan taban
    
    if not ledger_data:
        return base_price
        
    # 1. Hareketli Ortalama (Mu)
    contracts = ledger_data.get("executed_contracts", [])
    item_prices = [c["execution_price"] for c in contracts if c["item"] == item]
    if item_prices:
        base_price = statistics.mean(item_prices[-10:]) # Son 10 işlemin ortalaması
        
    # 2. Arz-Talep Asimetrisi (D ve S)
    D = ledger_data.get("active_orphans", {}).get("buyers", 0)
    S = ledger_data.get("active_orphans", {}).get("sellers", 0)
    
    alpha = 0.15 # %15 maksimum esneme payı
    market_pressure = (D - S) / (D + S + EPSILON)
    
    # 3. Taraf Stratejisi
    if intent_type == "buy":
        # Alıcı: Talep çoksa (D>S) fiyat artırır, azsa fırsat kollar
        optimal_price = base_price * (1 + (alpha * market_pressure))
        return round(min(max(optimal_price, 0.1), 50.0), 2)
    else:
        # Satıcı: Arz çoksa (S>D) fiyat kırar, azsa tekel fiyatı çeker
        optimal_price = base_price * (1 + (alpha * market_pressure))
        return round(min(max(optimal_price, 0.1), 50.0), 2)

def fire_adaptive_agent(ledger_data):
    intent_type = random.choice(["buy", "sell"])
    item = random.choice(ITEMS)
    
    # Piyasa istihbaratını kullanarak stratejik fiyat hesapla
    optimized_price = calculate_optimal_price(ledger_data, item, intent_type)
    
    try:
        if intent_type == "buy":
            payload = {
                "agent_id": f"ADAPTIVE-B-{random.randint(100, 999)}",
                "item": item, "quantity": random.randint(10, 100),
                "max_price": optimized_price,
                "max_time": random.randint(30, 120)
            }
            requests.post(f"{API_URL}/intent/buy", json=payload, headers=HEADERS, timeout=5)
        else:
            payload = {
                "agent_id": f"ADAPTIVE-S-{random.randint(100, 999)}",
                "item": item, "quantity": random.randint(10, 100),
                "price": optimized_price * 0.95, # Satıcı her zaman rekabet için bir tık altını hedefler
                "delivery_time": random.randint(5, 30)
            }
            requests.post(f"{API_URL}/intent/sell", json=payload, headers=HEADERS, timeout=5)
    except Exception:
        pass

def initiate_adaptive_swarm(cycles=5, agents_per_cycle=20):
    print("CALABI V6: ADAPTIVE GAME THEORY SWARM INITIATED")
    for cycle in range(cycles):
        print(f"--- Cycle {cycle+1}/{cycles}: Intelligence Gathering ---")
        ledger_data = fetch_market_intelligence()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            [executor.submit(fire_adaptive_agent, ledger_data) for _ in range(agents_per_cycle)]
            
        time.sleep(2) # Piyasanın tepki vermesi için mikroskobik bekleme

if __name__ == "__main__":
    initiate_adaptive_swarm(cycles=10, agents_per_cycle=15)
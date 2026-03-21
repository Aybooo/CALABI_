import requests
import random
import time
import concurrent.futures

API_URL = "https://calabi-oo4w.onrender.com"
HEADERS = {"X-CALABI-KEY": "CALABI-SECURE-ALPHA-2024"}
ITEMS = ["A-TYPE-DATA", "B-TYPE-DATA"]

BUYERS = [f"V9-BUYER-{i}" for i in range(1, 21)]
SELLERS = [f"V9-SELLER-{i}" for i in range(1, 21)]

def fire_buyer_intent():
    try:
        payload = {
            "agent_id": random.choice(BUYERS),
            "item": random.choice(ITEMS),
            "quantity": random.randint(5, 20),
            "max_price": round(random.uniform(10.0, 25.0), 2),
            "max_time": random.randint(30, 60)
        }
        requests.post(f"{API_URL}/intent/buy", json=payload, headers=HEADERS, timeout=5)
    except:
        pass

def fire_seller_mining_and_intent():
    seller_id = random.choice(SELLERS)
    item = random.choice(ITEMS)
    qty = random.randint(10, 30)
    
    try:
        # AŞAMA 1: Sentez (Madencilik) - Sermaye Yakımı
        mine_payload = {"agent_id": seller_id, "quantity": qty}
        mine_res = requests.post(f"{API_URL}/intent/mine", json=mine_payload, headers=HEADERS, timeout=5)
        
        if mine_res.status_code == 200:
            # AŞAMA 2: Piyasaya Sürme (Satış)
            # Maliyet birim başına 2.0$. Satıcı kâr etmek için fiyatı yüksek tutar.
            sell_payload = {
                "agent_id": seller_id,
                "item": item,
                "quantity": qty,
                "price": round(random.uniform(4.0, 15.0), 2), 
                "delivery_time": random.randint(5, 20)
            }
            requests.post(f"{API_URL}/intent/sell", json=sell_payload, headers=HEADERS, timeout=5)
    except:
        pass

def initiate_v9_swarm(cycles=50):
    print(f"CALABI V9: MINER SWARM ECONOMIC TEST INITIATED")
    print("Executing sequential Mining, Selling, and Buying vectors...")
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for _ in range(cycles):
            # Eşzamanlı olarak hem madenci/satıcıları hem de alıcıları fırlat
            futures = []
            for _ in range(3):  # Her döngüde 3 Satıcı atağı
                futures.append(executor.submit(fire_seller_mining_and_intent))
            for _ in range(5):  # Her döngüde 5 Alıcı atağı (Talep arzdan yüksek)
                futures.append(executor.submit(fire_buyer_intent))
            
            concurrent.futures.wait(futures)
            
    print(f"V9 WARFARE CONCLUDED IN {time.time() - start_time:.2f} SECONDS.")
    print("Sync the Telemetry on Command Center to observe the Supply Chain and Inventory.")

if __name__ == "__main__":
    initiate_v9_swarm(cycles=40)
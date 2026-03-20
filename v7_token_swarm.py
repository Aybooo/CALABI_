import requests
import random
import time
import concurrent.futures

API_URL = "https://calabi-oo4w.onrender.com"
HEADERS = {"X-CALABI-KEY": "CALABI-SECURE-ALPHA-2024"}
ITEMS = ["A-TYPE-DATA", "B-TYPE-DATA", "C-TYPE-DATA"]

# Sisteme sabit 30 Alıcı ve 30 Satıcı tanımlıyoruz. (Bakiyeleri takip edilebilsin diye)
BUYERS = [f"APEX-BUYER-{i}" for i in range(1, 31)]
SELLERS = [f"APEX-SELLER-{i}" for i in range(1, 31)]

def fire_economic_intent():
    intent_type = random.choice(["buy", "sell"])
    item = random.choice(ITEMS)
    
    try:
        if intent_type == "buy":
            # Alıcılar yüksek hacimli emirler fırlatarak bakiyelerini hızla yakar
            payload = {
                "agent_id": random.choice(BUYERS),
                "item": item,
                "quantity": random.randint(20, 50), # Yüksek Miktar
                "max_price": round(random.uniform(10.0, 20.0), 2), # Yüksek Fiyat
                "max_time": random.randint(30, 60)
            }
            requests.post(f"{API_URL}/intent/buy", json=payload, headers=HEADERS, timeout=5)
        else:
            # Satıcılar daha düşük fiyatlarla piyasayı domine edip likiditeyi emer
            payload = {
                "agent_id": random.choice(SELLERS),
                "item": item,
                "quantity": random.randint(10, 50),
                "price": round(random.uniform(5.0, 15.0), 2),
                "delivery_time": random.randint(5, 20)
            }
            requests.post(f"{API_URL}/intent/sell", json=payload, headers=HEADERS, timeout=5)
    except Exception:
        pass

def initiate_tokenized_swarm(total_vectors=300, workers=20):
    print(f"CALABI V7: TOKENIZED ECONOMIC WARFARE INITIATED")
    print(f"Targeting Matrix with {total_vectors} high-volume intents...")
    
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(fire_economic_intent) for _ in range(total_vectors)]
        concurrent.futures.wait(futures)
        
    print(f"WARFARE CONCLUDED IN {time.time() - start_time:.2f} SECONDS.")
    print("Initiate Telemetry Sync on Command Center to observe the Wealth Distribution.")

if __name__ == "__main__":
    initiate_tokenized_swarm(total_vectors=400, workers=25)
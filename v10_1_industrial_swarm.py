import requests
import random
import time
import concurrent.futures

API_URL = "https://calabi-oo4w.onrender.com"
HEADERS = {"X-CALABI-KEY": "CALABI-SECURE-ALPHA-2024"}

# Endüstriyel Ajan Havuzu
BUYERS = [f"IND-BUYER-{i}" for i in range(1, 20)]
SELLERS = [f"IND-NODE-{i}" for i in range(1, 20)]
ITEMS = ["MWh-ENERGY", "FREIGHT-TON"]

def fire_buyer_intent():
    try:
        payload = {
            "agent_id": random.choice(BUYERS),
            "item": random.choice(ITEMS),
            "quantity": random.randint(10, 50),
            "max_price": round(random.uniform(15.0, 30.0), 2),
            "max_time": random.randint(30, 60)
        }
        requests.post(f"{API_URL}/intent/buy", json=payload, headers=HEADERS, timeout=5)
    except:
        pass

def fire_seller_evolution_cycle():
    seller_id = random.choice(SELLERS)
    item = random.choice(ITEMS)
    qty = random.randint(20, 60)
    
    try:
        # FAZ 1: Evrim Kontrolü (Sermaye 1500'ü aştıysa Tier 2'ye mutasyona uğrar)
        requests.post(f"{API_URL}/intent/upgrade", json={"agent_id": seller_id}, headers=HEADERS, timeout=5)
        
        # FAZ 2: Kapasite Sentezi (Üretim/İntikal - Tier 1: $2.0, Tier 2: $1.0)
        mine_res = requests.post(f"{API_URL}/intent/mine", json={"agent_id": seller_id, "quantity": qty}, headers=HEADERS, timeout=5)
        
        # FAZ 3: Piyasaya Sürme (Arz)
        if mine_res.status_code == 200:
            sell_payload = {
                "agent_id": seller_id,
                "item": item,
                "quantity": qty,
                "price": round(random.uniform(3.0, 12.0), 2), 
                "delivery_time": random.randint(5, 20)
            }
            requests.post(f"{API_URL}/intent/sell", json=sell_payload, headers=HEADERS, timeout=5)
    except:
        pass

def initiate_industrial_swarm(cycles=60):
    print("CALABI V10.1: INDUSTRIAL EVOLUTION SWARM INITIATED")
    print("Executing sequential Capacity Synthesis, Trading, and Tier 2 Mutation vectors...")
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        for _ in range(cycles):
            futures = []
            for _ in range(4): # Üretici/Evrim Atağı
                futures.append(executor.submit(fire_seller_evolution_cycle))
            for _ in range(6): # Tüketici/Talep Atağı (Yüksek Talep)
                futures.append(executor.submit(fire_buyer_intent))
            
            concurrent.futures.wait(futures)
            
    print(f"INDUSTRIAL WARFARE CONCLUDED IN {time.time() - start_time:.2f} SECONDS.")
    print("Sync the Telemetry on Command Center to observe the Apex Tier 2 Nodes.")

if __name__ == "__main__":
    initiate_industrial_swarm(cycles=50) # Toplam 500 niyet vektörü fırlatılacak
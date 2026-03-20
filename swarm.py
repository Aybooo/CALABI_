import requests
import random
import time
import concurrent.futures
import threading

API_URL = "https://calabi-oo4w.onrender.com"
HEADERS = {"X-CALABI-KEY": "CALABI-SECURE-ALPHA-2024"}
ITEMS = ["A-TYPE-DATA", "B-TYPE-DATA", "C-TYPE-DATA"]

success_count = 0
fail_count = 0
lock = threading.Lock()

def fire_intent():
    global success_count, fail_count
    intent_type = random.choice(["buy", "sell"])
    item = random.choice(ITEMS)
    
    try:
        if intent_type == "buy":
            payload = {
                "agent_id": f"SWARM-B-{random.randint(1000, 9999)}",
                "item": item,
                "quantity": random.randint(10, 500),
                "max_price": round(random.uniform(5.0, 15.0), 2),
                "max_time": random.randint(10, 120)
            }
            res = requests.post(f"{API_URL}/intent/buy", json=payload, headers=HEADERS, timeout=5)
        else:
            payload = {
                "agent_id": f"SWARM-S-{random.randint(1000, 9999)}",
                "item": item,
                "quantity": random.randint(10, 500),
                "price": round(random.uniform(4.0, 14.0), 2),
                "delivery_time": random.randint(5, 60)
            }
            res = requests.post(f"{API_URL}/intent/sell", json=payload, headers=HEADERS, timeout=5)
            
        with lock:
            if res.status_code == 200:
                success_count += 1
            else:
                fail_count += 1
    except Exception:
        with lock:
            fail_count += 1

def initiate_swarm_attack(total_requests=100, max_workers=20):
    print(f"CALABI SWARM PROTOCOL INITIATED: {total_requests} Vectors / {max_workers} Threads")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fire_intent) for _ in range(total_requests)]
        concurrent.futures.wait(futures)
        
    end_time = time.time()
    print("-" * 40)
    print(f"SWARM EXECUTION COMPLETE: {end_time - start_time:.2f} seconds")
    print(f"SUCCESSFUL INJECTIONS: {success_count}")
    print(f"FAILED INJECTIONS: {fail_count}")
    print("-" * 40)

if __name__ == "__main__":
    initiate_swarm_attack(total_requests=200, max_workers=50)
import requests
import json

API_URL = "https://calabi-oo4w.onrender.com/ledger"
# Kriptografik anahtar URL'de değil, Header (Başlık) zırhının içinde gizleniyor
HEADERS = {"X-CALABI-KEY": "CALABI-SECURE-ALPHA-2024"}

res = requests.get(API_URL, headers=HEADERS)

if res.status_code == 200:
    print("--- DEFTER-İ KEBİR CANLI VERİSİ ---")
    print(json.dumps(res.json(), indent=4, ensure_ascii=False))
else:
    print(f"ERİŞİM REDDEDİLDİ: {res.text}")
import tkinter as tk
from tkinter import messagebox
import requests
import json

API_URL_MINE = "https://calabi-oo4w.onrender.com/intent/mine"
API_URL_SELL = "https://calabi-oo4w.onrender.com/intent/sell"
HEADERS = {"X-CALABI-KEY": "CALABI-SECURE-ALPHA-2024", "Content-Type": "application/json"}
AGENT_ID = "DESKTOP-SUPPLIER-01"

def synthesize_capacity():
    btn_mine.config(text="SENTEZLENİYOR...", state="disabled")
    root.update()
    try:
        payload = {"agent_id": AGENT_ID, "quantity": int(entry_qty.get())}
        res = requests.post(API_URL_MINE, json=payload, headers=HEADERS)
        if res.status_code == 200:
            formatted = json.dumps(res.json(), indent=2, ensure_ascii=False)
            messagebox.showinfo("ÜRETİM ONAYI", f"Kapasite sentezi başarılı. Ajan fiziksel envanter kazandı.\n\n{formatted}")
        else:
            messagebox.showerror("ÜRETİM REDDİ", res.text)
    except Exception as e:
        messagebox.showerror("AĞ ÇÖKÜŞÜ", f"Matris ile iletişim kurulamadı: {e}")
    finally:
        btn_mine.config(text="1. KAPASİTE SENTEZLE (ÜRETİM)", state="normal")

def execute_supply():
    btn_sell.config(text="MATRİSE BAĞLANILIYOR...", state="disabled")
    root.update()
    try:
        payload = {
            "agent_id": AGENT_ID,
            "item": "MWh-ENERGY",
            "quantity": int(entry_qty.get()),
            "price": 14.0, # Alıcının 15.0 limitinin altında
            "delivery_time": 2
        }
        res = requests.post(API_URL_SELL, json=payload, headers=HEADERS)
        if res.status_code == 200:
            formatted = json.dumps(res.json(), indent=2, ensure_ascii=False)
            messagebox.showinfo("MATRİS ONAYI (SATIŞ)", f"Arz piyasaya fırlatıldı ve sözleşme arandı:\n\n{formatted}")
        else:
            messagebox.showerror("MATRİS REDDİ", res.text)
    except Exception as e:
        messagebox.showerror("AĞ ÇÖKÜŞÜ", f"Matris ile iletişim kurulamadı: {e}")
    finally:
        btn_sell.config(text="2. PİYASAYA ARZ FIRLAT (SATIŞ)", state="normal")

# Tedarikçi Görsel Arayüzü (GUI)
root = tk.Tk()
root.title("Bağımsız Tedarikçi İstemcisi (GUI)")
root.geometry("450x350")
root.configure(bg="#0d1117")

tk.Label(root, text="HARİCİ TEDARİKÇİ ENTEGRASYON PANELİ", fg="#58a6ff", bg="#0d1117", font=("Consolas", 12, "bold")).pack(pady=20)
tk.Label(root, text="Üretilecek/Satılacak Hacim:", fg="#c9d1d9", bg="#0d1117", font=("Consolas", 10)).pack()

entry_qty = tk.Entry(root, justify="center", font=("Consolas", 12), bg="#161b22", fg="white", insertbackground="white")
entry_qty.insert(0, "50")
entry_qty.pack(pady=10)

btn_mine = tk.Button(root, text="1. KAPASİTE SENTEZLE (ÜRETİM)", bg="#d29922", fg="white", font=("Consolas", 10, "bold"), command=synthesize_capacity, relief="flat", padx=10, pady=5)
btn_mine.pack(pady=10)

btn_sell = tk.Button(root, text="2. PİYASAYA ARZ FIRLAT (SATIŞ)", bg="#238636", fg="white", font=("Consolas", 10, "bold"), command=execute_supply, relief="flat", padx=10, pady=5)
btn_sell.pack(pady=10)

root.mainloop()
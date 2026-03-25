import tkinter as tk
from tkinter import messagebox
import requests
import json

API_URL = "https://calabi-oo4w.onrender.com/intent/buy"
HEADERS = {"X-CALABI-KEY": "CALABI-SECURE-ALPHA-2024", "Content-Type": "application/json"}

def execute_trade():
    btn_fire.config(text="MATRİSE BAĞLANILIYOR...", state="disabled")
    root.update()
    try:
        payload = {
            "agent_id": "DESKTOP-ERP-CORE",
            "item": "MWh-ENERGY",
            "quantity": int(entry_qty.get()),
            "max_price": 15.0,
            "max_time": 5
        }
        
        # Dış yazılım matrisin API'sine saldırır
        response = requests.post(API_URL, json=payload, headers=HEADERS)
        
        if response.status_code == 200:
            formatted_res = json.dumps(response.json(), indent=4, ensure_ascii=False)
            messagebox.showinfo("MATRİS ONAYI (HTTP 200)", f"Niyet başarıyla fırlatıldı ve işlendi:\n\n{formatted_res}")
        else:
            messagebox.showerror("MATRİS REDDİ", f"İşlem Engellendi:\n\n{response.text}")
            
    except Exception as e:
        messagebox.showerror("AĞ ÇÖKÜŞÜ", f"Matris ile iletişim kurulamadı:\n\n{e}")
    finally:
        btn_fire.config(text="🔴 TALEBİ MATRİSE FIRLAT (DIŞ AĞ)", state="normal")

# Kurumsal ERP Görsel Arayüzü (GUI) İnşası
root = tk.Tk()
root.title("Bağımsız ERP İstemcisi (GUI)")
root.geometry("450x250")
root.configure(bg="#0d1117")

tk.Label(root, text="HARİCİ YAZILIM ENTEGRASYON PANELİ", fg="#58a6ff", bg="#0d1117", font=("Consolas", 12, "bold")).pack(pady=20)

tk.Label(root, text="Talep Edilen Kapasite Hacmi (Birim):", fg="#c9d1d9", bg="#0d1117", font=("Consolas", 10)).pack()
entry_qty = tk.Entry(root, justify="center", font=("Consolas", 12), bg="#161b22", fg="white", insertbackground="white")
entry_qty.insert(0, "50")
entry_qty.pack(pady=10)

btn_fire = tk.Button(root, text="🔴 TALEBİ MATRİSE FIRLAT (DIŞ AĞ)", bg="#da3633", fg="white", font=("Consolas", 11, "bold"), command=execute_trade, relief="flat", padx=10, pady=5)
btn_fire.pack(pady=15)

root.mainloop()
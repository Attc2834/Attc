import threading
import time
import requests
import json
import os
import sys

# Test için farklı veritabanı kullan
os.environ['DB_FILE'] = 'test_keys.json'

from server import app

# Sunucuyu ayrı bir thread'de çalıştır
def run_server():
    app.run(port=5001)

def test_system():
    # Eski test veritabanını temizle
    if os.path.exists('test_keys.json'):
        os.remove('test_keys.json')

    # Sunucuyu başlat
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2) # Sunucunun açılmasını bekle

    base_url = "http://127.0.0.1:5001"
    admin_token = "gizli123"

    print("--- TEST BAŞLIYOR ---")

    # 1. Yeni Key Oluştur
    print("\n[TEST 1] Key Oluşturuluyor...")
    resp = requests.get(f"{base_url}/admin/create?days=30&token={admin_token}")
    if resp.status_code == 200:
        key = resp.json()['key']
        print(f"✅ Key Oluşturuldu: {key}")
    else:
        print(f"❌ Key Oluşturma Başarısız: {resp.text}")
        sys.exit(1)

    # 2. Doğru HWID ile İlk Giriş
    print("\n[TEST 2] İlk Giriş (Kilitlenme)...")
    hwid1 = "device_123"
    resp = requests.post(f"{base_url}/api/login", json={"key": key, "hwid": hwid1})
    if resp.status_code == 200:
        print("✅ İlk Giriş Başarılı.")
    else:
        print(f"❌ İlk Giriş Başarısız: {resp.text}")
        sys.exit(1)

    # 3. Aynı HWID ile İkinci Giriş
    print("\n[TEST 3] Aynı Cihazdan Tekrar Giriş...")
    resp = requests.post(f"{base_url}/api/login", json={"key": key, "hwid": hwid1})
    if resp.status_code == 200:
        print("✅ Tekrar Giriş Başarılı.")
    else:
        print(f"❌ Tekrar Giriş Başarısız: {resp.text}")
        sys.exit(1)

    # 4. Farklı HWID ile Giriş (Reddedilmeli)
    print("\n[TEST 4] Farklı Cihazdan Giriş Denemesi...")
    hwid2 = "device_999"
    resp = requests.post(f"{base_url}/api/login", json={"key": key, "hwid": hwid2})
    if resp.status_code == 403:
        print("✅ Başarıyla Reddedildi (Beklenen Davranış).")
    else:
        print(f"❌ HATA: Erişim verilmemeliydi! Kod: {resp.status_code}")
        sys.exit(1)

    # 5. Süresi Dolmuş Key Testi
    print("\n[TEST 5] Süresi Dolmuş Key Testi...")
    resp = requests.get(f"{base_url}/admin/create?days=-1&token={admin_token}") # Geçmiş tarih
    expired_key = resp.json()['key']

    resp = requests.post(f"{base_url}/api/login", json={"key": expired_key, "hwid": hwid1})
    if resp.status_code == 403:
        print("✅ Süre Kontrolü Başarılı.")
    else:
        print(f"❌ HATA: Süresi dolmuş key kabul edildi veya yanlış hata! {resp.text}")
        sys.exit(1)

    # Temizlik
    if os.path.exists('test_keys.json'):
        os.remove('test_keys.json')

    print("\n--------------------------")
    print("🎉 TÜM TESTLER BAŞARIYLA GEÇTİ!")
    print("--------------------------")

if __name__ == "__main__":
    test_system()

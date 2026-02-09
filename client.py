import requests
import os
import uuid
import json
import sys
import time

CONFIG_FILE = 'client_config.json'
HWID_FILE = '.hwid'

def get_hwid():
    """
    Cihaz için benzersiz bir kimlik (HWID) döndürür.
    Eğer daha önce oluşturulmuşsa onu okur, yoksa yeni üretip kaydeder.
    """
    if os.path.exists(HWID_FILE):
        with open(HWID_FILE, 'r') as f:
            hwid = f.read().strip()
            if hwid:
                return hwid

    # Yeni HWID üret
    new_hwid = str(uuid.uuid4())
    with open(HWID_FILE, 'w') as f:
        f.write(new_hwid)
    return new_hwid

def get_server_url():
    """
    Sunucu URL'sini config dosyasından okur veya kullanıcıdan ister.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                if 'server_url' in config:
                    return config['server_url']
        except:
            pass

    print("--- İLK KURULUM ---")
    print("Lütfen bilgisayarınızdaki sunucunun adresini girin.")
    print("Örnek: http://192.168.1.35:5000 veya https://xxxx.ngrok-free.app")
    url = input("Sunucu URL: ").strip()

    # Sonunda / varsa kaldır
    if url.endswith('/'):
        url = url[:-1]

    with open(CONFIG_FILE, 'w') as f:
        json.dump({"server_url": url}, f)

    return url

def login():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("################################")
    print("#      ATTC TERMUX GİRİŞ       #")
    print("################################")

    server_url = get_server_url()
    hwid = get_hwid()

    print(f"\nCihaz ID (HWID): {hwid}")
    key = input("Lütfen Key Giriniz: ").strip()

    if not key:
        print("Hata: Key boş olamaz!")
        return False

    print("\nSunucuya bağlanılıyor...")

    try:
        payload = {"key": key, "hwid": hwid}
        response = requests.post(f"{server_url}/api/login", json=payload, timeout=10)

        if response.status_code == 200:
            data = response.json()
            # Başarılı ise logic'e devam et
            # data'nın dict olup olmadığını kontrol et (jsonify döndürüyor)
            if isinstance(data, dict) and data.get("status") == "success":
                print(f"\n✅ BAŞARILI: {data.get('message')}")
                return True
            else:
                 # Status 200 ama içerik hatası olabilir mi? Genelde hayır ama kontrol edelim
                 print(f"\n❌ BAŞARISIZ: {data.get('message', 'Bilinmeyen hata')}")
                 return False

        elif response.status_code == 403: # Yasaklı (Süre dolmuş veya Yanlış HWID)
            print(f"\n⛔ ERİŞİM REDDEDİLDİ: {response.json().get('message')}")
            return False

        elif response.status_code == 401: # Geçersiz Key
             print(f"\n❌ GEÇERSİZ KEY: {response.json().get('message')}")
             return False

        else:
            print(f"\n⚠️ Sunucu Hatası: Kod {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("\n⚠️ BAĞLANTI HATASI: Sunucuya ulaşılamadı!")
        print("Lütfen URL'yi ve internet bağlantınızı kontrol edin.")
        # Config hatalı olabilir, silmeyi önerelim
        ask = input("Kayıtlı URL hatalı olabilir. Ayarları sıfırlamak ister misiniz? (e/h): ")
        if ask.lower() == 'e':
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
            print("Ayarlar sıfırlandı. Tekrar başlatın.")
        return False

    except Exception as e:
        print(f"\n⚠️ Beklenmeyen Hata: {e}")
        return False

def main_program():
    print("\n--- HOŞGELDİNİZ ---")
    print("Program başarıyla başlatıldı.")
    print("Burada asıl kodlarınız çalışacak...")
    # Örnek bekleme
    time.sleep(2)

if __name__ == "__main__":
    if login():
        main_program()
    else:
        print("\nProgram sonlandırılıyor...")

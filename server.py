from flask import Flask, request, jsonify
import json
import os
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)

# Veritabanı dosyasını çevre değişkeninden al veya varsayılanı kullan
DB_FILE = os.getenv('DB_FILE', 'keys.json')

# Basit güvenlik için Admin Token (Bunu değiştirebilirsiniz)
ADMIN_TOKEN = "gizli123"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    return "ATTC Key Server Çalışıyor!"

@app.route('/admin/create', methods=['GET'])
def create_key():
    """
    Yeni bir Key oluşturur.
    Örnek Kullanım: /admin/create?days=60&token=gizli123
    Varsayılan süre: 60 gün (2 ay).
    """
    token = request.args.get('token')
    if token != ADMIN_TOKEN:
        return jsonify({"status": "error", "message": "Yetkisiz Erişim! Token yanlış."}), 403

    days = request.args.get('days', default=60, type=int)

    # Benzersiz Key Üret (UUID4'ün ilk 8 hanesi yeterli olur, daha uzun isterseniz değiştirilebilir)
    new_key = str(uuid.uuid4()).split('-')[0].upper()

    expiry_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

    db = load_db()
    db[new_key] = {
        "hwid": None,  # İlk kullanımda dolacak
        "expiry": expiry_date,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_db(db)

    return jsonify({
        "status": "success",
        "key": new_key,
        "expiry": expiry_date,
        "message": "Key başarıyla oluşturuldu."
    })

@app.route('/api/login', methods=['POST'])
def login():
    """
    Key ve HWID kontrolü yapar.
    JSON verisi bekler: {"key": "XXXX", "hwid": "device_id"}
    """
    data = request.json
    if not data or 'key' not in data or 'hwid' not in data:
        return jsonify({"status": "error", "message": "Eksik veri (Key veya HWID yok)."}), 400

    user_key = data['key'].strip()
    user_hwid = data['hwid'].strip()

    db = load_db()

    if user_key not in db:
        return jsonify({"status": "error", "message": "Geçersiz Key!"}), 401

    key_data = db[user_key]

    # 1. Süre Kontrolü
    expiry_dt = datetime.strptime(key_data['expiry'], "%Y-%m-%d %H:%M:%S")
    if datetime.now() > expiry_dt:
        return jsonify({"status": "error", "message": "Key süresi dolmuş!"}), 403

    # 2. HWID Kontrolü
    if key_data['hwid'] is None:
        # İlk giriş -> HWID'yi kaydet
        key_data['hwid'] = user_hwid
        key_data['first_use'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db[user_key] = key_data
        save_db(db)
        return jsonify({"status": "success", "message": "Key aktif edildi ve bu cihaza kilitlendi."})

    elif key_data['hwid'] == user_hwid:
        # HWID Eşleşiyor -> Başarılı
        return jsonify({"status": "success", "message": "Giriş Başarılı."})

    else:
        # HWID Eşleşmiyor -> Başarısız
        return jsonify({"status": "error", "message": "Bu Key başka bir cihazda kullanılıyor!"}), 403

if __name__ == '__main__':
    # Bilgisayarınızda yerel ağda da erişilebilsin diye 0.0.0.0 dinler.
    app.run(host='0.0.0.0', port=5000)

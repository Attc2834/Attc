# ATTC Key Sistemi Kurulum Kılavuzu

Bu proje, kendi bilgisayarınızı bir lisans sunucusu (Server) olarak kullanmanızı ve Termux üzerinden çalışan programı (Client) bu sunucu üzerinden doğrulamanızı sağlar.

## 1. Bilgisayar (Sunucu) Kurulumu

Bu adımlar bilgisayarınızda yapılacaktır.

### A. Python ve Gerekli Kütüphaneler
1. Bilgisayarınızda Python yüklü olduğundan emin olun. (https://www.python.org/downloads/)
2. Komut satırını (CMD veya PowerShell) açın ve gerekli kütüphaneleri yükleyin:
   ```bash
   pip install flask requests
   ```

### B. Sunucuyu Başlatma
1. `server.py` dosyasının olduğu klasörde terminali açın.
2. Sunucuyu başlatın:
   ```bash
   python server.py
   ```
3. Ekranda `Running on http://0.0.0.0:5000` yazısını göreceksiniz. Şu an sunucu yerel ağda çalışıyor.

### C. İnternete Açma (Ngrok ile)
Termux'un (mobil veri kullanırken bile) bilgisayarınıza ulaşabilmesi için `ngrok` kullanacağız.

1. [ngrok.com](https://ngrok.com) adresinden üye olun ve programı indirin.
2. Ngrok kurulumunu tamamlayın (token işlemini yapın).
3. Yeni bir terminal penceresi açın ve şu komutu girin:
   ```bash
   ngrok http 5000
   ```
4. Ekranda `Forwarding` kısmında şuna benzer bir adres göreceksiniz:
   `https://a1b2-c3d4.ngrok-free.app` -> `http://localhost:5000`

   **Bu `https://...` ile başlayan adres sizin Sunucu URL'nizdir.** Bunu bir yere not edin.

---

## 2. Key (Anahtar) Oluşturma

Sunucu çalışırken, internet tarayıcınızdan yeni key üretebilirsiniz. Güvenlik için `token` kullanılması gerekir. `server.py` içinde `ADMIN_TOKEN` değişkenini bulup şifrenizi değiştirebilirsiniz (Varsayılan: `gizli123`).

- **Varsayılan (60 Günlük) Key Üretmek için:**
  Tarayıcıda şu adrese gidin: `http://localhost:5000/admin/create?token=gizli123`

- **Özel Süreli (Örn: 30 Gün) Key Üretmek için:**
  `http://localhost:5000/admin/create?days=30&token=gizli123`

Ekrana gelen `key` değerini (Örn: `A1B2C3D4`) kopyalayın ve kullanıcıya verin.

---

## 3. Termux (İstemci) Kurulumu

Bu adımlar telefonda (Termux) yapılacaktır.

1. Termux'u açın ve Python yükleyin:
   ```bash
   pkg install python
   pip install requests
   ```
2. `client.py` dosyasını telefonunuza atın (veya kodu kopyalayıp yapıştırın).
3. Programı çalıştırın:
   ```bash
   python client.py
   ```
4. **İlk Açılış:**
   Program size "Sunucu URL" soracaktır. Ngrok'tan aldığınız adresi girin.
   Örnek: `https://a1b2-c3d4.ngrok-free.app` (Sonunda `/` olmamasına dikkat edin).
5. **Giriş:**
   Sizden Key isteyecektir. Bilgisayarda ürettiğiniz Key'i girin.
6. **Sonuç:**
   - Eğer key doğruysa ve süresi dolmamışsa giriş başarılı olur.
   - İlk giren cihazın ID'si (HWID) sunucuya kaydedilir.
   - Başka bir cihaz aynı key ile girmeye çalışırsa reddedilir.

---

## Önemli Notlar

- **HWID (Cihaz Kilidi):** Sistem, Termux'a özgü bir kurulum kimliği (Installation ID) üretir ve `.hwid` dosyasına kaydeder. Programı silip tekrar yüklerseniz veya `.hwid` dosyasını silerseniz ID değişebilir ve eski key çalışmayabilir.
- **Sunucu Açık Kalmalı:** Bilgisayarınızdaki `server.py` ve `ngrok` penceresi açık olduğu sürece sistem çalışır. Bilgisayarı kapatırsanız Termux bağlanamaz.
- **Ngrok Adresi Değişebilir:** Ngrok ücretsiz sürümü her kapatıp açtığınızda farklı bir URL verebilir. Bu durumda Termux'ta `client_config.json` dosyasını silip yeni adresi girmeniz gerekir.
- **Veritabanı:** Kayıtlı keyler `keys.json` dosyasında tutulur. Bu dosyayı silerseniz tüm lisanslar gider.

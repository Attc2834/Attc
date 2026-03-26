# Attc Jarvis — Termux Kurulum Rehberi

## 1. Gerekli Paketler

```bash
# Termux paketlerini güncelle
pkg update && pkg upgrade -y

# Python ve temel araçlar
pkg install python python-pip git -y

# Ses oynatma için
pkg install mpv -y

# Termux API (bildirim, mikrofon, pano, batarya vs.)
pkg install termux-api -y
```

> **Önemli:** Google Play Store'dan değil, [F-Droid](https://f-droid.org) üzerinden hem **Termux** hem **Termux:API** uygulamasını indirin.

## 2. Python Kütüphaneleri

```bash
cd termux
pip install -r requirements.txt
```

## 3. Termux İzinleri

Termux:API'nin çalışması için Android izinleri gereklidir:

```bash
# Mikrofon izni
termux-microphone-record -f /dev/null -l 1

# Depolama izni (opsiyonel)
termux-setup-storage
```

Ardından Android ayarlarından Termux:API uygulamasına **Mikrofon** izni verin.

## 4. Çalıştırma

```bash
python main.py
```

## 5. Komutlar

| Komut | Açıklama |
|---|---|
| `/help` | Yardım menüsü |
| `/lang tr\|en` | Dil değiştir |
| `/name <isim>` | İsim ayarla |
| `/mode wake\|always` | Dinleme modu |
| `/mic` | Mikrofon aç/kapat |
| `/voice` | Sesli yanıt aç/kapat |
| `/status` | Sistem durumu |
| `/clear` | Sohbeti temizle |
| `/quit` | Çıkış |

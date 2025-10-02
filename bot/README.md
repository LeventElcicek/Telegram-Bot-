# Telegram Quiz Bot

Bu klasör, Expo mobil uygulaması için Telegram bot'unu içerir.

## 📁 Dosyalar

- `leventbot.py` - Ana bot kodu
- `questions.json` - Soru veritabanı
- `start_bot.py` - Bot başlatma scripti (Python)
- `start_bot.bat` - Bot başlatma scripti (Windows)
- `requirements.txt` - Gerekli Python kütüphaneleri
- `name.txt` - Bot adı

## 🚀 Bot'u Başlatma

### Windows için:
1. `start_bot.bat` dosyasına çift tıklayın
2. Veya komut satırında: `python leventbot.py`

### Diğer işletim sistemleri için:
1. Gerekli kütüphaneleri yükleyin: `pip install -r requirements.txt`
2. Bot'u başlatın: `python leventbot.py`

## 📱 Mobil Uygulama Entegrasyonu

Bot aktif olduğunda, mobil uygulamadaki "Bot'u Aktifleştir" butonu Telegram'da bot'u açar.

## ⚙️ Bot Özellikleri

- Bilgi yarışması
- 10 soru limiti
- Puan sistemi
- Zamanlayıcı (25 saniye)
- Ödül sistemi
- Telegram cüzdan entegrasyonu

## 🔧 Gereksinimler

- Python 3.7+
- python-telegram-bot kütüphanesi
- Telegram Bot Token

## 📞 Bot Kullanıcı Adı

Bot'u Telegram'da bulmak için: `@levent_quiz_bot`

## ⚠️ Önemli Notlar

- Bot token'ı `leventbot.py` dosyasında tanımlıdır
- Bot'u çalıştırmadan önce token'ın geçerli olduğundan emin olun
- Bot'u durdurmak için Ctrl+C tuşlarını kullanın 
@echo off
echo 🤖 Telegram Bot Başlatıcı
echo ================================
echo.

REM Gerekli kütüphaneleri kontrol et ve yükle
echo 🔍 Gerekli kütüphaneler kontrol ediliyor...
python -c "import telegram" 2>nul
if errorlevel 1 (
    echo ❌ python-telegram-bot yüklü değil!
    echo 📦 Yükleniyor...
    pip install python-telegram-bot==20.7
    if errorlevel 1 (
        echo ❌ Kütüphane yüklenemedi!
        pause
        exit /b 1
    )
) else (
    echo ✅ python-telegram-bot yüklü
)

echo.
echo 🚀 Bot başlatılıyor...
echo 📱 Bot aktif olduğunda Telegram'da @levent_quiz_bot kullanıcı adıyla bulabilirsiniz.
echo ⏹️  Bot'u durdurmak için Ctrl+C tuşlarına basın.
echo.

REM Bot'u başlat
python leventbot.py

echo.
echo ✅ Bot durduruldu.
pause 
#!/usr/bin/env python3
"""
Telegram Bot Başlatma Scripti
Bu script leventbot.py dosyasını çalıştırarak Telegram bot'unu aktif hale getirir.
"""

import subprocess
import sys
import os
import signal
import time

def start_bot():
    """Bot'u başlatır"""
    try:
        print("🤖 Telegram Bot başlatılıyor...")
        print("📱 Bot aktif olduğunda Telegram'da @levent_quiz_bot kullanıcı adıyla bulabilirsiniz.")
        print("⏹️  Bot'u durdurmak için Ctrl+C tuşlarına basın.")
        print("-" * 50)
        
        # Bot'u başlat
        process = subprocess.Popen([sys.executable, "leventbot.py"], 
                                 cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # Bot çalışırken bekle
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Bot durduruluyor...")
            process.terminate()
            process.wait()
            print("✅ Bot başarıyla durduruldu.")
            
    except FileNotFoundError:
        print("❌ Hata: leventbot.py dosyası bulunamadı!")
        print("📁 Lütfen bu script'in bot klasöründe olduğundan emin olun.")
    except Exception as e:
        print(f"❌ Hata: {e}")

def check_dependencies():
    """Gerekli kütüphanelerin yüklü olup olmadığını kontrol eder"""
    required_packages = ['python-telegram-bot', 'asyncio']
    
    print("🔍 Gerekli kütüphaneler kontrol ediliyor...")
    
    for package in required_packages:
        try:
            if package == 'python-telegram-bot':
                import telegram
            elif package == 'asyncio':
                import asyncio
            print(f"✅ {package} yüklü")
        except ImportError:
            print(f"❌ {package} yüklü değil!")
            print(f"📦 Yüklemek için: pip install {package}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Telegram Bot Başlatıcı")
    print("=" * 30)
    
    # Gerekli kütüphaneleri kontrol et
    if not check_dependencies():
        print("\n❌ Gerekli kütüphaneler eksik. Lütfen yükleyin.")
        sys.exit(1)
    
    # Bot'u başlat
    start_bot() 
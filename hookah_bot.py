# bot.py - С ПРАВИЛЬНЫМ ЗАПУСКОМ FLASK
import os
import json
import logging
import threading
import time
from datetime import datetime
from flask import Flask, jsonify
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("=" * 60)
print("🚀 ЗАПУСК БОТА НА RAILWAY")
print("=" * 60)

# ====== ВЕБ-СЕРВЕР FLASK ======
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Hookah Bot is ALIVE!"

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "bot": "running",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/ping')
def ping():
    return "pong", 200

def run_flask():
    """Запуск Flask с явными параметрами"""
    print("🌐 Запускаю веб-сервер на порту 8080...")
    # Важно: use_reloader=False для Railway
    app.run(
        host='0.0.0.0', 
        port=8080, 
        debug=False, 
        use_reloader=False,
        threaded=True
    )

# ЗАПУСКАЕМ FLASK ПЕРВЫМ И ЖДЕМ
print("1. Запускаю веб-сервер...")
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Даем Flask время на запуск
print("2. Жду запуск веб-сервера...")
time.sleep(3)  # Ждем 3 секунды
print("✅ Веб-сервер запущен!")

# ====== ПРОВЕРКА ПОРТА ======
import socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('127.0.0.1', 8080))
    if result == 0:
        print("✅ Порт 8080 открыт и слушает")
    else:
        print("⚠️  Порт 8080 не отвечает")
    sock.close()
except Exception as e:
    print(f"⚠️  Ошибка проверки порта: {e}")

# ====== КОНФИГУРАЦИЯ БОТА ======
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    print("❌ ОШИБКА: TELEGRAM_TOKEN не найден!")
    print("Добавьте в Railway: Settings → Variables")
    print("Name: TELEGRAM_TOKEN")
    print("Value: ваш_токен")
    exit(1)

print(f"✅ Токен получен: {TOKEN[:10]}...")

DATA_FILE = "user_data.json"

# ... ОСТАЛЬНОЙ ВАШ КОД БОТА ...

def main():
    print("3. Запускаю Telegram бота...")
    
    try:
        telegram_app = Application.builder().token(TOKEN).build()
        telegram_app.add_handler(CommandHandler("start", start))
        telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("=" * 60)
        print("🤖 БОТ УСПЕШНО ЗАПУЩЕН!")
        print("🌐 Веб-сервер: http://localhost:8080")
        print("🔧 Healthcheck: /health")
        print("📱 Telegram: /start")
        print("=" * 60)
        
        telegram_app.run_polling(drop_pending_updates=True, timeout=30)
        
    except Exception as e:
        print(f"❌ Ошибка Telegram бота: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    main()

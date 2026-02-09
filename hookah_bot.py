# hookah_bot.py - ФИНАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ
import os
import sys
import time
import json
import logging
from datetime import datetime

print("=" * 70)
print("🤖 HOOKAH BOT - FINAL VERSION")
print("=" * 70)

# ====== 1. FLASK ДЛЯ HEALTHCHECK (ТОЛЬКО ЕСЛИ НЕ ЗАПУЩЕН) ======
try:
    # Проверяем не запущен ли уже Flask
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8080))
    sock.close()
    
    if result != 0:  # Порт свободен
        from flask import Flask, jsonify
        import threading
        
        app = Flask(__name__)
        
        @app.route('/health')
        def health():
            return jsonify({"status": "healthy"}), 200
        
        @app.route('/')
        def home():
            return "Hookah Bot Running"
        
        def run_flask():
            print("🌐 Starting Flask on port 8080...")
            app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        time.sleep(2)
        print("✅ Flask started for Railway healthcheck")
    else:
        print("✅ Flask already running (port 8080 busy)")
        
except Exception as e:
    print(f"⚠️ Flask issue: {e}")

# ====== 2. ПРОВЕРКА ТОКЕНА ======
print("\n" + "=" * 70)
print("🔑 CHECKING TELEGRAM TOKEN")
print("=" * 70)

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    print("❌ CRITICAL ERROR: TELEGRAM_TOKEN NOT FOUND!")
    print("Please add it in Railway: Settings → Variables")
    print("Name: TELEGRAM_TOKEN")
    print("Value: your_bot_token_from_BotFather")
    print("\nCurrent environment variables:")
    for key in sorted(os.environ.keys()):
        if 'TOKEN' in key or 'SECRET' in key:
            print(f"  {key}: [HIDDEN]")
        else:
            print(f"  {key}: {os.environ[key][:50]}...")
    
    # Flask уже работает для healthcheck, так что не завершаем
    print("\n⏳ Waiting indefinitely... Flask healthcheck is working")
    print("   Add TELEGRAM_TOKEN to start the Telegram bot")
    while True:
        time.sleep(60)  # Ждем вечно
    
print(f"✅ Token found: {TOKEN[:10]}...")
print(f"   Token length: {len(TOKEN)} characters")

# ====== 3. ЗАГРУЗКА TELEGRAM БИБЛИОТЕК ======
print("\n" + "=" * 70)
print("📚 LOADING TELEGRAM LIBRARIES")
print("=" * 70)

try:
    from telegram import Update, ReplyKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    print("✅ Telegram libraries imported")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# ====== 4. ВАШ КОД БОТА (вставьте сюда ваш рабочий код) ======
print("\n" + "=" * 70)
print("⚙️  SETTING UP BOT FUNCTIONS")
print("=" * 70)

# Файл для данных
DATA_FILE = "user_data.json"

def load_data():
    """Загрузить данные"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    """Сохранить данные"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Save error: {e}")

def get_user_data(user_id):
    """Получить данные пользователя"""
    data = load_data()
    return data.get(str(user_id), {"name": "", "tastes": []})

def save_user_data(user_id, user_data):
    """Сохранить данные пользователя"""
    data = load_data()
    data[str(user_id)] = user_data
    save_data(data)

# Обработчики бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    user_id = str(user.id)
    
    user_data = get_user_data(user_id)
    
    if not user_data.get("name"):
        await update.message.reply_text(
            f"Привет, {user.first_name}! 👋\nКак тебя зовут? (Один раз)"
        )
        context.user_data['step'] = 'ask_name'
    else:
        keyboard = [["➕ Новый вкус", "📜 Моя история"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            f"С возвращением, {user_data['name']}! 😊",
            reply_markup=reply_markup
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений"""
    user = update.effective_user
    user_id = str(user.id)
    text = update.message.text
    
    if 'step' in context.user_data and context.user_data['step'] == 'ask_name':
        user_data = {
            "name": text,
            "tastes": [],
            "first_seen": datetime.now().isoformat()
        }
        save_user_data(user_id, user_data)
        
        keyboard = [["➕ Новый вкус", "📜 Моя история"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"Отлично, {text}! 🎉\nЧто хочешь сделать?",
            reply_markup=reply_markup
        )
        context.user_data.clear()
        return
    
    if text == "➕ Новый вкус":
        await update.message.reply_text("Какой вкус кальяна тебе понравился?")
        context.user_data['step'] = 'add_taste'
    elif text == "📜 Моя история":
        user_data = get_user_data(user_id)
        if not user_data.get("tastes"):
            await update.message.reply_text("📭 У тебя пока нет записей.")
        else:
            response = f"📜 Твоя история, {user_data['name']}:\n\n"
            for taste in user_data["tastes"]:
                response += f"📅 {taste['date']}: {taste['flavor']}\n"
            await update.message.reply_text(response)
    elif 'step' in context.user_data and context.user_data['step'] == 'add_taste':
        flavor = text
        date = datetime.now().strftime("%d.%m.%Y")
        
        user_data = get_user_data(user_id)
        user_data["tastes"].append({
            "date": date,
            "flavor": flavor,
            "timestamp": datetime.now().isoformat()
        })
        save_user_data(user_id, user_data)
        
        await update.message.reply_text(f"✅ Записано: {flavor} ({date})")
        context.user_data.clear()
    else:
        await start(update, context)

# ====== 5. ЗАПУСК TELEGRAM БОТА ======
print("\n" + "=" * 70)
print("🚀 STARTING TELEGRAM BOT")
print("=" * 70)

def main():
    print("Initializing Telegram bot...")
    
    try:
        # Создаем приложение
        telegram_app = Application.builder().token(TOKEN).build()
        
        # Добавляем обработчики
        telegram_app.add_handler(CommandHandler("start", start))
        telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("\n" + "=" * 70)
        print("🎉 BOT STARTED SUCCESSFULLY!")
        print("=" * 70)
        print("📱 Open Telegram and write: /start")
        print("🌐 Healthcheck: /health (already working)")
        print(f"⏰ Start time: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 70)
        
        # Запускаем бота
        telegram_app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Telegram bot error: {type(e).__name__}")
        print(f"Message: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # Настройка логирования
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    main()

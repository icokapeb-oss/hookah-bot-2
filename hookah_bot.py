import sys
import time

# Принудительный вывод
sys.stdout.flush()
sys.stderr.flush()

print("=" * 70, flush=True)
print("🚀 БОТ НАЧИНАЕТ РАБОТАТЬ!", flush=True)
print("=" * 70, flush=True)

# Ждем и выводим
time.sleep(1)
print("Жду 1 секунду...", flush=True)
time.sleep(1)
print("Еще 1 секунда...", flush=True)

# ... ваш код дальше
# hookah_bot.py - с Flask для Railway
import os
import threading
import time
from flask import Flask, jsonify
from datetime import datetime

print("=" * 60)
print("🤖 HOOKAH BOT - Railway Version")
print("=" * 60)

# Flask сервер для healthcheck
app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "hookah-bot"}), 200

@app.route('/')
def home():
    return "Hookah Bot is running!"

def run_flask():
    print("Starting Flask on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

# Запускаем Flask
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()
time.sleep(3)
print("✅ Flask started for healthcheck")

# ====== ВАШ ОСНОВНОЙ КОД НИЖЕ ======
# ... весь ваш существующий код hookah_bot.py ...
# bot.py - Railway рабочий вариант
import os
import sys
import json
import logging
import threading
import time
from datetime import datetime

print("=" * 70)
print("🚀 ЗАПУСК БОТА НА RAILWAY - ВЕРСИЯ 2.0")
print("=" * 70)
print(f"Время: {datetime.now()}")
print(f"Python: {sys.version}")
print(f"Директория: {os.getcwd()}")
print("Список файлов:", os.listdir('.'))

# ====== 1. СНАЧАЛА FLASK ======
print("\n" + "=" * 70)
print("1. ЗАПУСКАЮ FLASK ДЛЯ HEALTHCHECK")
print("=" * 70)

try:
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return """
        <html>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🤖 Hookah Taste Bot</h1>
            <p>Status: <span style="color: green;">🟢 RUNNING</span></p>
            <p>Telegram bot for tracking hookah flavors</p>
        </body>
        </html>
        """
    
    @app.route('/health')
    def health():
        return jsonify({
            "status": "healthy",
            "service": "telegram-bot",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0"
        }), 200
    
    @app.route('/ping')
    def ping():
        return "pong", 200
    
    # Функция запуска Flask
    def run_flask():
        print("🌐 Flask запускается на порту 8080...")
        # Важно: use_reloader=False для Railway
        app.run(
            host='0.0.0.0',
            port=8080,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    
    # Запускаем Flask в ОСНОВНОМ потоке и ждем
    print("Запускаю Flask в отдельном потоке...")
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # ЖДЕМ пока Flask запустится
    print("Жду 3 секунды для запуска Flask...")
    time.sleep(3)
    print("✅ Flask должен быть запущен")
    
    # Проверяем порт
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 8080))
        if result == 0:
            print("✅ Порт 8080 открыт - Flask работает!")
        else:
            print("⚠️  Порт 8080 не отвечает")
        sock.close()
    except Exception as e:
        print(f"⚠️  Ошибка проверки порта: {e}")
    
except Exception as e:
    print(f"❌ Ошибка Flask: {e}")
    import traceback
    traceback.print_exc()

# ====== 2. ПРОВЕРКА ТОКЕНА ======
print("\n" + "=" * 70)
print("2. ПРОВЕРКА ТОКЕНА TELEGRAM")
print("=" * 70)

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    print("❌ КРИТИЧЕСКАЯ ОШИБКА: TELEGRAM_TOKEN не найден!")
    print("Переменные окружения:", list(os.environ.keys()))
    print("\n💡 РЕШЕНИЕ:")
    print("1. В Railway откройте Settings → Variables")
    print("2. Добавьте переменную: TELEGRAM_TOKEN = ваш_токен")
    print("3. Перезапустите проект")
    
    # Ждем чтобы увидеть ошибку в логах
    print("\n⏳ Жду 60 секунд перед завершением...")
    time.sleep(60)
    sys.exit(1)

print(f"✅ Токен найден: {TOKEN[:10]}...")
print(f"Длина токена: {len(TOKEN)} символов")

# ====== 3. ЗАГРУЗКА БИБЛИОТЕК TELEGRAM ======
print("\n" + "=" * 70)
print("3. ЗАГРУЗКА TELEGRAM БИБЛИОТЕК")
print("=" * 70)

try:
    from telegram import Update, ReplyKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    print("✅ Telegram библиотеки загружены")
except ImportError as e:
    print(f"❌ Ошибка импорта Telegram: {e}")
    print("Пытаюсь установить...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot==20.7"])
    from telegram import Update, ReplyKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ====== 4. ВАШИ ФУНКЦИИ БОТА ======
print("\n" + "=" * 70)
print("4. НАСТРОЙКА БОТА")
print("=" * 70)

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
        print(f"Ошибка сохранения: {e}")

def get_user_data(user_id):
    data = load_data()
    return data.get(str(user_id), {"name": "", "tastes": []})

def save_user_data(user_id, user_data):
    data = load_data()
    data[str(user_id)] = user_data
    save_data(data)

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
print("5. ЗАПУСК TELEGRAM БОТА")
print("=" * 70)

def main():
    print("Создаю Telegram приложение...")
    
    try:
        telegram_app = Application.builder().token(TOKEN).build()
        telegram_app.add_handler(CommandHandler("start", start))
        telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Telegram бот настроен!")
        print("\n" + "=" * 70)
        print("🎉 БОТ УСПЕШНО ЗАПУЩЕН!")
        print("=" * 70)
        print("📱 Напишите в Telegram: /start")
        print("🌐 Healthcheck: /health")
        print("⏰ Время запуска:", datetime.now().strftime("%H:%M:%S"))
        print("=" * 70)
        
        # Запускаем бота
        telegram_app.run_polling(drop_pending_updates=True, timeout=30)
        
    except Exception as e:
        print(f"❌ Ошибка Telegram бота: {type(e).__name__}")
        print(f"Сообщение: {e}")
        import traceback
        traceback.print_exc()
        
        # Ждем чтобы увидеть ошибку
        print("\n⏳ Жду 30 секунд...")
        time.sleep(30)

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    main()



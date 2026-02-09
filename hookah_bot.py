# hookah_bot.py - ВЕРСИЯ ДЛЯ RENDER.COM
import os
import sys
import json
import logging
from datetime import datetime

print("=" * 70)
print("🤖 HOOKAH BOT - RENDER.COM VERSION")
print("=" * 70)

# ====== 1. ПРОВЕРКА ТОКЕНА ======
TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ CRITICAL ERROR: TELEGRAM TOKEN NOT FOUND!")
    print("Please add it on Render.com:")
    print("1. Go to your service → Environment")
    print("2. Add: TELEGRAM_TOKEN = your_token_here")
    print("\n⏳ Bot will exit. Add token and redeploy.")
    sys.exit(1)

print(f"✅ Token found: {TOKEN[:10]}...")

# ====== 2. НАСТРОЙКА ПУТЕЙ ДЛЯ ФАЙЛОВ ======
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "user_data.json")
print(f"📁 Data will be saved to: {DATA_FILE}")

# ====== 3. ИМПОРТ TELEGRAM БИБЛИОТЕК ======
try:
    from telegram import Update, ReplyKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    print("✅ Telegram libraries imported")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# ====== 4. ФУНКЦИИ ДЛЯ РАБОТЫ С ДАННЫМИ ======
def load_data():
    """Загрузить данные"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading data: {e}")
            return {}
    return {}

def save_data(data):
    """Сохранить данные"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Save error: {e}")

def get_user_data(user_id):
    """Получить данные пользователя"""
    data = load_data()
    return data.get(str(user_id), {"name": "", "tastes": []})

def save_user_data(user_id, user_data):
    """Сохранить данные пользователя"""
    data = load_data()
    data[str(user_id)] = user_data
    save_data(data)

# ====== 5. ОБРАБОТЧИКИ БОТА ======
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

# ====== 6. ЗАПУСК БОТА ======
def main():
    print("\n" + "=" * 70)
    print("🚀 STARTING BOT ON RENDER.COM")
    print("=" * 70)
    
    # Настройка логирования
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    try:
        # Создаем приложение
        app = Application.builder().token(TOKEN).build()
        
        # Добавляем обработчики
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Bot initialized successfully!")
        print("📱 Open Telegram and write: /start")
        print(f"⏰ Start time: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 70)
        
        # Запускаем бота
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

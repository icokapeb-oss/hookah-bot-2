# individual_bot.py
# Бот с индивидуальной историей для каждого пользователя

import os
import json
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
TOKEN = "8246009144:AAEUk-fHuPjCnSYoNY3dWCaQSr7fK6pR46c"

# Файл для данных
DATA_FILE = "user_data.json"

def load_data():
    """Загрузить данные всех пользователей"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    """Сохранить данные"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_data(user_id):
    """Получить данные конкретного пользователя"""
    data = load_data()
    return data.get(str(user_id), {"name": "", "tastes": []})

def save_user_data(user_id, user_data):
    """Сохранить данные пользователя"""
    data = load_data()
    data[str(user_id)] = user_data
    save_data(data)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - начало работы"""
    user = update.effective_user
    user_id = str(user.id)

    # Загружаем данные пользователя
    user_data = get_user_data(user_id)

    # Если пользователь новый, спрашиваем имя
    if not user_data.get("name"):
        await update.message.reply_text(
            f"Привет, {user.first_name}! 👋\n"
            "Я бот для записи вкусов кальяна.\n\n"
            "Как тебя зовут? (Это нужно только один раз)"
        )
        context.user_data['step'] = 'ask_name'
    else:
        # Если имя уже есть - показываем меню
        keyboard = [["➕ Новый вкус", "📜 Моя история"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            f"С возвращением, {user_data['name']}! 😊\n\n"
            "Что хочешь сделать?",
            reply_markup=reply_markup
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка всех сообщений"""
    user = update.effective_user
    user_id = str(user.id)
    text = update.message.text

    print(f"Сообщение от {user_id} ({user.first_name}): {text}")

    # Если пользователь отправляет имя (первый раз)
    if 'step' in context.user_data and context.user_data['step'] == 'ask_name':
        # Сохраняем имя пользователя
        user_data = {
            "name": text,
            "tastes": [],
            "first_seen": datetime.now().isoformat()
        }
        save_user_data(user_id, user_data)

        # Показываем меню
        keyboard = [["➕ Новый вкус", "📜 Моя история"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            f"Отлично, {text}! 🎉\n"
            "Теперь я буду запоминать твои вкусы.\n\n"
            "Что хочешь сделать?",
            reply_markup=reply_markup
        )

        context.user_data.clear()
        return

    # Обработка команд из меню
    if text == "➕ Новый вкус":
        await update.message.reply_text("Какой вкус кальяна тебе понравился?")
        context.user_data['step'] = 'add_taste'

    elif text == "📜 Моя история":
        # Показываем историю пользователя
        user_data = get_user_data(user_id)

        if not user_data.get("tastes"):
            keyboard = [["➕ Новый вкус", "📜 Моя история"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await update.message.reply_text(
                f"📭 {user_data.get('name', 'Друг')}, у тебя пока нет записей.\n"
                "Добавь первый вкус!",
                reply_markup=reply_markup
            )
        else:
            # Группируем по датам
            by_date = {}
            for taste in user_data["tastes"]:
                date = taste['date']
                flavor = taste['flavor']
                if date not in by_date:
                    by_date[date] = []
                by_date[date].append(flavor)

            # Формируем ответ
            response = f"📜 Твоя история, {user_data['name']}:\n\n"

            if by_date:
                for date in sorted(by_date.keys(), reverse=True):
                    response += f"📅 {date}:\n"
                    for flavor in by_date[date]:
                        response += f"  • {flavor}\n"
                    response += "\n"

                # Статистика
                total = len(user_data["tastes"])
                unique_dates = len(by_date)
                response += f"📊 Всего записей: {total}\n"
                response += f"📅 Уникальных дат: {unique_dates}"
            else:
                response = "У тебя пока нет записей."

            keyboard = [["➕ Новый вкус", "📜 Моя история"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await update.message.reply_text(response, reply_markup=reply_markup)

    # Обработка добавления вкуса
    elif 'step' in context.user_data and context.user_data['step'] == 'add_taste':
        flavor = text
        date = datetime.now().strftime("%d.%m.%Y")
        time = datetime.now().strftime("%H:%M")

        # Загружаем данные пользователя
        user_data = get_user_data(user_id)

        # Добавляем вкус
        user_data["tastes"].append({
            "date": date,
            "time": time,
            "flavor": flavor,
            "timestamp": datetime.now().isoformat()
        })

        # Сохраняем
        save_user_data(user_id, user_data)

        # Подтверждение
        keyboard = [["➕ Новый вкус", "📜 Моя история"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            f"✅ Записано! ✨\n\n"
            f"💨 Вкус: {flavor}\n"
            f"📅 Дата: {date}\n"
            f"🕒 Время: {time}\n\n"
            f"Твоя коллекция пополнилась! 🎉",
            reply_markup=reply_markup
        )

        context.user_data.clear()

    # Если непонятное сообщение
    else:
        keyboard = [["➕ Новый вкус", "📜 Моя история"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Выбери действие на клавиатуре:",
            reply_markup=reply_markup
        )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stats - статистика пользователя"""
    user_id = str(update.effective_user.id)
    user_data = get_user_data(user_id)

    if not user_data.get("tastes"):
        await update.message.reply_text(
            f"📊 {user_data.get('name', 'Друг')}, у тебя пока нет статистики.\n"
            "Добавь первый вкус!"
        )
        return

    tastes = user_data["tastes"]
    total = len(tastes)

    # Считаем популярные вкусы
    flavor_counts = {}
    for taste in tastes:
        flavor = taste["flavor"]
        flavor_counts[flavor] = flavor_counts.get(flavor, 0) + 1

    # Самый популярный вкус
    if flavor_counts:
        top_flavor = max(flavor_counts.items(), key=lambda x: x[1])

    # Статистика
    stats_text = f"📊 Статистика {user_data['name']}:\n\n"
    stats_text += f"Всего записей: {total}\n"

    if total > 0:
        # Первая запись
        first_date = min(t["date"] for t in tastes)
        stats_text += f"Первая запись: {first_date}\n"

        # Последняя запись
        last_date = max(t["date"] for t in tastes)
        stats_text += f"Последняя запись: {last_date}\n"

        # Популярный вкус
        if flavor_counts:
            stats_text += f"\n🏆 Любимый вкус: {top_flavor[0]} ({top_flavor[1]} раз)\n"

            # Все вкусы
            if len(flavor_counts) > 1:
                stats_text += f"\n🎯 Все твои вкусы:\n"
                for flavor, count in sorted(flavor_counts.items(), key=lambda x: x[1], reverse=True):
                    stats_text += f"  • {flavor}: {count} раз\n"

    await update.message.reply_text(stats_text)

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /clear - очистить историю"""
    user_id = str(update.effective_user.id)

    # Загружаем данные
    user_data = get_user_data(user_id)

    if not user_data.get("tastes"):
        await update.message.reply_text("📭 Твоя история уже пуста.")
        return

    # Сохраняем имя, но очищаем вкусы
    user_data["tastes"] = []
    save_user_data(user_id, user_data)

    await update.message.reply_text(
        "🧹 История очищена!\n"
        "Твое имя сохранено. Можешь начать с чистого листа! ✨"
    )

def main():
    """Запуск бота"""
    print("=" * 50)
    print("🤖 БОТ С ИНДИВИДУАЛЬНОЙ ИСТОРИЕЙ ДЛЯ КАЖДОГО")
    print("=" * 50)

    try:
        # Создаем приложение
        app = Application.builder().token(TOKEN).build()

        # Команды
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("stats", stats_command))
        app.add_handler(CommandHandler("clear", clear_command))

        # Обработка сообщений
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        print("✅ Бот настроен успешно!")
        print("✨ Особенности:")
        print("   • Каждый пользователь видит ТОЛЬКО свою историю")
        print("   • Имя запрашивается один раз")
        print("   • История сохраняется навсегда")
        print("   • Работает на любом устройстве")
        print("\n🚀 Запускаю...")
        print("=" * 50)

        # Запускаем бота
        app.run_polling(drop_pending_updates=True)

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("Проверьте токен и перезапустите.")

if __name__ == '__main__':
    main()
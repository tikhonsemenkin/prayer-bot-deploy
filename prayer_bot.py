import logging
import json
import os
import time
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Замените на свой токен бота
TOKEN = "7773322601:AAHlYp6XhATuhZOFPjOnGfEKv1xftEkSWOI"
DATA_FILE = "prayers.json"

logging.basicConfig(level=logging.INFO)

# Загрузка данных
def load_prayers():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Сохранение данных
def save_prayers(prayers):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(prayers, f, ensure_ascii=False, indent=2)

# Удаление просроченных молитв
def remove_expired_prayers():
    prayers = load_prayers()
    now = datetime.now()
    prayers = [p for p in prayers if datetime.fromisoformat(p["until"]) > now]
    save_prayers(prayers)

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Это молитвенный бот. Используй /add чтобы добавить прошение.")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Использование: /add <дни> <текст>")
        return
    try:
        days = int(context.args[0])
        text = " ".join(context.args[1:])
        until = datetime.now() + timedelta(days=days)
        prayers = load_prayers()
        prayers.append({"text": text, "until": until.isoformat()})
        save_prayers(prayers)
        await update.message.reply_text("Прошение добавлено!")
    except ValueError:
        await update.message.reply_text("Неверный формат. Пример: /add 3 Помолитесь за здоровье мамы")

async def list_prayers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    remove_expired_prayers()
    prayers = load_prayers()
    if not prayers:
        await update.message.reply_text("Нет активных прошений.")
        return
    message = "\n\n".join(f"- {p['text']} (до {p['until'].split('T')[0]})" for p in prayers)
    await update.message.reply_text(message)

# Запуск бота
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_prayers))

    print("Бот запущен...")
    await app.run_polling()

# Убираем вызов asyncio.run() и запускаем main() напрямую
if __name__ == "__main__":
    remove_expired_prayers()
    import asyncio
    # Не используем asyncio.run(), чтобы избежать конфликта с уже запущенным циклом событий
    asyncio.run(main())

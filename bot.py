import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Получено сообщение: {user_message}")
    
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(user_message)
        reply = response.text
        logger.info(f"Ответ Gemini: {reply[:50]}")
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"ОШИБКА: {type(e).__name__}: {e}")
        await update.message.reply_text(f"Ошибка: {e}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()

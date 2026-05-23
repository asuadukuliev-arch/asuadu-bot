import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="""Ты — помощник конного клуба ASUADU (Нальчик). Отвечаешь клиентам в Telegram от имени клуба.

УСЛУГИ И ЦЕНЫ:
• Прогулки — 1 чел 2000 ₽/час, от 2 чел 1500 ₽ (1-й час), далее 1000 ₽/час
• Аллюры (рысь, галоп) — +1000 ₽ (по согласованию)
• Иппотерапия — 1000 ₽ (30 мин)
• Фотосессии — от 2000 ₽
• Перевозка — 70 ₽/км
• Абонементы и туры: https://asuadu.ru/p/price/

ВРЕМЯ РАБОТЫ: 9:00–18:00, возможны индивидуальные маршруты

ЗАПИСЬ: Для записи нужны: дата, время приезда, кол-во человек, номер телефона, уровень верховой езды (0-10)
Предоплата 1000 ₽ (входит в стоимость): Тинькофф 2200700554696970
Отмена — за 24 часа, позже без возврата.

БЕЗОПАСНОСТЬ: Маршруты только с инструктором. Подробнее: https://asuadu.ru/p/disclaimer/
АДРЕС И КОНТАКТЫ: https://asuadu.ru/p/contacts/
РЕЗЕРВНЫЙ КОНТАКТ: https://t.me/asuadu1

ПРАВИЛА ОТВЕТОВ:
- Отвечай дружелюбно и кратко
- Если клиент хочет записаться — собери все нужные данные (дата, время, кол-во человек, телефон, уровень езды)
- Когда все данные собраны, напиши: "НОВАЯ ЗАПИСЬ: [все данные клиента]" — это уведомит владельца
- Если вопрос сложный или нестандартный — скажи что свяжутся в ближайшее время
- Пиши на русском языке"""
)

# История диалогов
conversations = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "Клиент"
    user_message = update.message.text

    if user_id not in conversations:
        conversations[user_id] = model.start_chat(history=[])

    chat = conversations[user_id]

    try:
        response = chat.send_message(user_message)
        reply = response.text

        await update.message.reply_text(reply)

        # Уведомляем владельца если это новая запись
        if "НОВАЯ ЗАПИСЬ:" in reply and OWNER_CHAT_ID:
            now = datetime.now().strftime("%d.%m.%Y %H:%M")
            owner_msg = f"🐴 *Новая запись!*\n\n👤 Клиент: {user_name} (ID: {user_id})\n🕐 {now}\n\n{reply}"
            await context.bot.send_message(
                chat_id=OWNER_CHAT_ID,
                text=owner_msg,
                parse_mode="Markdown"
            )

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text(
            "Извините, произошла ошибка. Свяжитесь с нами напрямую: https://t.me/asuadu1"
        )

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()

import logging
import pandas as pd
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os

# Log sozlamalari
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# .env faylidan token o'qish
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Excel faylini o'qish
try:
    df = pd.read_excel("talabalar.xlsx", engine="openpyxl")
except FileNotFoundError:
    logger.error("talabalar.xlsx topilmadi!")
    raise FileNotFoundError("talabalar.xlsx fayli loyiha papkasida bo'lishi kerak!")
except Exception as e:
    logger.error(f"Excel o'qish xatosi: {e}")
    raise

# Excel'dan lug'at yaratish
STUDENT_GROUPS = {
    str(row["passport_num"]).strip().upper(): (row["group_name"], row["group_link"])
    for _, row in df.iterrows()
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Passport raqamingizni yuboring (masalan: AA1234567).")

async def handle_passport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    passport_num = update.message.text.strip().upper()
    if passport_num in STUDENT_GROUPS:
        group_name, group_link = STUDENT_GROUPS[passport_num]
        await update.message.reply_text(f"Guruh: {group_name}\nLink: {group_link}")
    else:
        await update.message.reply_text("Bunday passport raqami topilmadi!")

def main() -> None:
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN topilmadi!")
        raise ValueError(".env faylida BOT_TOKEN sozlang.")
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_passport))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

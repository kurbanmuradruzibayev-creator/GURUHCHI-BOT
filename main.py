import telebot
import os
from dotenv import load_dotenv
import pandas as pd
import re

# .env faylidan ma'lumotlarni o'qish
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Botni ishga tushirish
bot = telebot.TeleBot(BOT_TOKEN)

# Foydalanuvchi holatini saqlash
user_states = {}

# Pasport raqamini tekshirish uchun regex (AA1234567 yoki 14 raqamli JShShIR)
PASSPORT_REGEX = r'^[A-Z]{2}\d{7}$|^[0-9]{14}$'

# Excel faylidan guruh ma'lumotlarini olish
def get_group_info(passport):
    try:
        df = pd.read_excel('talabalar.xlsx')
        if 'passport' in df.columns:
            result = df[df['passport'] == passport][['group_name', 'group_link']]
            if not result.empty:
                return result.iloc[0]['group_name'], result.iloc[0]['group_link']
        return None, None
    except FileNotFoundError:
        return None, None
    except Exception as e:
        print(f"Excel o'qishda xato: {e}")
        return None, None

@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    user_states[user_id] = 'waiting_for_passport'
    bot.send_message(message.chat.id,
                     "Assalomu alaykum! Guruhga qo'shilish uchun pasport raqamingizni (AA1234567 yoki 14 raqamli JShShIR) yuboring.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if user_id in user_states and user_states[user_id] == 'waiting_for_passport':
        passport = message.text.strip()
        # Pasport raqamini regex bilan tekshirish
        if re.match(PASSPORT_REGEX, passport):
            group_name, group_link = get_group_info(passport)
            if group_name and group_link:
                bot.send_message(message.chat.id,
                                 f"Pasport raqamingiz tasdiqlandi: {passport}\n"
                                 f"Guruh: {group_name}\n"
                                 f"Link: {group_link}")
            else:
                bot.send_message(message.chat.id,
                                "Pasport raqamingiz ro'yxatda topilmadi yoki Excel fayli bilan muammo bor. Iltimos, tekshiring.")
            del user_states[user_id]
        else:
            bot.send_message(message.chat.id,
                            "Noto'g'ri format! Iltimos, AA1234567 yoki 14 raqamli JShShIR kiriting.")
    else:
        bot.send_message(message.chat.id, "Avval /start buyrug'ini yuboring.")

if __name__ == '__main__':
    print("Bot ishga tushdi...")
    bot.polling(none_stop=True)

import os
import telebot
from dotenv import load_dotenv

# 1. Load the ".env" file
load_dotenv()

# 2. Grab the token from the .env file
# (Make sure your .env file has: BOT_TOKEN=8638049326:AAF...)
TOKEN = os.getenv('BOT_TOKEN')

# 3. Initialize the Telegram Bot
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def begin(message):
    bot.reply_to(message, "Hello, I am aviBot and I welcome you!")

# 4. Start the bot
print("Bot is running...")
bot.infinity_polling()
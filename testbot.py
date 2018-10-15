import telebot
import time
import sys

import gspread
from oauth2client.service_account import ServiceAccountCredentials

bot_token = "674824175:AAE4Rtk7nhLfq78juNPq9GT80UC_pB7W8oM"

bot = telebot.TeleBot(bot_token)

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)


# simple start command & bot responds with querying from google sheets
@bot.message_handler(commands=['start'])
def send_welcome(message):
    sheet = client.open("Sheares Media Inventory").sheet1
    sheet_msg = sheet.row_values(1)
    bot.reply_to(message, sheet_msg)

while True:
    try:
        bot.polling()
    except Exception:
        time.sleep(15)

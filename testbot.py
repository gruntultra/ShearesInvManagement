import telebot
import time
import sys

import gspread
from oauth2client.service_account import ServiceAccountCredentials

bot_token = "674824175:AAE4Rtk7nhLfq78juNPq9GT80UC_pB7W8oM"
bot = telebot.TeleBot(bot_token)

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

spreadsheet = client.open("Sheares Media Inventory")

# Assign each sheet to a var
equip_sheet = spreadsheet.worksheet("Equipment_list")
current_loan = spreadsheet.worksheet("Loan")

# simple start command & bot responds with querying from google sheets
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hi! You can create a loan by /createloan")

@bot.message_handler(commands=['createloan'])
def create_loan(message):
    msg = bot.reply_to(message, "-----New Loan Entry-----\n\n" + "Name: \n" + "Block: \n" + "Item: \n" + "Date: \n" + "Duration: \n" + "Purpose: \n\n" +
                       "*****Split each entry with SPACE *****" )
    bot.register_next_step_handler(msg, process_name_step)
    

def process_name_step(message):
    try:
        user_data = message.text.split()
        current_loan.append_row(user_data)
        reply_message = "Loan created successfully!\n\n" + "Name: {}\n" + "Block: {}\n" + "Item: {}\n" + "Date: {}\n" + "Duration: {}\n" + "Purpose: {}\n\n"
        msg = reply_message.format(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4], user_data[5])
        bot.reply_to(message, msg)
    except:
        bot.reply_to(message, "Sorry. Loan has failed to create.")


def main_loop():
    bot.polling(True)
    while 1:
        time.sleep(3)

if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print('Exiting by user request.')
        sys.exit(0)

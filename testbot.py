import telebot
import time
import sys
import markups as mark_ups

import gspread
from oauth2client.service_account import ServiceAccountCredentials

bot_token = "649808767:AAFSKZsMbExXkC2iUHHAWKs-5Z9uLkFGicU"
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
def send_welcome(m):
    cid = m.chat.id
    bot.send_message(cid, text='What would you like to do', reply_markup=mark_ups.start_markup)
    bot.register_next_step_handler(m, create_loan)

# list down all current loans
@bot.message_handler(commands=['list'])
def list_all(m):
    cid = m.chat.id
    count = current_loan.row_count
    counter = 2
    while counter <= count:
        if (current_loan.cell(counter,1).value != ''):
            name = current_loan.cell(counter,1).value
            block = current_loan.cell(counter,2).value
            item = current_loan.cell(counter,3).value
            date = current_loan.cell(counter,4).value
            duration = current_loan.cell(counter,5).value
            purpose = current_loan.cell(counter,6).value
            a_row = "{}. {} {} {} {} {} {}".format(counter - 1,name, block, item, date, duration, purpose)
            bot.send_message(cid, text=a_row)
            counter += 1
        else:
            bot.send_message(cid, text='End of list')
            break

# @bot.message_handler(commands=['createloan'])
def create_loan(m):
    cid = m.chat.id
    text_event = m.text
    if (text_event == u'Create loan'):
        msg = bot.send_message(cid, parse_mode='Markdown', text="*-----New Loan Entry-----*\n\n" + "Name: \n" + "Block: \n" + "Item: \n" + "Date: \n" + "Duration: \n" + "Purpose: \n\n" +
                       "**** *Split each entry with SPACE* ****")
        bot.register_next_step_handler(msg, process_loan)
    else:
        bot.reply_to(m, "goodbye")



def process_loan(m):
    try:
        cid = m.chat.id
        user_data = m.text.split()
        check = validation(user_data, m)
        if(check):
            current_loan.append_row(user_data)
            reply_message = "Loan created successfully!\n\n" + "Name: {}\n" + "Block: {}\n" + "Item: {}\n" + "Date: {}\n" + "Duration: {}\n" + "Purpose: {}\n\n"
            msg = reply_message.format(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4], user_data[5])
            bot.send_message(cid, parse_mode='Markdown', text=msg)
        else:
            bot.send_message(cid, text="Sorry. Loan has failed to create!")
    except:
        bot.send_message(cid, text="Sorry. Loan has failed to create!")

# checks the block to ensure that it exist
def validation(user_data, m):
    cid = m.chat.id
    block = user_data[1]
    if (block == 'A' or block == 'B' or block == 'C' or block == 'D' or block == 'E'):
        return True
    else:
        bot.send_message(cid, text="Sorry! No block exist!")
        return False

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

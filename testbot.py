import telebot
import time
import sys
import markups as mark_up

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

# /start command
@bot.message_handler(commands=['start'])
def start(m):
    cid = m.chat.id
    bot.send_message(cid, parse_mode='Markdown', text='*Available Commands*\n' + '/start - start?\n' + '/menu - Main Menu\n\n' + '*Shortcuts*\n' + '/createloan - Create a loan')

# /menu command
@bot.message_handler(commands=['menu'])
def main_menu(m):
    try:
        mid = m.message_id
        cid = m.chat.id
        bot.edit_message_text(message_id=mid, chat_id=cid, text='Hi! What would you like to do?', reply_markup=mark_up.menu_markup())
    except:
        bot.send_message(chat_id=cid, text='Hi! What would you like to do?', reply_markup=mark_up.menu_markup())

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

# An object to save user data into during createloan 
class User(object):
    def __init__(self):
        self.name = ""
        self.block = ""
        self.item = ""
        self.date = ""
        self.duration = ""
        self.purpose = ""

user = User()

# /createloan command
@bot.message_handler(commands=['createloan'])
def create_loan(m):
    try:
        mid = m.message_id
        cid = m.chat.id
        bot.edit_message_text(message_id=mid, chat_id=cid, parse_mode='Markdown', text="Would you like to create a loan?", reply_markup=mark_up.answer_markup())
    except:
        bot.send_message(chat_id=cid, parse_mode='Markdown', text="Would you like to create a loan?", reply_markup=mark_up.answer_markup())

def process_name(m):
    try:
        cid = m.chat.id
        msg = bot.send_message(cid, parse_mode='Markdown', text="Tell me the name?")
        bot.register_next_step_handler(msg, process_block)
    except:
        bot.send_message(cid, text="An error has occured.")

def process_block(m):
    try:
        cid = m.chat.id
        user.name = m.text
        msg = bot.send_message(cid, parse_mode='Markdown', text="Which block?")
        bot.register_next_step_handler(msg, process_item)
    except:
        bot.send_message(cid, text="An error has occured.")

def process_item(m):
    try:
        cid = m.chat.id
        user.block = m.text
        msg = bot.send_message(cid, parse_mode='Markdown', text="Item that is to be loaned out?")
        bot.register_next_step_handler(msg, process_date)
    except:
        bot.send_message(cid, text="An error has occured.")

def process_date(m):
    try:
        cid = m.chat.id
        user.item = m.text
        msg = bot.send_message(cid, parse_mode='Markdown', text="Date that it is loaned out?")
        bot.register_next_step_handler(msg, process_duration)
    except:
        bot.send_message(cid, text="An error has occured.")

def process_duration(m):
    try:
        cid = m.chat.id
        user.date = m.text
        msg = bot.send_message(cid, parse_mode='Markdown', text="Duration?")
        bot.register_next_step_handler(msg, process_purpose)
    except:
        bot.send_message(cid, text="An error has occured.")

def process_purpose(m):
    try:
        cid = m.chat.id
        user.duration = m.text
        msg = bot.send_message(cid, parse_mode='Markdown', text="Purpose of the loan?")
        bot.register_next_step_handler(msg, process_all_data)
    except:
        bot.send_message(cid, text="An error has occured.")

def process_all_data(m):
    try:
        cid = m.chat.id
        user.purpose = m.text
        verify_loan(m, True)
    except:
        bot.send_message(cid, text="An error has occured.")

def verify_loan(m, args):
    try:
        cid = m.chat.id
        mid = m.message_id
        verify_msg = "*Please verify that the entries are correct!*\n\n" + "*Name:* {}\n" + "*Block:* {}\n" + "*Item:* {}\n" + "*Date:* {}\n" + "*Duration:* {}\n" + "*Purpose:* {}\n\n"
        if(args == True):
            bot.send_message(cid, 
                            parse_mode="Markdown", 
                            text=verify_msg.format(user.name, user.block, user.item, user.date, user.duration, user.purpose),
                            reply_markup=mark_up.submit_loan_markup()
                            )
        else:
            bot.edit_message_text(message_id=mid,
                            chat_id=cid, 
                            parse_mode="Markdown", 
                            text=verify_msg.format(user.name, user.block, user.item, user.date, user.duration, user.purpose),
                            reply_markup=mark_up.submit_loan_markup()
                            )
    except:
        bot.send_message(cid, text="An error has occured.")

def edit_current_loan(m):
    try:
        cid = m.chat.id
        mid = m.message_id
        msg = "*Edit current loan*\n\n" + "*Name:* {}\n" + "*Block:* {}\n" + "*Item:* {}\n" + "*Date:* {}\n" + "*Duration:* {}\n" + "*Purpose:* {}\n\n"
        bot.edit_message_text(message_id=mid, 
                            chat_id=cid, 
                            parse_mode="Markdown",
                            text=msg.format(user.name, user.block, user.item, user.date, user.duration, user.purpose), 
                            reply_markup=mark_up.edit_current_loan_markup())
    except:
        bot.send_message(cid, text="An error has occured.")

def edit_current_loan_data(m, data):
    try:
        mid = m.message_id
        cid = m.chat.id
        msg = bot.edit_message_text(message_id=mid, chat_id=cid, text="OK. Send me the new " + data + ".")
        bot.register_next_step_handler(msg, save_edit_current_loan_data, data)
    except:
        bot.send_message(cid, text="An error has occured.")

def save_edit_current_loan_data(m, data):
    cid = m.chat.id
    if(data == "name"):
        user.name = m.text
        bot.send_message(chat_id=cid, text="Name has succesfully changed!")
    elif(data == "block"):
        user.block = m.text
        bot.send_message(chat_id=cid, text="Block has succesfully changed!")
    elif(data == "item"):
        user.item = m.text
        bot.send_message(chat_id=cid, text="Item has succesfully changed!")
    elif(data == "date"):
        user.date = m.text
        bot.send_message(chat_id=cid, text="Date has succesfully changed!")
    elif(data == "duration"):
        user.duration = m.text
        bot.send_message(chat_id=cid, text="Duration has succesfully changed!")
    elif(data == "purpose"):
        user.purpose = m.text
        bot.send_message(chat_id=cid, text="Purpose has succesfully changed!")
    verify_loan(m, True)

def process_loan(m):
    try:
        cid = m.chat.id
        user_data = [user.name, user.block, user.item, user.date, user.duration, user.purpose]
        check = validation(user_data, m)
        if(check):
            current_loan.append_row(user_data)
            reply_message = "*Loan created successfully!*\n\n" + "*Name:* {}\n" + "*Block:* {}\n" + "*Item:* {}\n" + "*Date:* {}\n" + "*Duration:* {}\n" + "*Purpose:* {}\n\n"
            msg = reply_message.format(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4], user_data[5])
            bot.send_message(cid, parse_mode='Markdown', text=msg, reply_markup=mark_up.great_markup())
            bot.clear_step_handler(m)
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


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    mid = call.message.message_id
    cid = call.message.chat.id
    if call.data == "cb_createloan":
        bot.answer_callback_query(call.id)
        create_loan(call.message)
    elif call.data == "cb_viewloan":
        pass
    elif call.data == "cb_editloan":
        pass
    elif call.data == "cb_letscreate":
        bot.answer_callback_query(call.id)
        process_name(call.message)
    elif call.data == "cb_mainmenu":
        bot.answer_callback_query(call.id)
        main_menu(call.message)
    elif call.data == "cb_editloan_1":
        bot.answer_callback_query(call.id)
        edit_current_loan(call.message)
    elif call.data == "cb_submitloan":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(message_id=mid, chat_id=cid, text="Verifying...")
        process_loan(call.message)
    elif call.data == 'cb_great':
        bot.answer_callback_query(call.id, text="hehe")
    elif call.data == 'cb_backtoverifyloan':
        bot.answer_callback_query(call.id)
        verify_loan(call.message, False)
    elif call.data == 'cb_editname':
        bot.answer_callback_query(call.id)
        edit_current_loan_data(call.message, "name")
    elif call.data == 'cb_editblock':
        bot.answer_callback_query(call.id)
        edit_current_loan_data(call.message, "block")
    elif call.data == 'cb_edititem':
        bot.answer_callback_query(call.id)
        edit_current_loan_data(call.message, "item")
    elif call.data == 'cb_editdate':
        bot.answer_callback_query(call.id)
        edit_current_loan_data(call.message, "date")
    elif call.data == 'cb_editduration':
        bot.answer_callback_query(call.id)
        edit_current_loan_data(call.message, "duration")
    elif call.data == 'cb_editpurpose':
        bot.answer_callback_query(call.id)
        edit_current_loan_data(call.message, "purpose")

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

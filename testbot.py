import telebot
import time
import sys
import markups as mark_up
import datetime
import re
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
equipment_list = spreadsheet.worksheet("Equipment_list")
current_loan = spreadsheet.worksheet("Loan")
loan_history = spreadsheet.worksheet("Loan_history")

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
    list_of_lists = current_loan.get_all_values()
    count = len(list_of_lists)
    counter = 1
    a_row = ''
    while counter < count:
        name = list_of_lists[counter][0]
        block = list_of_lists[counter][1]
        item = list_of_lists[counter][2]
        startdate = list_of_lists[counter][3]
        enddate = list_of_lists[counter][4]
        purpose = list_of_lists[counter][5]
        a_row += "*{}.* {}, {}, {}, {}, {}, {}\n".format(counter, name, block, item, startdate, enddate, purpose)
        counter += 1
    bot.send_message(cid, parse_mode='markdown', text=a_row + '\nEnd of list')

#List Based on name
@bot.message_handler(commands=['listName'])
def list_name(m):
    cid = m.chat.id
    msg = bot.send_message(cid, parse_mode='Markdown', text="What is the name?")
    bot.register_next_step_handler(msg, find_user)
    
def find_user(m):
    try:
        cid = m.chat.id
        compare = m.text
        list_of_lists = current_loan.get_all_values()
        count = len(list_of_lists)      
        counter = 1
        occurance = 0
        while counter < count:
            if list_of_lists[counter][0] == compare:
                name = list_of_lists[counter][0]
                block = list_of_lists[counter][1]
                item = list_of_lists[counter][2]
                startdate = list_of_lists[counter][3]
                enddate = list_of_lists[counter][4]
                purpose = list_of_lists[counter][5]
                a_row = "{}. {} {} {} {} {} {}".format(occurance + 1,name, block, item, startdate, enddate, purpose)
                bot.send_message(cid, text=a_row)
                occurance +=1
            counter += 1
        if occurance == 0:
            txt = "Not Found"
        else:
            txt = "Found {} of {}".format(occurance,compare)
        bot.send_message(cid, text=txt)
    except Exception as e:
        print(e)
        bot.send_message(cid, text="An error has occured.")

#list down expired users
@bot.message_handler(commands=['listExpired'])
def list_expired(m):
    cid = m.chat.id
    list_of_lists = current_loan.get_all_values()
    count = len(list_of_lists)
    counter = 1
    occurance = 0
    a_row = ''
    while counter < count:
        name = list_of_lists[counter][0]
        block = list_of_lists[counter][1]
        item = list_of_lists[counter][2]
        startdate = list_of_lists[counter][3]
        enddate = list_of_lists[counter][4]
        purpose = list_of_lists[counter][5]
        format_str = '%d/%m/%y' # The format
        todays_date = time.strftime("%d/%m/%y")
        todays_date = datetime.datetime.strptime(todays_date, format_str)
        end_date = datetime.datetime.strptime(enddate, format_str)
        if end_date < todays_date:
            a_row += "*{}.* *Name:* {}\n *Block:* {}\n *Item:* {}\n *Start Date:* {}\n *End Date:* {}\n *Purpose:* {}\n\n".format(occurance + 1,name, block, item, startdate, enddate, purpose)
            occurance += 1
        counter += 1
    bot.send_message(cid, parse_mode='markdown', text=a_row + '\nEnd of list')

# An object to save user data into during createloan 
class User(object):
    def __init__(self):
        self.name = ""
        self.block = ""
        self.item = ""
        self.startdate = ""
        self.enddate = ""
        self.duration = ""
        self.purpose = ""

user = User()

# /createloan command
@bot.message_handler(commands=['createloan'])
def create_loan(m):
    try:
        mid = m.message_id
        cid = m.chat.id
        bot.edit_message_text(message_id=mid, chat_id=cid, parse_mode='Markdown', text="Would you like to create a loan?", reply_markup=mark_up.createloan_submenu_markup())
    except:
        bot.send_message(chat_id=cid, parse_mode='Markdown', text="Would you like to create a loan?", reply_markup=mark_up.createloan_submenu_markup())

def process_name(m):
    try:
        cid = m.chat.id
        msg = bot.send_message(cid, parse_mode='Markdown', text="What is the name?")
        bot.register_next_step_handler(msg, process_block, True)
    except:
        bot.send_message(cid, text="An error has occured.")

def process_block(m, arg):
    try:
        cid = m.chat.id
        if(arg):
            user.name = m.text
            msg = bot.send_message(cid, parse_mode='Markdown', text="Which block?")
            bot.register_next_step_handler(msg, process_item)
        else:
            msg = bot.send_message(cid, parse_mode='Markdown', text="Which block?")
            bot.register_next_step_handler(msg, process_item)
    except:
        bot.send_message(cid, text="An error has occured.")

def process_item(m):
    try:
        cid = m.chat.id
        user.block = m.text
        block_val_result = block_validation(user.block, m)
        if (block_val_result):
            msg = bot.send_message(cid, parse_mode='Markdown', text="What is the item/items that are to be loaned out? Specify the item name as well as the quantity. \n\n*If there is more than one, type in this format:*\n\nFlash - 2\nTripod - 1")
            bot.register_next_step_handler(msg, process_startdate, True)
        else:
            process_block(m, False)
    except:
        bot.send_message(cid, text="An error has occured.")

def process_startdate(m, arg):
    try:
        cid = m.chat.id
        if (arg):
            user.item = m.text
            msg = bot.send_message(cid, parse_mode='Markdown', text="Date that it is loaned out?\n\n*Input the date in this format dd/mm/yy*")
            bot.register_next_step_handler(msg, process_enddate, True)
        else:
            msg = bot.send_message(cid, parse_mode='Markdown', text="Date that it is loaned out?\n\n*Input the date in this format dd/mm/yy*")
            bot.register_next_step_handler(msg, process_enddate, True)
    except:
        bot.send_message(cid, text="An error has occured.")

def process_enddate(m, arg):
    try:
        cid = m.chat.id
        if (arg):
            user.startdate = m.text
            date_val_result = start_date_validation(user.startdate, m)
            if (date_val_result):
                msg = bot.send_message(cid, parse_mode='Markdown', text="Date that the item should be returned?\n\n*Input the date in this format dd/mm/yy*")
                bot.register_next_step_handler(msg, process_purpose)
            else:
                process_startdate(m, False)
        else:
            user.startdate = user.startdate
            msg = bot.send_message(cid, parse_mode='Markdown', text="Date that the item should be returned?\n\n*Input the date in this format dd/mm/yy*")
            bot.register_next_step_handler(msg, process_purpose)
    except:
        bot.send_message(cid, text="An error has occured.")

def process_purpose(m):
    try:
        cid = m.chat.id
        user.enddate = m.text
        date_val_result = end_date_validation(user.enddate, m)
        if (date_val_result):
            msg = bot.send_message(cid, parse_mode='Markdown', text="Purpose of the loan?")
            bot.register_next_step_handler(msg, process_all_data)
        else:
            process_enddate(m, False)
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
        verify_msg = "*Please verify that the entries are correct!*\n\n" + "*Name:* {}\n" + "*Block:* {}\n" + "*Item:* {}\n" + "*Start Date:* {}\n" + "*End Date:* {}\n" + "*Purpose:* {}\n\n"
        if(args == True):
            bot.send_message(cid, 
                            parse_mode="Markdown", 
                            text=verify_msg.format(user.name, user.block, user.item, user.startdate, user.enddate, user.purpose),
                            reply_markup=mark_up.submit_loan_markup()
                            )
        else:
            bot.edit_message_text(message_id=mid,
                            chat_id=cid, 
                            parse_mode="Markdown", 
                            text=verify_msg.format(user.name, user.block, user.item, user.startdate, user.enddate, user.purpose),
                            reply_markup=mark_up.submit_loan_markup()
                            )
    except:
        bot.send_message(cid, text="An error has occured.")

def edit_current_loan(m):
    try:
        cid = m.chat.id
        mid = m.message_id
        msg = "*Edit current loan*\n\n" + "*Name:* {}\n" + "*Block:* {}\n" + "*Item:* {}\n" + "*Start Date:* {}\n" + "*End Date:* {}\n" + "*Purpose:* {}\n\n"
        bot.edit_message_text(message_id=mid, 
                                chat_id=cid, 
                                parse_mode="Markdown",
                                text=msg.format(user.name, user.block, user.item, user.startdate, user.enddate, user.purpose), 
                                reply_markup=mark_up.edit_current_loan_markup())
    except:
        bot.send_message(cid, text="An error has occured.")

def edit_current_loan_data(m, data):
    try:
        cid = m.chat.id
        msg = bot.send_message(chat_id=cid, text="OK. Send me the new " + data + ".")
        bot.register_next_step_handler(msg, save_edit_current_loan_data, data)
    except:
        bot.send_message(cid, text="An error has occured.")

def validation_fail(m, data):
    try:
        cid = m.chat.id
        msg = bot.send_message(chat_id=cid, text="Send me the " + data + " again.")
        bot.register_next_step_handler(msg, save_edit_current_loan_data, data)
    except:
        bot.send_message(cid, text="An error has occured.")

def save_edit_current_loan_data(m, data):
    cid = m.chat.id
    if(data == "name"):
        user.name = m.text
        bot.send_message(chat_id=cid, text="Success! Name Updated.")
    elif(data == "block"):
        user.block = m.text
        block_val = block_validation(user.block, m)
        if(block_val):
            bot.send_message(chat_id=cid, text="Success! Block Updated.")
            verify_loan(m, True)
        else:
            validation_fail(m, 'block')
    elif(data == "item"):
        user.item = m.text
        bot.send_message(chat_id=cid, text="Success! Item Updated.")
    elif(data == "startdate"):
        user.startdate = m.text
        startdate_val = start_date_validation(user.startdate, m)
        if(startdate_val):
            bot.send_message(chat_id=cid, text="Success! Start Date Updated.")
            verify_loan(m, True)
        else:
            validation_fail(m, 'startdate')
    elif(data == "enddate"):
        user.enddate = m.text
        enddate_val = end_date_validation(user.startdate, m)
        if(enddate_val):
            bot.send_message(chat_id=cid, text="Success! End Date Updated.")
            verify_loan(m, True)
        else:
            validation_fail(m, 'enddate')
    elif(data == "purpose"):
        user.purpose = m.text
        bot.send_message(chat_id=cid, text="Success! Purpose Updated.")

def process_loan(m):
    try:
        cid = m.chat.id
        user_data = [user.name, user.block, user.item, user.startdate, user.enddate, user.purpose]
        current_loan.append_row(user_data)
        stock_taking(user.item)
        reply_message = "*Loan created successfully!*\n\n" + "*Name:* {}\n" + "*Block:* {}\n" + "*Item:* {}\n" + "*Start Date:* {}\n" + "*End Date:* {}\n" + "*Purpose:* {}\n\n"
        msg = reply_message.format(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4], user_data[5])
        bot.send_message(cid, parse_mode='Markdown', text=msg, reply_markup=mark_up.great_markup())
        bot.clear_step_handler(m)
    except:
        bot.send_message(cid, text="Loan has failed to create!")

def block_validation(block, m):
    cid = m.chat.id
    block_criteria = re.match(re.compile(r'[A-Ea-e]'), block)
    if(block_criteria):
        return True
    else:
        bot.send_message(cid, text="It doesn't seem like there is Block " + block + " in Sheares Hall. Please type again.")
        return False

def start_date_validation(date, m):
    cid = m.chat.id
    pattern = re.compile(r'^(3[01]|[12][0-9]|0?[1-9])/(1[0-2]|0?[1-9])/(?:[0-9]{2})?[0-9]{2}$')
    date_criteria = re.match(pattern, date)
    if(date_criteria):
        return True
    else:
        bot.send_message(cid, text="I do not recognise this date :( Please type again")
        return False

def end_date_validation(date, m):
    cid = m.chat.id
    pattern = re.compile(r'^(3[01]|[12][0-9]|0?[1-9])/(1[0-2]|0?[1-9])/(?:[0-9]{2})?[0-9]{2}$')
    date_criteria = re.match(pattern, date)
    if(date_criteria):
        return True
    else:
        bot.send_message(cid, text="I do not recognise this date :( Please type again")
        return False

# stock taking
def stock_taking(item_name):
    item = item_name.splitlines()
    d = {}
    temp = []
    for i in item:
        temp = i.split("-")
        d[(temp[0].strip())] = temp[1].strip()
    for key, value in d.items():
        item = equipment_list.find(re.compile(key, re.IGNORECASE))
        in_stock = int(equipment_list.cell(item.row, 4).value) - int(value)
        on_loan = int(equipment_list.cell(item.row, 5).value) + int(value)
        equipment_list.update_cell(item.row, 4, in_stock)
        equipment_list.update_cell(item.row, 5, on_loan)
    return

# Edit Loan Sub-Menu
def edit_loan_submenu(m):
    try:
        mid = m.message_id
        cid = m.chat.id
        bot.edit_message_text(message_id=mid, chat_id=cid, text='Edit on google sheets.', reply_markup=mark_up.edit_loan_submenu_markup())
    except:
        bot.send_message(chat_id=cid, text='An error has occured')

# View Loan Sub-Menu
def view_loan_submenu(m):
    try:
        mid = m.message_id
        cid = m.chat.id
        bot.edit_message_text(message_id=mid, chat_id=cid, text='Choose one option:', reply_markup=mark_up.view_loan_submenu_markup())
    except:
        bot.send_message(chat_id=cid, text='An error has occured')

#return loan and keep track of history
@bot.message_handler(commands=['returnloan'])
def return_loan(m):
    try:
        cid = m.chat.id
        mid = m.message_id
        msg = bot.send_message(cid, parse_mode='Markdown', text="What is the name?")
        bot.register_next_step_handler(msg, find_name)
    except:
        bot.send_message(cid, text="An error has occured.")

def find_name(m):
    try:
        cid = m.chat.id
        compare = m.text
        list_of_lists = current_loan.get_all_values()
        count = len(list_of_lists)      
        counter = 1
        occurance = 0
        while counter < count:
            if list_of_lists[counter][0] == compare:
                name = list_of_lists[counter][0]
                block = list_of_lists[counter][1]
                item = list_of_lists[counter][2]
                startdate = list_of_lists[counter][3]
                enddate = list_of_lists[counter][4]
                purpose = list_of_lists[counter][5]
                a_row = "{}. {} {} {} {} {} {} row {}".format(occurance + 1,name, block, item, startdate, enddate, purpose, counter)
                bot.send_message(cid, text=a_row)
                occurance +=1
            counter += 1
        if occurance == 0:
            txt = "Not Found"
        else:
            txt = "Found {} of {}".format(occurance,compare)
            msg = bot.send_message(cid, parse_mode='Markdown', text="Which item is returned? Specify the row number")
            bot.register_next_step_handler(msg, return_process)
        bot.send_message(cid, text=txt)
    except Exception as e: 
        print(e)
        bot.send_message(cid, text="Error is here.")

def return_process(m):
    try:
        cid = m.chat.id
        row = int(m.text)
        list_of_lists = current_loan.get_all_values()
        stock_track = list_of_lists[row][2]
        check = stock_returning(stock_track, m)
        if check:
            loan_history.append_row(list_of_lists[row])
            current_loan.delete_row(row + 1)
            bot.send_message(cid, text="Success! Loan completed.")
        else:
            bot.send_message(cid, text="Failed to delete.")
    except Exception as e:
        print(e)
        bot.send_message(cid, text="Problem with the deletion process.")
        
def stock_returning(item_name, m):
    try:
        cid = m.chat.id
        item = item_name.splitlines()
        d = {}
        temp = []
        print(item)
        for i in item:
            temp = i.split("-")
            d[(temp[0].strip())] = temp[1].strip()
        for key, value in d.items():
            item = equipment_list.find(re.compile(key, re.IGNORECASE))
            in_stock = int(equipment_list.cell(item.row, 4).value) + int(value)
            on_loan = int(equipment_list.cell(item.row, 5).value) - int(value)
            equipment_list.update_cell(item.row, 4, in_stock)
            equipment_list.update_cell(item.row, 5, on_loan)
        return True
    except:
        bot.send_message(cid, text="Somehow the stock isn't returning")
        return False


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    mid = call.message.message_id
    cid = call.message.chat.id
    if call.data == "cb_createloan":
        bot.answer_callback_query(call.id)
        create_loan(call.message)
    elif call.data == "cb_viewloan":
        bot.answer_callback_query(call.id)
        view_loan_submenu(call.message)
    elif call.data == "cb_editloan":
        bot.answer_callback_query(call.id)
        edit_loan_submenu(call.message)
    elif call.data == "cb_returnloan":
        bot.answer_callback_query(call.id)
        return_loan(call.message)
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
        bot.edit_message_text(message_id=mid, chat_id=cid, text="Loading...")
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
    elif call.data == 'cb_editstartdate':
        bot.answer_callback_query(call.id)
        edit_current_loan_data(call.message, "startdate")
    elif call.data == 'cb_editenddate':
        bot.answer_callback_query(call.id)
        edit_current_loan_data(call.message, "enddate")
    elif call.data == 'cb_editpurpose':
        bot.answer_callback_query(call.id)
        edit_current_loan_data(call.message, "purpose")
    elif call.data == 'cb_viewallloans':
        bot.answer_callback_query(call.id)
        list_all(call.message)
    elif call.data == 'cb_viewbyname':
        bot.answer_callback_query(call.id)
        list_name(call.message)
    elif call.data == 'cb_viewexpiredloans':
        bot.answer_callback_query(call.id)
        list_expired(call.message)

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

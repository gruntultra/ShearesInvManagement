import config
import sys
import sqlite3
import shmbot
import gspread
import time
import datetime
import operator

client = gspread.authorize(config.creds)

spreadsheet = client.open("Sheares Media Inventory")
camera_bodies_list = spreadsheet.worksheet("Camera Bodies")
lens_list = spreadsheet.worksheet("Lens")
camera_equipments_list = spreadsheet.worksheet("Camera Equipments")
loan = spreadsheet.worksheet("Loan")
loan_history = spreadsheet.worksheet("Loan_history")

def save_to_db(user_id, column_name, value):
    try:
        command = "UPDATE users SET {} = ? WHERE user_id = ?".format(column_name)
        sqlite_db = sqlite3.connect(config.db)
        cur = sqlite_db.cursor()
        cur.execute(command, (str(value), str(user_id)))
        sqlite_db.commit()
        sqlite_db.close()
    except Exception as e:
        shmbot.bot.send_message(chat_id = user_id, text = str(e))

def get_from_db(user_id, column_name):
    try:
        command = "SELECT {} FROM users WHERE user_id = {}".format(column_name, str(user_id))
        sqlite_db = sqlite3.connect(config.db)
        cur = sqlite_db.cursor()
        cur.execute(command)
        result = cur.fetchall()
        sqlite_db.close()
        return result[0][0]
    except:
        shmbot.bot.send_message(chat_id = user_id, text = "Error saving data to database.")

def clear_fields(user_id):
    try:
        command = """UPDATE users
                     SET name = "", 
                        block = "",
                        item = "", 
                        start_date = "", 
                        end_date = "", 
                        purpose = "", 
                        to_be_edited = "", 
                        temp_items = "", 
                        temp_category = ""
                        WHERE user_id = {}""".format(user_id)
        sqlite_db = sqlite3.connect(config.db)
        cur = sqlite_db.cursor()
        cur.execute(command,)
        sqlite_db.commit()
        sqlite_db.close()
    except Exception as e:
        shmbot.bot.send_message(chat_id = user_id, text = str(e))

def initialize_user(message, value):
    try:
        exist_user_command = 'SELECT user_id FROM users'
        command = '''INSERT INTO users VALUES(?, ?, ?, null, null, null ,null ,null ,null, null, "", null)'''
        sqlite_db = sqlite3.connect(config.db)
        cur = sqlite_db.cursor()
        cur.execute(exist_user_command)
        users = cur.fetchall()
        user_list = []
        for user in users:
            user_list.append(user[0])
        if str(message.chat.id) in user_list:
            return False
        else:
            cur.execute(command, (str(message.from_user.username), str(message.chat.id), str(value)))
            sqlite_db.commit()
            sqlite_db.close()
            return True
    except Exception as e:
        raise e

def get_current_state(user_id):
    try:
        command = '''SELECT state FROM users WHERE user_id = {}'''.format(str(user_id))
        sqlite_db = sqlite3.connect(config.db)
        cur = sqlite_db.cursor()
        cur.execute(command)
        state = cur.fetchall()
        sqlite_db.close()
        return state[0][0]
    except Exception as e:
        raise e

def get_entry(user_id):
    try:
        command = 'SELECT * FROM users where user_id = {}'.format(str(user_id))
        sqlite_db = sqlite3.connect(config.db)
        cur = sqlite_db.cursor()
        cur.execute(command)
        entries = cur.fetchall()
        sqlite_db.close()
        return entries[0]
    except Exception as e:
        raise e

def set_field(user_id, field):
    try:
        command = 'UPDATE users SET to_be_edited = ? WHERE user_id = ?'
        sqlite_db = sqlite3.connect(config.db)
        cur = sqlite_db.cursor()
        cur.execute(command, (str(field), str(user_id)))
        sqlite_db.commit()
        sqlite_db.close()
    except Exception as e:
        raise e

def get_field(user_id):
    try:
        command = 'SELECT to_be_edited from users WHERE user_id = {}'.format(user_id)
        sqlite_db = sqlite3.connect(config.db)
        cur = sqlite_db.cursor()
        cur.execute(command)
        field = cur.fetchall()
        sqlite_db.close()
        return field[0][0]
    except Exception as e:
        raise e

def save_items_temp(user_id, item_name, quantity):
    try:
        command = 'SELECT temp_items from users WHERE user_id = {}'.format(user_id)
        command_1 = 'UPDATE users SET temp_items = ? WHERE user_id = ?'
        sqlite_db = sqlite3.connect(config.db)
        cur = sqlite_db.cursor()
        cur.execute(command)
        existing_items = cur.fetchall()[0][0]
        new_items = existing_items + "\n" + item_name + " " + quantity + "x"
        cur.execute(command_1, (new_items, str(user_id)))
        sqlite_db.commit()
        sqlite_db.close()
        return new_items
    except Exception as e:
        raise e

def check_overlap(user_id, item_name):
    command = 'SELECT temp_items from users WHERE user_id = {}'.format(user_id)
    sqlite_db = sqlite3.connect(config.db)
    cur = sqlite_db.cursor()
    cur.execute(command)
    existing_items = cur.fetchall()[0][0].split("\n")
    if any(item_name in s for s in existing_items):
        return True
    else:
        return False

def edit_quantity(user_id, item_name, quantity):
    command = 'SELECT temp_items from users WHERE user_id = {}'.format(user_id)
    command_1 = 'UPDATE users SET temp_items = ? WHERE user_id = {}'.format(user_id)
    sqlite_db = sqlite3.connect(config.db)
    cur = sqlite_db.cursor()
    cur.execute(command)
    existing_items = cur.fetchall()[0][0].split("\n")
    for items in existing_items:
        if item_name in items:
            splitted_items = items.split(" ")
            existing_quantity = splitted_items[1].replace("x", "")
            new_quantity = int(quantity) + int(existing_quantity)
            updated_item = item_name + " " + str(new_quantity) + "x"
            index = existing_items.index(items)
            existing_items[index] = updated_item
            updated_list = "\n".join(existing_items)
            cur.execute(command_1, (updated_list,))
            sqlite_db.commit()
            sqlite_db.close()
            return updated_list
        else:
            continue
        return None

def if_empty(user_id):
    try:
        command = 'SELECT temp_items from users WHERE user_id = {}'.format(user_id)
        sqlite_db = sqlite3.connect(config.db)
        cur = sqlite_db.cursor()
        cur.execute(command)
        value = cur.fetchall()
        sqlite_db.close()
        if value[0][0] == "":
            return True
        else:
            return False
    except Exception as e:
        raise e

def update_loan_gsheets(category, item, quantity, in_stock_operator, on_loan_operator):
    if category == "Camera Equipments":
        cell = camera_equipments_list.findall(item)[0]
        in_stock = camera_equipments_list.cell(cell.row, 4)
        on_loan = camera_equipments_list.cell(cell.row, 5)
        new_in_stock_val = in_stock_operator(int(in_stock.value), int(quantity))
        new_on_loan_val = on_loan_operator(int(on_loan.value), int(quantity))
        camera_equipments_list.update_cell(cell.row, 4, str(new_in_stock_val))
        camera_equipments_list.update_cell(cell.row, 5, str(new_on_loan_val))
    elif category == "Camera Bodies":
        cell = camera_bodies_list.findall(item)[0]
        in_stock = camera_bodies_list.cell(cell.row, 4)
        on_loan = camera_bodies_list.cell(cell.row, 5)
        new_in_stock_val = in_stock_operator(int(in_stock.value), int(quantity))
        new_on_loan_val = on_loan_operator(int(on_loan.value), int(quantity))
        camera_bodies_list.update_cell(cell.row, 4, str(new_in_stock_val))
        camera_bodies_list.update_cell(cell.row, 5, str(new_on_loan_val))
    elif category == "Lens":
        cell = lens_list.findall(item)[0]
        in_stock = lens_list.cell(cell.row, 4)
        on_loan = lens_list.cell(cell.row, 5)
        new_in_stock_val = in_stock_operator(int(in_stock.value), int(quantity))
        new_on_loan_val = on_loan_operator(int(on_loan.value), int(quantity))
        lens_list.update_cell(cell.row, 4, str(new_in_stock_val))
        lens_list.update_cell(cell.row, 5, str(new_on_loan_val))

def submit_loan_gsheets(entry):
    loan.append_row(entry)
    return True

def get_expiry_loans():
    list_of_lists = loan.get_all_values()
    count = len(list_of_lists)
    counter = 1
    expired_loans = []
    row = []
    while counter < count:
        format_str = '%d/%m/%y' # The format
        todays_date = time.strftime("%d/%m/%y")
        todays_date = datetime.datetime.strptime(todays_date, format_str)
        enddate = list_of_lists[counter][4]
        end_date = datetime.datetime.strptime(enddate, format_str)
        if end_date < todays_date:
            msg = str(list_of_lists[counter][0]) + ", Expired On " + list_of_lists[counter][4]
            expired_loans.append(msg)
            row.append(counter)
        counter += 1
    return expired_loans, row

def move_expired_to_history(row: int):
    list_of_lists = loan.get_all_values()
    loan_history.append_row(list_of_lists[row])
    item_pair = list_of_lists[row][2]
    list_of_items = item_pair.split("\n")
    for items in list_of_items:
        split_item = items.split(" ")
        if split_item[0] == "":
            continue
        item = split_item[0]
        quantity = split_item[1].replace("x", "")
        category = find_category(item)
        update_loan_gsheets(category, item, quantity, operator.__add__, operator.__sub__)
    loan.delete_row(row + 1)

def get_expired_user_detail(row):
    row = int(row) + 1
    user_details = loan.row_values(row)
    msg = "*User Details:*\n\n" + "*Name:* {}\n" + "*Block:* {}\n" + "*Item:* {}\n" + "*Start Date:* {}\n" + "*End Date:* {}\n" + "*Purpose:* {}\n\nDo you want to return this?"
    return msg.format(user_details[0], user_details[1], user_details[2], user_details[3], user_details[4], user_details[5])

def find_category(item):
    if camera_bodies_list.findall(item):
        return "Camera Bodies"
    elif camera_equipments_list.findall(item):
        return "Camera Equipments"
    elif lens_list.findall(item):
        return "Lens"
    

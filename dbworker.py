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
batteries_list = spreadsheet.worksheet("Batteries")
memory_card_list = spreadsheet.worksheet("Memory Card")
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
    except:
        shmbot.bot.send_message(chat_id = user_id, text = "Error saving data to database.")

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
        shmbot.bot.send_message(chat_id = user_id, text = "Error getting data from database.")

def clear_fields(user_id):
    try:
        command = """UPDATE users
                     SET name = "", 
                        block = "",
                        item = "", 
                        start_date = "", 
                        end_date = "", 
                        purpose = "",  
                        temp_items = "", 
                        temp_category = "",
                        temp_row = "",
                        temp_field = "",
                        items_to_add = "",
                        items_to_remove = ""
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
        command = '''INSERT INTO users VALUES(?, ?, ?, null, null, null ,null ,null, null, "", null, null, null, "", "")'''
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
    except:
        print("Initialization error")

def get_current_state(user_id):
    try:
        command = '''SELECT state FROM users WHERE user_id = {}'''.format(str(user_id))
        sqlite_db = sqlite3.connect(config.db)
        cur = sqlite_db.cursor()
        cur.execute(command)
        state = cur.fetchall()
        sqlite_db.close()
        return state[0][0]
    except:
        shmbot.bot.send_message(chat_id = user_id, text = "Please /start again.")
        
def get_entry(user_id):
    try:
        command = 'SELECT * FROM users where user_id = {}'.format(str(user_id))
        sqlite_db = sqlite3.connect(config.db)
        cur = sqlite_db.cursor()
        cur.execute(command)
        entries = cur.fetchall()
        sqlite_db.close()
        return entries[0]
    except:
        print("Get entry error")

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
    except:
        print("Error saving items")

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
        print("If empty error")

def submit_loan_gsheets(entry):
    try:
        client.login()
        loan.append_row(entry)
        items = entry[2].split("\n")
        for item in items:
            item_name = item.split(" ")[0]
            if camera_bodies_list.findall(item_name):
                command = "SELECT In_Stock, On_Loan FROM 'Camera Bodies' WHERE Equipment = '{}'".format(item_name)
                sqlite_db = sqlite3.connect(config.inv_db)
                cur = sqlite_db.cursor()
                cur.execute(command)
                existing_quantity = cur.fetchall()
                in_stock_qty = existing_quantity[0][0]
                on_loan_qty = existing_quantity[0][1]
                item = camera_bodies_list.findall(item_name)[0]
                camera_bodies_list.update_cell(item.row, 4, in_stock_qty)
                camera_bodies_list.update_cell(item.row, 5, on_loan_qty)
            elif camera_equipments_list.findall(item_name):
                command = "SELECT In_Stock, On_Loan FROM 'Camera Equipments' WHERE Equipment = '{}'".format(item_name)
                sqlite_db = sqlite3.connect(config.inv_db)
                cur = sqlite_db.cursor()
                cur.execute(command)
                existing_quantity = cur.fetchall()
                in_stock_qty = existing_quantity[0][0]
                on_loan_qty = existing_quantity[0][1]
                item = camera_equipments_list.findall(item_name)[0]
                camera_equipments_list.update_cell(item.row, 4, in_stock_qty)
                camera_equipments_list.update_cell(item.row, 5, on_loan_qty)
            elif lens_list.findall(item_name):
                command = "SELECT In_Stock, On_Loan FROM 'Lens' WHERE Equipment = '{}'".format(item_name)
                sqlite_db = sqlite3.connect(config.inv_db)
                cur = sqlite_db.cursor()
                cur.execute(command)
                existing_quantity = cur.fetchall()
                in_stock_qty = existing_quantity[0][0]
                on_loan_qty = existing_quantity[0][1]
                item = lens_list.findall(item_name)[0]
                lens_list.update_cell(item.row, 4, in_stock_qty)
                lens_list.update_cell(item.row, 5, on_loan_qty)
            elif batteries_list.findall(item_name):
                command = "SELECT In_Stock, On_Loan FROM 'Batteries' WHERE Equipment = '{}'".format(item_name)
                sqlite_db = sqlite3.connect(config.inv_db)
                cur = sqlite_db.cursor()
                cur.execute(command)
                existing_quantity = cur.fetchall()
                in_stock_qty = existing_quantity[0][0]
                on_loan_qty = existing_quantity[0][1]
                item = batteries_list.findall(item_name)[0]
                batteries_list.update_cell(item.row, 4, in_stock_qty)
                batteries_list.update_cell(item.row, 5, on_loan_qty)
            elif memory_card_list.findall(item_name): 
                command = "SELECT In_Stock, On_Loan FROM 'Memory Cards' WHERE Equipment = '{}'".format(item_name)
                sqlite_db = sqlite3.connect(config.inv_db)
                cur = sqlite_db.cursor()
                cur.execute(command)
                existing_quantity = cur.fetchall()
                in_stock_qty = existing_quantity[0][0]
                on_loan_qty = existing_quantity[0][1]
                item = memory_card_list.findall(item_name)[0]
                memory_card_list.update_cell(item.row, 4, in_stock_qty)
                memory_card_list.update_cell(item.row, 5, on_loan_qty)
        return True
    except:
        return False

def update_loan_gsheets(category, item, quantity, in_stock_operator, on_loan_operator):
    client.login()
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
    elif category == "Batteries":
        cell = batteries_list.findall(item)[0]
        in_stock = batteries_list.cell(cell.row, 4)
        on_loan = batteries_list.cell(cell.row, 5)
        new_in_stock_val = in_stock_operator(int(in_stock.value), int(quantity))
        new_on_loan_val = on_loan_operator(int(on_loan.value), int(quantity))
        batteries_list.update_cell(cell.row, 4, str(new_in_stock_val))
        batteries_list.update_cell(cell.row, 5, str(new_on_loan_val))
    elif category == "Memory Cards":
        cell = memory_card_list.findall(item)[0]
        in_stock = memory_card_list.cell(cell.row, 4)
        on_loan = memory_card_list.cell(cell.row, 5)
        new_in_stock_val = in_stock_operator(int(in_stock.value), int(quantity))
        new_on_loan_val = on_loan_operator(int(on_loan.value), int(quantity))
        memory_card_list.update_cell(cell.row, 4, str(new_in_stock_val))
        memory_card_list.update_cell(cell.row, 5, str(new_on_loan_val))

def get_expiry_loans():
    client.login()
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
    client.login()
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
    loan.delete_row(row + 1)

def get_expired_user_detail(row):
    client.login()
    row = int(row) + 1
    user_details = loan.row_values(row)
    return user_details

def find_category(item):
    categories = get_table_name()
    command = "SELECT * FROM '{}' WHERE Equipment = ?"
    sqlite_db = sqlite3.connect(config.inv_db)
    cur = sqlite_db.cursor()
    for category in categories:
        new_command = command.format(category[0])
        cur.execute(new_command, (item,))
        data = cur.fetchall()
        if data:
            break
        else:
            continue
    return category[0]

def get_loan_names():
    client.login()
    name_list = loan.col_values(1)[1:]
    start_date = loan.col_values(4)[1:]
    a = len(name_list) + 2
    return name_list, start_date, list(range(2, a))

def view_loan(user_row):
    client.login()
    user_details = loan.row_values(user_row)
    return user_details

def delete_loan(user_row):
    client.login()
    loan.delete_row(int(user_row))
    pass

def update_editted_data(row, col, new_data):
    client.login()
    my_dict = {"name":1, "block":2, "startdate":4, "enddate":5, "purpose":6}
    loan.update_cell(row, my_dict[col], new_data)

def update_items(row, new_data):
    client.login()
    loan.update_cell(row, 3, new_data)

def get_table_name():
    try:
        command = "SELECT name FROM sqlite_master WHERE type = 'table';"
        sqlite_db = sqlite3.connect(config.inv_db)
        cur = sqlite_db.cursor()
        cur.execute(command)
        categories = cur.fetchall()
        return categories
    except:
        print("Error while quering database")

def get_from_inv_db(category):
    command = "SELECT Equipment, In_Stock FROM '{}'".format(category)
    sqlite_db = sqlite3.connect(config.inv_db)
    cur = sqlite_db.cursor()
    cur.execute(command)
    items = cur.fetchall()
    return items

def stock_taking(category, item, quantity, lending):
    try:
        select_command = "SELECT In_Stock, On_Loan FROM '{}' WHERE Equipment = '{}'".format(category, item)
        update_command = "UPDATE '{}' set In_Stock = ?, On_Loan = ? WHERE Equipment = '{}'".format(category, item)
        sqlite_db = sqlite3.connect(config.inv_db)
        cur = sqlite_db.cursor()
        cur.execute(select_command)
        existing_quantity = cur.fetchall()
        in_stock_qty = existing_quantity[0][0]
        on_loan_qty = existing_quantity[0][1]
        if lending:
            new_in_stock = in_stock_qty - int(quantity)
            new_on_loan = on_loan_qty + int(quantity)
        else:
            new_in_stock = in_stock_qty + int(quantity)
            new_on_loan = on_loan_qty - int(quantity)
        cur.execute(update_command, (new_in_stock, new_on_loan,))
        sqlite_db.commit()
        sqlite_db.close()
    except:
        print("database error")

def add_or_remove(user_id, category, item, quantity, add):
    if add:
        select_command = "SELECT items_to_add FROM users WHERE user_id = {}".format(user_id)
        update_command = "UPDATE users SET items_to_add = ? WHERE user_id = {}".format(user_id)
    else:
        select_command = "SELECT items_to_remove FROM users WHERE user_id = {}".format(user_id)
        update_command = "UPDATE users SET items_to_remove = ? WHERE user_id = {}".format(user_id)
    data = category + "," + item + "," + quantity
    sqlite_db = sqlite3.connect(config.db)
    cur = sqlite_db.cursor()
    cur.execute(select_command)
    existing_items = cur.fetchall()[0][0]
    new_items = existing_items + "\n" + category + "," + item + "," + quantity
    cur.execute(update_command, (new_items,))
    sqlite_db.commit()
    sqlite_db.close()
    
    
    

    

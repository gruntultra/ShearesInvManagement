from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import config
import gspread

client = gspread.authorize(config.creds)

spreadsheet = client.open("Sheares Media Inventory")
camera_bodies_list = spreadsheet.worksheet("Camera Bodies")
lens_list = spreadsheet.worksheet("Lens")
camera_equipments_list = spreadsheet.worksheet("Camera Equipments")

# Main Menu
def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Create Loan", callback_data=f"cb_createloan"), 
                InlineKeyboardButton("View Loan", callback_data=f"cb_viewloan"), 
                InlineKeyboardButton("Edit Loan", callback_data=f"cb_editloan"),
                InlineKeyboardButton("Return Loan", callback_data=f"cb_returnloan"))
    return markup

# Edit Loan Main Menu
def edit_loan_main_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Open Google Sheets", url='https://docs.google.com/spreadsheets/d/1FtSe_qt3lgHE8TTkqaSwWfzCcKk8WZ_Rdblw7nXsIWc/edit?usp=sharing'),
               InlineKeyboardButton("Main Menu", callback_data=f"cb_mainmenu"))
    return markup

# Createloan Sub Menu
def create_loan_sub_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Let's Create!", callback_data=f"cb_letscreate"), 
                InlineKeyboardButton("Main Menu", callback_data=f"cb_mainmenu"))
    return markup

# Submit Loan menu during createloan
def submit_loan_sub_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Edit Loan", callback_data=f"cb_editloan_cl"), 
                InlineKeyboardButton("Submit Loan", callback_data=f"cb_submitloan_cl"))
    return markup

# Edit loan menu during createloan
def edit_current_loan_sub_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Edit Name", callback_data=f"cb_editname"), 
                InlineKeyboardButton("Edit Block", callback_data=f"cb_editblock"),
                InlineKeyboardButton("Edit Item", callback_data=f"cb_edititem"),
                InlineKeyboardButton("Edit Start Date", callback_data=f"cb_editstartdate"),
                InlineKeyboardButton("Edit End Date", callback_data=f"cb_editenddate"),
                InlineKeyboardButton("Edit Purpose", callback_data=f"cb_editpurpose"),
                InlineKeyboardButton("Back", callback_data=f'cb_backtoverifyloan'))
    return markup

# Item menu
def main_category_menu():
    categories = ["Camera Equipments", "Camera Bodies", "Lens"]
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for category in categories:
        markup.add(InlineKeyboardButton(text = category, callback_data = "cat_{}".format(category)))
    markup.add(InlineKeyboardButton(text = "Remove items", callback_data = f"cb_remove_items"))
    markup.add(InlineKeyboardButton(text = "Submit items", callback_data = f"cb_submit_items"))
    return markup

def items_menu(category):
    list_of_camera_bodies = camera_bodies_list.col_values(1)
    camera_body_quantity = camera_bodies_list.col_values(4)
    list_of_lens = lens_list.col_values(1)
    lens_quantity = lens_list.col_values(4)
    list_of_camera_equipments = camera_equipments_list.col_values(1)
    camera_equipments_quantity = camera_equipments_list.col_values(4)
    if category == "cat_Camera Equipments":
        buttons = list_of_camera_equipments[1:]
        quantities = camera_equipments_quantity[1:]
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        for button_name, quantity in zip(buttons, quantities):
            markup.add(InlineKeyboardButton(text = button_name + " " + quantity + "x", callback_data = "item_{}_{}".format(button_name, quantity)))
    elif category == "cat_Camera Bodies":
        buttons = list_of_camera_bodies[1:]
        quantities = camera_body_quantity[1:]
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        for button_name, quantity in zip(buttons, quantities):
            markup.add(InlineKeyboardButton(text = button_name + " " + quantity + "x", callback_data = "item_{}_{}".format(button_name, quantity)))
    elif category == "cat_Lens":
        buttons = list_of_lens[1:]
        quantities = lens_quantity[1:]
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        for button_name, quantity in zip(buttons, quantities):
            markup.add(InlineKeyboardButton(text = button_name + " " + quantity + "x", callback_data = "item_{}_{}".format(button_name, quantity)))
    markup.add(InlineKeyboardButton(text = "Back to 🏠", callback_data = f"back_to_main_cat"))
    return markup

def quantity_choosing(quantity, item_name):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    i = 1
    while i <= int(quantity):
        markup.add(InlineKeyboardButton(text = i, callback_data = "q_{}_{}".format(i, item_name)))
        i += 1
    markup.add(InlineKeyboardButton(text = "Back to items", callback_data = f"back_to_items"))
    return markup

def item_removal(user_id, items):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    list_of_items = items.split("\n")
    for item in list_of_items:
        markup.add(InlineKeyboardButton(text = item, callback_data= "remove_{}".format(item)))
    markup.add(InlineKeyboardButton(text = "Back to 🏠", callback_data = f"back_to_main_cat"))
    return markup

def return_loan_menu(expired_loans, rows):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for loan, row in zip(expired_loans, rows):
        markup.add(InlineKeyboardButton(text = loan, callback_data = "return_{}".format(row)))
    markup.add(InlineKeyboardButton("Main Menu", callback_data=f"cb_mainmenu"))
    return markup

def return_loan_confirmation(row):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(text = "No", callback_data = "rno"),
                InlineKeyboardButton(text = "Yes", callback_data = "ryes_{}".format(row)))
    return markup
    
    


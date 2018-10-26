from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def menu_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Create Loan", callback_data=f"cb_createloan"), 
                InlineKeyboardButton("View Loan", callback_data=f"cb_viewloan"), 
                InlineKeyboardButton("Edit Loan", callback_data=f"cb_editloan"))
    return markup

def answer_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Let's Create!", callback_data=f"cb_letscreate"), 
                InlineKeyboardButton("Main Menu", callback_data=f"cb_mainmenu"))
    return markup

def submit_loan_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Edit Loan", callback_data=f"cb_editloan_1"), 
                InlineKeyboardButton("Submit Loan", callback_data=f"cb_submitloan"))
    return markup

def edit_loan_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("by name", callback_data=f"cb_editbyname"), 
                InlineKeyboardButton("by date", callback_data=f"cb_editbydate"),
                InlineKeyboardButton("by item", callback_data=f"cb_editbyitem"))
    return markup

def great_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Great!", callback_data=f"cb_great"))
    return markup
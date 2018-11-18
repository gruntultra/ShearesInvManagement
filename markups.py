from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Main Menu
def menu_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Create Loan", callback_data=f"cb_createloan"), 
                InlineKeyboardButton("View Loan", callback_data=f"cb_viewloan"), 
                InlineKeyboardButton("Edit Loan", callback_data=f"cb_editloan"),
                InlineKeyboardButton("Return Loan", callback_data=f"cb_returnloan"))
    return markup

# Createloan submenu
def createloan_submenu_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Let's Create!", callback_data=f"cb_letscreate"), 
                InlineKeyboardButton("Main Menu", callback_data=f"cb_mainmenu"))
    return markup

# Submit Loan menu during createloan
def submit_loan_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Edit Loan", callback_data=f"cb_editloan_1"), 
                InlineKeyboardButton("Submit Loan", callback_data=f"cb_submitloan"))
    return markup

# Edit loan menu during createloan
def edit_current_loan_markup():
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

def great_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Great!", callback_data=f"cb_great"))
    return markup

# Edit Loan Submenu
def edit_loan_submenu_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Open Google Sheets", url='https://docs.google.com/spreadsheets/d/1FtSe_qt3lgHE8TTkqaSwWfzCcKk8WZ_Rdblw7nXsIWc/edit?usp=sharing'),
               InlineKeyboardButton("Main Menu", callback_data=f"cb_mainmenu"))
    return markup

# View Loan Submenu
def view_loan_submenu_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("View All Loans", callback_data=f"cb_viewallloans"), 
                InlineKeyboardButton("View by Name", callback_data=f"cb_viewbyname"),
                InlineKeyboardButton("View Expired Loans ", callback_data=f"cb_viewexpiredloans"),
                InlineKeyboardButton("View On Google Sheets", url='https://docs.google.com/spreadsheets/d/1FtSe_qt3lgHE8TTkqaSwWfzCcKk8WZ_Rdblw7nXsIWc/edit?usp=sharing'),
                InlineKeyboardButton("Main Menu", callback_data=f"cb_mainmenu"))
    return markup

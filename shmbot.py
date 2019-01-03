import telebot
import config
import dbworker
import time
import operator
import markups as markup

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=["state"])
def cmd_state(message):
    state = dbworker.get_current_state(message.chat.id)
    print("State : " + state + " (" + str(message.chat.id) + ")")

@bot.message_handler(commands=["abort"])
def cmd_abort(message):
    pass

@bot.message_handler(commands=["start"])
def cmd_initialize(message):
    val = dbworker.initialize_user(message, config.States.S_START.value)
    if val is True:
        msg  = "Welcome " + str(message.from_user.username) + " !"
    else:
        msg = "You have been initialized before"
    bot.send_message(chat_id = message.chat.id, text = msg)

@bot.message_handler(commands=["menu"])
def cmd_menu(message):
    try:
        bot.edit_message_text(message_id = message.message_id,
                            chat_id = message.chat.id,
                            text = "Hi! What would you like to do?",
                            reply_markup = markup.main_menu())
    except:
        bot.send_message(message.chat.id, "Hi! What would you like to do?", reply_markup = markup.main_menu())
    dbworker.save_to_db(message.chat.id, "state", config.States.S_MAIN_MENU.value)

#------------------Create Loan Process-------------
@bot.message_handler(commands=["createloan"])
def cmd_createloan(message):
    mid = message.message_id
    cid = message.chat.id
    bot.edit_message_text(message_id=mid, chat_id=cid, parse_mode="Markdown", text="Would you like to create a loan?", reply_markup = markup.create_loan_sub_menu())
    dbworker.save_to_db(message.chat.id, "state", config.States.S_CREATE_LOAN.value)

def proceed_to_create_loan(message):
    bot.send_message(message.chat.id, "Enter Name:")
    dbworker.save_to_db(message.chat.id, "state", config.States.S_CREATE_LOAN_ENTER_NAME.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_CREATE_LOAN_ENTER_NAME.value)
def user_entering_name(message):
    dbworker.save_to_db(message.chat.id, "name", message.text)
    bot.send_message(message.chat.id, "Nice. Enter Block:")
    dbworker.save_to_db(message.chat.id, "state", config.States.S_CREATE_LOAN_ENTER_BLOCK.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_CREATE_LOAN_ENTER_BLOCK.value)
def user_entering_block(message):
    dbworker.save_to_db(message.chat.id, "block", message.text)
    user_entering_item(message, True)
    dbworker.save_to_db(message.chat.id, "state", config.States.S_CREATE_LOAN_ENTER_ITEM.value)

# Item Choosing Process
def user_entering_item(message, send_msg):
    if send_msg is True:
        bot.send_message(chat_id = message.chat.id, text = "Select items:\n\n🏠 Home", reply_markup = markup.main_category_menu())
    else:
        list_of_items = dbworker.get_from_db(message.chat.id, "temp_items")
        bot.edit_message_text(message_id = message.message_id,
                            chat_id = message.chat.id,
                            text = "Select items:\n\n🏠 Home\n\nYour Items 👇\n" + list_of_items,
                            reply_markup = markup.main_category_menu())

def user_finish_entering_item(message):
    bot.send_message(message.chat.id, "Enter Start Date:")
    dbworker.save_to_db(message.chat.id, "state", config.States.S_CREATE_LOAN_ENTER_SDATE.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_CREATE_LOAN_ENTER_SDATE.value)
def user_entering_sdate(message):
    dbworker.save_to_db(message.chat.id, "start_date", message.text)
    bot.send_message(message.chat.id, "Enter End Date")
    dbworker.save_to_db(message.chat.id, "state", config.States.S_CREATE_LOAN_ENTER_EDATE.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_CREATE_LOAN_ENTER_EDATE.value)
def user_entering_edate(message):
    dbworker.save_to_db(message.chat.id, "end_date", message.text)
    bot.send_message(message.chat.id, "Enter Purpose")
    dbworker.save_to_db(message.chat.id, "state", config.States.S_CREATE_LOAN_ENTER_PURPOSE.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_CREATE_LOAN_ENTER_PURPOSE.value)
def user_entering_purpose(message):
    dbworker.save_to_db(message.chat.id, "purpose", message.text)
    dbworker.save_to_db(message.chat.id, "state", config.States.S_CREATE_LOAN_VERIFICATION.value)
    loan_verification(message, True)

def loan_verification(message, send_msg):
    entries = dbworker.get_entry(message.chat.id)
    verify_msg = "*Please verify that the entries are correct!*\n\n" + "*Name:* {}\n" + "*Block:* {}\n" + "*Item:* {}\n" + "*Start Date:* {}\n" + "*End Date:* {}\n" + "*Purpose:* {}\n\n"
    if send_msg is True:
        bot.send_message(chat_id = message.chat.id, 
                        parse_mode = "Markdown", 
                        text  =verify_msg.format(entries[3], entries[4], entries[5], entries[6], entries[7], entries[8]),
                        reply_markup = markup.submit_loan_sub_menu())
    else:
        bot.edit_message_text(message_id = message.message_id,
                            chat_id = message.chat.id, 
                            parse_mode = "Markdown", 
                            text  =verify_msg.format(entries[3], entries[4], entries[5], entries[6], entries[7], entries[8]),
                            reply_markup = markup.submit_loan_sub_menu())

def edit_entry_mode(message):
    entries = dbworker.get_entry(message.chat.id)
    msg = "*Edit current loan*\n\n" + "*Name:* {}\n" + "*Block:* {}\n" + "*Item:* {}\n" + "*Start Date:* {}\n" + "*End Date:* {}\n" + "*Purpose:* {}\n\n"
    bot.edit_message_text(message_id = message.message_id, 
                            chat_id = message.chat.id, 
                            parse_mode = "Markdown",
                            text = msg.format(entries[3], entries[4], entries[5], entries[6], entries[7], entries[8]), 
                            reply_markup = markup.edit_current_loan_sub_menu())
    dbworker.save_to_db(message.chat.id, "state", config.States.S_CREATE_LOAN_EDIT_MODE.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_CREATE_LOAN_SAVE_ENTRY.value)
def save_editted_entry(message):
    field = dbworker.get_field(message.chat.id)
    dbworker.save_to_db(message.chat.id, field, message.text)
    dbworker.save_to_db(message.chat.id, "state", config.States.S_CREATE_LOAN_VERIFICATION.value)
    loan_verification(message, True)

def entry_submission(message):
    entries = dbworker.get_entry(message.chat.id)
    entry_list = [entries[3], entries[4], entries[5], entries[6], entries[7], entries[8], entries[0]]
    result = dbworker.submit_loan_gsheets(entry_list)
    if result is True:
        msg = "*Loan created successfully!*\n\n" + "*Name:* {}\n" + "*Block:* {}\n" + "*Item:* {}\n" + "*Start Date:* {}\n" + "*End Date:* {}\n" + "*Purpose:* {}\n\n" + "_by {}_" 
        bot.edit_message_text(message_id = message.message_id ,
                            chat_id = message.chat.id, 
                            parse_mode= 'markdown',
                            text = msg.format(entries[3], entries[4], entries[5], entries[6], entries[7], entries[8], entries[0]))
        dbworker.clear_fields(message.chat.id)
        dbworker.save_to_db(message.chat.id, "state", config.States.S_CREATE_LOAN_COMPLETE.value)
    else:
        bot.send_message(chat_id = message.chat.id, text = "Failed to create loan")
#------------------Create Loan Process-------------

#------------------Edit Loan Process---------------
@bot.message_handler(commands=["editloan"])
def cmd_editloan(message):
    bot.edit_message_text(message_id = message.message_id ,
                        chat_id = message.chat.id,
                        text='Edit on google sheets.', 
                        reply_markup = markup.edit_loan_main_menu())
    dbworker.save_to_db(message.chat.id, "state", config.States.S_EDIT_LOAN.value)
#------------------Edit Loan Process---------------

#------------------Return Loan Process---------------
@bot.message_handler(commands=["returnloan"])
def cmd_returnloan(message):
    expired_loans, row = dbworker.get_expiry_loans()
    bot.edit_message_text(message_id = message.message_id ,
                        chat_id = message.chat.id,
                        text="Select any to return loan:", 
                        reply_markup = markup.return_loan_menu(expired_loans, row))
    dbworker.save_to_db(message.chat.id, "state", config.States.S_RETURN_LOAN.value)
#------------------Return Loan Process---------------

# All the buttons handler
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # Main Menu buttons
    if call.data == "cb_createloan":
        bot.answer_callback_query(call.id)
        cmd_createloan(call.message)
    elif call.data == "cb_editloan":
        bot.answer_callback_query(call.id)
        cmd_editloan(call.message)
    elif call.data == "cb_returnloan":
        bot.answer_callback_query(call.id)
        cmd_returnloan(call.message)
    # Back to Main Menu button
    elif call.data == "cb_mainmenu":
        bot.answer_callback_query(call.id)
        cmd_menu(call.message)
    # Let's Create Loan Button
    elif call.data == "cb_letscreate":
        bot.answer_callback_query(call.id)
        proceed_to_create_loan(call.message)
    # Submit or Edit loan buttons in Create Loan
    elif call.data == "cb_editloan_cl":
        bot.answer_callback_query(call.id)
        edit_entry_mode(call.message)
    elif call.data == "cb_submitloan_cl":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(message_id = call.message.message_id, chat_id = call.message.chat.id, text = "Submitting...")
        entry_submission(call.message)
    # Edit loan during create loan process buttons
    elif call.data == "cb_editname":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id = call.message.chat.id, text = "Send me the new name.")
        dbworker.set_field(call.message.chat.id, "name")
        dbworker.save_to_db(call.message.chat.id, "state", config.States.S_CREATE_LOAN_SAVE_ENTRY.value)
    elif call.data == "cb_editblock":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id = call.message.chat.id, text = "Send me the new block.")
        dbworker.set_field(call.message.chat.id, "block")
        dbworker.save_to_db(call.message.chat.id, "state", config.States.S_CREATE_LOAN_SAVE_ENTRY.value)
    elif call.data == "cb_edititem":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id = call.message.chat.id, text = "Send me the new item.")
        dbworker.set_field(call.message.chat.id, "item")
        dbworker.save_to_db(call.message.chat.id, "state", config.States.S_CREATE_LOAN_SAVE_ENTRY.value)
    elif call.data == "cb_editstartdate":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id = call.message.chat.id, text = "Send me the new start date.")
        dbworker.set_field(call.message.chat.id, "start_date")
        dbworker.save_to_db(call.message.chat.id, "state", config.States.S_CREATE_LOAN_SAVE_ENTRY.value)
    elif call.data == "cb_editenddate":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id = call.message.chat.id, text = "Send me the new end date.")
        dbworker.set_field(call.message.chat.id, "end_date")
        dbworker.save_to_db(call.message.chat.id, "state", config.States.S_CREATE_LOAN_SAVE_ENTRY.value)
    elif call.data == "cb_editpurpose":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id = call.message.chat.id, text = "Send me the new purpose.")
        dbworker.set_field(call.message.chat.id, "purpose")
        dbworker.save_to_db(call.message.chat.id, "state", config.States.S_CREATE_LOAN_SAVE_ENTRY.value)
    elif call.data == "cb_backtoverifyloan":
        bot.answer_callback_query(call.id)
        loan_verification(call.message, False)
    # Item Choosing
    elif call.data.startswith("cat_"):
        bot.answer_callback_query(call.id)
        category = call.data.split("_")[1]
        dbworker.save_to_db(call.message.chat.id, "temp_category", category)
        list_of_items = dbworker.get_from_db(call.message.chat.id, "temp_items")
        bot.edit_message_text(message_id = call.message.message_id,
                            chat_id = call.message.chat.id,
                            text = "🏠 > " + category + "\n\nYour Items:\n" + list_of_items,
                            reply_markup = markup.items_menu(call.data))
    elif call.data.startswith("item_"):
        bot.answer_callback_query(call.id)
        item = call.data.split("_")[1]
        quantity = call.data.split("_")[2]
        bot.edit_message_reply_markup(message_id = call.message.message_id,
                                    chat_id = call.message.chat.id,
                                    reply_markup = markup.quantity_choosing(quantity, item))
    elif call.data.startswith("q_"):
        bot.answer_callback_query(call.id)
        quantity = call.data.split("_")[1]
        item = call.data.split("_")[2]
        db_category = dbworker.get_from_db(call.message.chat.id, "temp_category")
        category = "cat_" + db_category
        dbworker.update_loan_gsheets(db_category, item, quantity, operator.__sub__, operator.__add__)
        result = dbworker.check_overlap(call.message.chat.id, item)
        if result is True:
            updated_list = dbworker.edit_quantity(call.message.chat.id, item, quantity)
            bot.edit_message_text(message_id = call.message.message_id,
                                chat_id = call.message.chat.id,
                                text = "🏠 > " + db_category + "\n\nYour Items:\n" + updated_list,
                                reply_markup = markup.items_menu(category))
        else:
            list_of_items = dbworker.save_items_temp(call.message.chat.id, item, quantity)
            bot.edit_message_text(message_id = call.message.message_id,
                                chat_id = call.message.chat.id,
                                text = "🏠 > " + db_category + "\n\nYour Items:\n" + list_of_items,
                                reply_markup = markup.items_menu(category))
    elif call.data == "back_to_main_cat":
        bot.answer_callback_query(call.id)
        user_entering_item(call.message, False)
    elif call.data == "back_to_items":
        bot.answer_callback_query(call.id)
        db_category = dbworker.get_from_db(call.message.chat.id, "temp_category")
        category = "cat_" + db_category
        list_of_items = dbworker.get_from_db(call.message.chat.id, "temp_items")
        bot.edit_message_text(message_id = call.message.message_id,
                            chat_id = call.message.chat.id,
                            text = "🏠 > " + db_category + "\n\nYour Items:\n" + list_of_items,
                            reply_markup = markup.items_menu(category))
    elif call.data == "cb_remove_items":
        bot.answer_callback_query(call.id)
        list_of_existing_items = dbworker.get_from_db(call.message.chat.id, "temp_items")
        bot.edit_message_text(message_id = call.message.message_id,
                            chat_id = call.message.chat.id,
                            text = "Select the items that you want to remove:\n" + list_of_existing_items,
                            reply_markup = markup.item_removal(call.message.chat.id, list_of_existing_items))
    elif call.data.startswith("remove_"):
        bot.answer_callback_query(call.id)
        item_to_be_removed = call.data.split("_")[1]
        item = item_to_be_removed.split(" ")[0]
        quantity = item_to_be_removed.split(" ")[1].replace("x", "")
        existing_items = dbworker.get_from_db(call.message.chat.id, "temp_items")
        list_of_existing_items = existing_items.split("\n")
        if item_to_be_removed in list_of_existing_items:
            list_of_existing_items.remove(item_to_be_removed)
        new_list = "\n".join(list_of_existing_items)
        db_category = dbworker.get_from_db(call.message.chat.id, "temp_category")
        dbworker.update_loan_gsheets(db_category, item, quantity, operator.__add__, operator.__sub__)
        dbworker.save_to_db(call.message.chat.id, "temp_items", new_list)
        bot.edit_message_text(message_id = call.message.message_id,
                            chat_id = call.message.chat.id,
                            text = "Select the items that you want to remove:\n" + new_list,
                            reply_markup = markup.item_removal(call.message.chat.id, new_list))
    elif call.data == "cb_submit_items":
        bot.answer_callback_query(call.id)
        is_empty = dbworker.if_empty(call.message.chat.id)
        if is_empty:
            bot.send_message(chat_id = call.message.chat.id, text = "You have not selected any items yet")
        else:
            list_of_items = dbworker.get_from_db(call.message.chat.id, "temp_items")
            dbworker.save_to_db(call.message.chat.id, "item", list_of_items)
            user_finish_entering_item(call.message)
            bot.edit_message_text(message_id = call.message.message_id,
                                chat_id = call.message.chat.id,
                                text = "Submitted Successfully!")
            dbworker.save_to_db(call.message.chat.id, "state", config.States.S_CREATE_LOAN_ENTER_SDATE.value)
    # Return Loan
    elif call.data.startswith("return_"):
        bot.answer_callback_query(call.id)
        row = call.data.split("_")[1]
        msg = dbworker.get_expired_user_detail(row)
        bot.edit_message_text(message_id = call.message.message_id,
                                chat_id = call.message.chat.id,
                                parse_mode = "Markdown",
                                text = msg,
                                reply_markup = markup.return_loan_confirmation(row))
    elif call.data.startswith("ryes_"):
        bot.answer_callback_query(call.id)
        row = call.data.split("_")[1]
        dbworker.move_expired_to_history(int(row))
        expired_loans, rows = dbworker.get_expiry_loans()
        bot.edit_message_text(message_id = call.message.message_id,
                                chat_id = call.message.chat.id,
                                text = "Select any to return loan:",
                                reply_markup = markup.return_loan_menu(expired_loans, rows))


if __name__ == "__main__":
    bot.polling(none_stop=True)
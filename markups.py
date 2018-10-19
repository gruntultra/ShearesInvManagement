from telebot import types

start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
itembtn_createloan = types.KeyboardButton('Create loan')
itembtn_hello = types.KeyboardButton("Exit")
start_markup.row(itembtn_createloan, itembtn_hello)
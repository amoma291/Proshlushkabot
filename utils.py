from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def get_kb():
    btns = [
        ['Опубликовать пост'],
        ['Связаться с админом'],
    ]
    return ReplyKeyboardMarkup(btns)


def get_yes_or_no_inline_kb():
    btns = [
        [
            InlineKeyboardButton('✅', callback_data='accept'),
            InlineKeyboardButton('❌', callback_data='decline'),
        ],
    ]
    return InlineKeyboardMarkup(btns)

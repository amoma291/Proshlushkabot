from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, ConversationHandler

import config
from json_funcs import append_to_json, read_json, remove_question_from_json
import utils


def answer_to_user(update: Update, context: CallbackContext):
    if update.message.chat.id in config.ADMINS and update.message.reply_to_message:
        data = read_json()  # {'2224': 6587453534}
        message_id = str(update.message.reply_to_message.message_id)
        forward_id = data.get(message_id)  # None
        if forward_id:
            remove_question_from_json(message_id)
            try:
                text = f'Ответ от админа:\n{update.message.text}'
                context.bot.send_message(chat_id=forward_id, text=text)
            except BadRequest:
                update.message.reply_text('Пользователь заблокировал бота')


def greet_user(update: Update, context: CallbackContext):
    name = update.message.chat.first_name
    if len(name) == 1 and ord(name) == 4448:
        name = update.message.chat.username
        if len(name) == 1 and ord(name) == 4448:
            name = 'друг'
    update.message.reply_text(
        f'Привет, {name.capitalize()}! Выбери интересующий пункт',
        reply_markup=utils.get_kb(),
        )


def publish_post(update: Update, context: CallbackContext):
    update.callback_query.answer('Публикую пост...')  # , show_alert=True)
    data = update.callback_query.data
    text = update.callback_query.message.text
    photo = update.callback_query.message.photo
    video = update.callback_query.message.video
    if text:
        text = text.replace('Опубликовать данный пост?\n\n', '')
    elif photo:
        text = update.callback_query.message.caption
        photo = update.callback_query.message.photo[-1]
        if text:
            text = text.replace('Опубликовать данный пост?\n\n', '')
    elif video:
        text = update.callback_query.message.caption
        if text:
            text = text.replace('Опубликовать данный пост?\n\n', '')
    if data == 'accept':
        if not photo and not video:
            context.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=text,
            )
        elif video:
            context.bot.send_video(
                chat_id=config.CHANNEL_ID,
                video=video,
                caption=text,
            )
        else:
            context.bot.send_photo(
                chat_id=config.CHANNEL_ID,
                photo=photo,
                caption=text,
            )
    elif data == 'decline':
        try:
            text = text + '\n\n❌ПОСТ ОТКЛОНЕН❌'
        except TypeError:
            text = ''
        if not photo and not video:
            update.callback_query.message.edit_text(
                text=text,
                reply_markup=None,
            )
        else:
            update.callback_query.message.edit_caption(
                caption=text,
                reply_markup=None,
            )


def send_message_to_admin(update: Update, context: CallbackContext):
    update.message.reply_text('Ваше сообщение передано админу, ожидайте...')
    user_id = update.message.chat.id

    text = update.message.text
    for admin in config.ADMINS:
        message = context.bot.send_message(
            chat_id=admin,
            text=text,
        )

    message_id = message.message_id
    new_data = {message_id: user_id}   # {17: 345465763452}
    append_to_json(new_data)
    return ConversationHandler.END


def send_post_to_admin(update: Update, context: CallbackContext):
    update.message.reply_text('Ваш пост передан на модерацию, ожидайте...')
    photo = update.message.photo
    video = update.message.video
    if photo:
        photo = update.message.photo[-1]
        caption = update.message.caption
        if caption:
            caption = 'Опубликовать данный пост?\n\n' + caption
        for admin in config.ADMINS:
            context.bot.send_photo(
                chat_id=admin,
                photo=photo,
                caption=caption,
                reply_markup=utils.get_yes_or_no_inline_kb(),
            )
    elif video:
        caption = update.message.caption
        if caption:
            caption = 'Опубликовать данный пост?\n\n' + caption
        for admin in config.ADMINS:
            context.bot.send_video(
                chat_id=admin,
                video=video,
                caption=caption,
                reply_markup=utils.get_yes_or_no_inline_kb(),
            )
    else:
        text = update.message.text
        text = 'Опубликовать данный пост?\n\n' + text
        for admin in config.ADMINS:
            context.bot.send_message(
                chat_id=admin,
                text=text,
                reply_markup=utils.get_yes_or_no_inline_kb(),
            )
    return ConversationHandler.END


def waiting_for_message(update: Update, context: CallbackContext):
    update.message.reply_text('Введите текст сообщения, а я передам его админу')
    return 'send_message_to_admin'


def waiting_for_post(update: Update, context: CallbackContext):
    update.message.reply_text('Отправьте текст поста, фото с подписью или видео')
    return 'send_post_to_admin'


def wrong_message(update: Update, context: CallbackContext):
    update.message.reply_text('Отправьте текст, фото c подписью или видео')
    return 'send_to_admin'

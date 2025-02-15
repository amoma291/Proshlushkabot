from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, ConversationHandler

import config
from json_funcs import append_to_json, read_json, remove_question_from_json
import utils


def answer_to_user(update: Update, context: CallbackContext):
    if update.message.chat.id in config.ADMINS and update.message.reply_to_message:
        data = read_json('questions.json')
        message_id = str(update.message.reply_to_message.message_id)
        forward_id = data.get(message_id)
        if forward_id:
            remove_question_from_json('questions.json', message_id)
            try:
                text = f'Ответ от админа:\n{update.message.text}'
                context.bot.send_message(chat_id=forward_id, text=text)
            except BadRequest:
                update.message.reply_text('Пользователь заблокировал бота')
    else:
        if not update.message.forward_from_chat:
            text = update.message.text
            photo = update.message.photo
            video = update.message.video

            context.user_data['first_message'] = {
                'message_id': update.message.message_id,
                'user_id': update.message.chat.id,
            }

            if photo:
                context.user_data['first_message']['reply_photo'] = photo[-1]
            elif video:
                context.user_data['first_message']['reply_video'] = video
            else:
                context.user_data['first_message']['reply_text'] = text
        else:
            if update.message.forward_from_chat.id == config.CHANNEL_ID:
                context.user_data['second_message'] = {
                    'message_id': update.message.message_id,
                    'forward_message_id': update.message.forward_from_message_id,
                }
        if context.user_data.get('first_message') and context.user_data.get('second_message'):
            send_post_to_admin(update, context)


def greet_user(update: Update, context: CallbackContext):
    """
    Функция реагирует на команду /start и приветствует для пользователя

    Args:
        update (Update): Информация о текущем сообщении
        cotext (CallbackContext): контекст бота

    Returns:
        ConversationHandler.END: окончание диалог
    """
    name = update.message.chat.first_name
    if len(name) == 1 and ord(name) == 4448:
        name = update.message.chat.username
        if len(name) == 1 and ord(name) == 4448:
            name = 'друг'
    update.message.reply_text(
        f'Привет, {name.capitalize()}! Выбери интересующий пункт',
        reply_markup=utils.get_kb(),
        )
    return ConversationHandler.END


def publish_post(update: Update, context: CallbackContext):
    update.callback_query.answer('Публикую пост...')
    data = update.callback_query.data
    text = update.callback_query.message.text
    photo = update.callback_query.message.photo
    video = update.callback_query.message.video
    if photo:
        text = update.callback_query.message.caption or ''
        photo = update.callback_query.message.photo[-1]
    elif video:
        text = update.callback_query.message.caption or ''

    if data == 'accept':
        text_for_admin = text + '\n\n✅ПОСТ ОПУБЛИКОВАН✅'
        reply_to_message_id = None
        if 'second_message' in context.user_data:
            reply_to_message_id = context.user_data['second_message'].get('forward_message_id')
        if not photo and not video:
            context.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=text,
                reply_to_message_id=reply_to_message_id,
            )
        elif video:
            context.bot.send_video(
                chat_id=config.CHANNEL_ID,
                video=video,
                caption=text,
                reply_to_message_id=reply_to_message_id,
            )
        else:
            context.bot.send_photo(
                chat_id=config.CHANNEL_ID,
                photo=photo,
                caption=text,
                reply_to_message_id=reply_to_message_id,
            )
    elif data == 'decline':
        text_for_admin = text + '\n\n❌ПОСТ ОТКЛОНЕН❌'

    if not photo and not video:
        update.callback_query.message.edit_text(
            text=text_for_admin,
            reply_markup=None,
        )
    else:
        update.callback_query.message.edit_caption(
            caption=text_for_admin,
            reply_markup=None,
        )
    if 'first_message' in context.user_data:
        del context.user_data['first_message']
    if 'second_message' in context.user_data:
        del context.user_data['second_message']


def send_message_to_admin(update: Update, context: CallbackContext):
    text = update.message.text
    if text not in ('Опубликовать пост', 'Связаться с админом'):
        update.message.reply_text('Ваше сообщение передано админу, ожидайте...')
        user_id = update.message.chat.id

        text = update.message.text
        for admin in config.ADMINS:
            message = context.bot.send_message(
                chat_id=admin,
                text=text,
            )

        message_id = message.message_id
        new_data = {message_id: user_id}
        append_to_json(new_data)
    else:
        update.message.reply_text('Диалог с админом прерван')
    return ConversationHandler.END


def send_post_to_admin(update: Update, context: CallbackContext):
    update.message.reply_text('Ваш пост передан на модерацию, ожидайте...')
    photo = update.message.photo
    video = update.message.video
    if photo and not context.user_data.get('second_message'):
        photo = update.message.photo[-1]
        caption = update.message.caption
        for admin in config.ADMINS:
            context.bot.send_photo(
                chat_id=admin,
                photo=photo,
                caption=caption,
                reply_markup=utils.get_yes_or_no_inline_kb(),
            )
    elif video and not context.user_data.get('second_message'):
        caption = update.message.caption
        for admin in config.ADMINS:
            context.bot.send_video(
                chat_id=admin,
                video=video,
                caption=caption,
                reply_markup=utils.get_yes_or_no_inline_kb(),
            )
    else:
        if context.user_data.get('second_message'):
            for admin in config.ADMINS:
                context.bot.forward_message(
                    chat_id=admin,
                    from_chat_id=config.CHANNEL_ID,
                    message_id=context.user_data['second_message']['forward_message_id']
                )
            if 'reply_text' in context.user_data['first_message']:
                text = context.user_data['first_message']['reply_text']
                for admin in config.ADMINS:
                    context.bot.send_message(
                        chat_id=admin,
                        text=text,
                        reply_markup=utils.get_yes_or_no_inline_kb(),
                    )
            elif 'reply_photo' in context.user_data['first_message']:
                photo = context.user_data['first_message']['reply_photo']
                for admin in config.ADMINS:
                    context.bot.send_photo(
                        chat_id=admin,
                        photo=photo,
                        reply_markup=utils.get_yes_or_no_inline_kb(),
                    )
            elif 'reply_video' in context.user_data['first_message']:
                video = context.user_data['first_message']['reply_video']
                for admin in config.ADMINS:
                    context.bot.send_video(
                        chat_id=admin,
                        video=video,
                        reply_markup=utils.get_yes_or_no_inline_kb(),
                    )
        else:
            text = update.message.text
            if text not in ('Опубликовать пост', 'Связаться с админом'):
                for admin in config.ADMINS:
                    context.bot.send_message(
                        chat_id=admin,
                        text=text,
                        reply_markup=utils.get_yes_or_no_inline_kb(),
                    )
            else:
                update.message.reply_text('Создание поста прервано')
    return ConversationHandler.END


def waiting_for_message(update: Update, context: CallbackContext):
    update.message.reply_text('Введите текст сообщения, а я передам его админу')
    return 'send_message_to_admin'


def waiting_for_post(update: Update, context: CallbackContext):
    update.message.reply_text('Введите текст поста либо приложите фото с подписью')
    return 'send_post_to_admin'


def wrong_message(update: Update, context: CallbackContext):
    update.message.reply_text('Отправьте текст, фото или видеокружок')
    return 'send_to_admin'

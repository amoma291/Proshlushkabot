import os

from dotenv import load_dotenv
from telegram.ext import (Updater, CallbackQueryHandler, CommandHandler,
                          ConversationHandler, MessageHandler, Filters)

import handlers

load_dotenv()


def main():
    bot = Updater(os.environ.get('API_TOKEN'))
    dp = bot.dispatcher
    dp.add_handler(CommandHandler('start', handlers.greet_user))
    dp.add_handler(CallbackQueryHandler(handlers.publish_post))

    conv = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^(Опубликовать пост)$'), handlers.waiting_for_post),
            MessageHandler(Filters.regex('^(Связаться с админом)$'), handlers.waiting_for_message),
        ],
        states={
            'send_post_to_admin': [MessageHandler(
                Filters.text | Filters.video | Filters.photo,
                handlers.send_post_to_admin)],
            'send_message_to_admin': [MessageHandler(Filters.text, handlers.send_message_to_admin)],
        },
        fallbacks=[
            MessageHandler(Filters.sticker, handlers.wrong_message),
        ],
    )
    dp.add_handler(conv)

    dp.add_handler(MessageHandler(
        Filters.text | Filters.photo | Filters.video,
        handlers.answer_to_user))

    bot.start_polling()
    bot.idle()


if __name__ == '__main__':
    main()

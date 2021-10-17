from config import Config
import logging

import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CONFIG = None  # a dictionary that stores the whole configuration of the bot


def get_help_user(update: Update, context: CallbackContext) -> None:
    msg = "<b>User Help Page</b>" + '\n'
    msg += "/provision - To get a virtual machine" + '\n'
    msg += "/help      - Gives this page" + '\n'
    update.message.reply_text(msg, parse_mode='HTML')


def get_help_master(update: Update, context: CallbackContext) -> None:
    msg = "<b>Master Help Page</b>" + '\n'
    msg += "/list - list all the users in the database"
    msg += "/help - to output this help message" + '\n'
    update.message.reply_text(msg, parse_mode='HTML')


def help_command(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if username == CONFIG['master_telegram_id']:
        get_help_master(update, context)
    else:
        get_help_user(update, context)


def main():
    global CONFIG
    c = Config('config.cfg')
    CONFIG = c.get_data()

    updater = Updater(CONFIG['token'])
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("help", help_command))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

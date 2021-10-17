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
ACCEPT_AND_REQUEST_MASTER = 2


def get_help_user(update: Update, context: CallbackContext) -> None:
    msg = "<b>User Help Page</b>" + '\n'
    msg += "/provision - To get a virtual machine" + '\n'
    msg += "/help      - Gives this page" + '\n'
    update.message.reply_text(msg, parse_mode='HTML')


def get_help_master(update: Update, context: CallbackContext) -> None:
    msg = "<b>Master Help Page</b>" + '\n'
    msg += "/list - list all the users in the database\n"
    msg += "/help - to output this help message" + '\n'
    update.message.reply_text(msg, parse_mode='HTML')


def help_command(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if username == CONFIG['master_telegram_id']:
        get_help_master(update, context)
    else:
        get_help_user(update, context)


def start_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_Text("Use /help to get the help message")


def provision_command(update: Update, context: CallbackContext) -> None:
    reply_keyboard = [['ubuntu', 'redhat']]

    update.message.reply_text(
        'Choose your operating system: ',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Operating System?'
        ),
    )

    return ACCEPT_AND_REQUEST_MASTER


def get_full_name(update: Update) -> str:
    '''
    returns the full name of a teacher, given an update
    '''
    name = update.effective_user.first_name
    if update.effective_user.last_name:
        name += ' ' + update.effective_user.last_name
    return name


def send_to_master(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Your request is being processed!!'
                              '\nI will notify you when it is finished.'
                              )

    # message to be sent to the master
    msg = f"User: <b>{get_full_name(update)}</b>\n"
    msg += f'wants access to the operating system: <b>{update.message.text}</b>\n'
    msg += '\nDo you want me to give access to him??'
    user_id = update.message.from_user.id
    reply_keyboard = [[f'yes allow {user_id}', f'no, do not allow {user_id}']]

    context.bot.send_message(
        chat_id=f"@{CONFIG['master_telegram_id']}",
        text=msg,
        parse_mode='HTML',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
        )
    )

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("/cancel called!! shutting down!!",
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    global CONFIG
    c = Config('config.cfg')
    CONFIG = c.get_data()

    updater = Updater(CONFIG['token'])
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('provision', provision_command)],
        states={
            ACCEPT_AND_REQUEST_MASTER: [MessageHandler(
                Filters.regex('^(ubuntu|redhat)$'), send_to_master)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

import telebot
from telebot import types

from pveapi import proxmox
from pveapi import power_op
from util import config_parser
import db
import time

from pprint import pprint

bot = telebot.TeleBot(config_parser.CONFIG['bot']['token'])
# conn= db.create_connection(db.db_file)

# TODO
# - command handler for start and help 

@bot.message_handler(commands=['control'])
def control(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    itembtn1 = types.KeyboardButton('Power On')
    itembtn2 = types.KeyboardButton('Power Off')
    itembtn3 = types.KeyboardButton('Reboot')
    itembtn4 = types.KeyboardButton("STATUS")
    markup.add(itembtn1, itembtn2)
    markup.add(itembtn3)
    markup.add(itembtn4)
    bot.send_message(message.chat.id, "Select Operation:", reply_markup=markup)

@bot.message_handler(regexp='(^Power On$|^Power Off$|^Reboot$)')
def power_control(message):
    
    # Read user id from db
    conn= db.create_connection(db.db_file)
    cur = conn.cursor()
    cur.execute(db.sql_command.sql_select_user_from_machine, (message.chat.id,))
    data = cur.fetchone()
    # close cursor

    if data :
        bot.send_chat_action(message.chat.id, 'typing')
        POWR_FUNCS[message.text](message, data)
    else :
        bot.send_message(message.chat.id, "You have no vm assigned to you. Please /command to get a vm")

    conn.close()

def power_on_machine(message , cur, data):

    msg = power_op.power_on(proxmox , config_parser.CONFIG['proxmox']['node'] , data[0]) 
    if msg['success'] == 1 :
        # Machine has been powered on
        bot.send_message(message.chat.id ,"Your vm has powered ON")
    else :
        bot.send_message(message.chat.id, msg['msg'])


def power_off_machine(message, data):

    msg = power_op.power_off(proxmox , config_parser.CONFIG['proxmox']['node'] , data[0])
    if msg['success'] == 1 :
        # Machine has been turned  off
        bot.send_message(message.chat.id ,"Your vm has powered off")
    else :
        bot.send_message(message.chat.id, msg['msg'])

def reboot_machine(message ,  data):

    msg = power_op.reboot(proxmox , config_parser.CONFIG['proxmox']['node'] , data[0])
    if msg['success'] == 1 :
        # Machine has been rebooted
        bot.send_message(message.chat.id ,"Your vm has rebooted")
        # Update the message once the machine has rebooted
    else :
        bot.send_message(message.chat.id, msg['msg'])

def machine_status(message, data) :
    pass
    # uptime , ip addresses , load 

# Dispatcher
POWR_FUNCS={"Power On" : power_on_machine, "Power Off" : power_off_machine , "Reboot" : reboot_machine}



# if __name__  == 'main' :
bot.infinity_polling()
   
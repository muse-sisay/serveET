import telebot
from telebot import types

from pveapi import proxmox
from pveapi import power_op
from pveapi import status

from util import CONFIG
from util import util
from util import humanBytes

from res import STRINGS

from db import db_file
from db import helper

import datetime
import logging

from pprint import pprint

bot = telebot.TeleBot(CONFIG['bot']['token'])
# logger = telebot.logger
# telebot.logger.setLevel(logging.DEBUG)


# - command handler for start and help 
@bot.message_handler(commands=['start', 'help'])
def start(message):
    msg = util.string_format(STRINGS['STR_START'], message.chat.first_name)
    bot.send_message(message.chat.id , msg , parse_mode="MarkdownV2")

@bot.message_handler(commands=['control'])
def control(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    itembtn1 = types.KeyboardButton('Power On')
    itembtn2 = types.KeyboardButton('Power Off')
    itembtn3 = types.KeyboardButton('Reboot')
    itembtn4 = types.KeyboardButton("status")
    markup.add(itembtn1, itembtn2)
    markup.add(itembtn3)
    markup.add(itembtn4)
    
    msg = util.string_format(STRINGS['STR_SELECT_OP'], '')
    bot.send_message(message.chat.id, msg, reply_markup=markup ,  parse_mode="MarkdownV2")

@bot.message_handler(regexp='(^Power On$|^Power Off$|^Reboot$|^status$)')
def power_control(message):

    # Read user id from db
    data=''
    try : 
        conn = helper.create_connection(db_file)
        data = helper.get_user_from_machine(conn, message.chat.id)
        conn.close()
    except Error as e :
        print(e)


    if data :
        bot.send_chat_action(message.chat.id, 'typing')
        POWR_FUNCS[message.text](message, data )
    else :
        msg = util.string_format( STRINGS['STR_NO_VM_ASSIGNED'], '')
        bot.send_message(message.chat.id,msg, parse_mode="MarkdownV2")

def power_on_machine(message , data):

    msg = power_op.power_on(proxmox , CONFIG['proxmox']['node'] , data[0]) 
    if msg['success'] == 1 :
        # Machine has been powered on
        msg = util.string_format(STRINGS['STR_VM_POWER_ON'], '')
        bot.send_message(message.chat.id ,msg, parse_mode="MarkdownV2")
    else :
        bot.send_message(message.chat.id, msg['msg'])


def power_off_machine(message, data):

    msg = power_op.power_off(proxmox , CONFIG['proxmox']['node'] , data[0])
    if msg['success'] == 1 :
        # Machine has been turned  off
        msg = util.string_format(STRINGS['STR_VM_POWER_OFF'], '')
        bot.send_message(message.chat.id ,msg, parse_mode="MarkdownV2")
    else :
        bot.send_message(message.chat.id, msg['msg'])

def reboot_machine(message ,  data):

    msg = power_op.reboot(proxmox , CONFIG['proxmox']['node'] , data[0])
    if msg['success'] == 1 :
        # Machine has been rebooted
        msg = util.string_format(STRINGS['STR_VM_POWER_REBOOT_START'], '')
        bot.send_message(message.chat.id ,msg, parse_mode="MarkdownV2")
        # Update the message once the machine has rebooted
    else :
        bot.send_message(message.chat.id, msg['msg'])

def machine_status(message, data) :
    vm_id = data[0]
    # power_on or off status
    stat = status.get_vmstat(proxmox, CONFIG['proxmox']['node'], vm_id)
    
    power_status = stat['msg']['status']
    
    msg = util.string_format(STRINGS['STR_VM_STATUS_POWER'], power_status)

    if power_status == "running" :
        
        os_info = status.get_os_info(proxmox, CONFIG['proxmox']['node'], vm_id)
        nics = status.get_ip_address(proxmox, CONFIG['proxmox']['node'], vm_id)
        # os_info
        if os_info['success']  == 0 :
            os_info = 'unkown'
        else :
            os_info = os_info['msg']
        # uptime
        uptime = str(datetime.timedelta( seconds=stat['msg']['uptime'] ))
     
        # net usage
        net_in = humanBytes.format( stat['msg']['netin'], precision=2)
        net_out= humanBytes.format(stat['msg']['netout'], precision=2)
        # load 

        msg += util.string_format(STRINGS['STR_VM_STATUS'], os_info, uptime , net_in , net_out)

        # ip addresses (local , tailscale)
        if nics['success'] == 1 :
            for nic  in nics['msg']:
                msg += util.string_format(STRINGS['STR_VM_STATUS_IP'], nic['if'] , nic['ip'] )
       
    else :
        msg += util.string_format(STRINGS['STR_VM_STATUS_POWER_ON_MSG'],'')

    bot.send_message(message.chat.id ,msg, parse_mode="MarkdownV2")   


# Dispatcher
POWR_FUNCS={"Power On" : power_on_machine, "Power Off" : power_off_machine , "Reboot" : reboot_machine, "status" : machine_status}


@bot.message_handler(commands=['login'])
def login_url(message):

    
    bot.send_chat_action(message.chat.id, 'typing')
    # Read user id from db
    data=''
    try : 
        conn = helper.create_connection(db_file)
        data = helper.get_user_from_machine(conn, message.chat.id)
        conn.close()
    except Error as e :
        print(e)

    power_status = status.get_vmstat(proxmox, CONFIG['proxmox']['node'], data[0])['msg']['status']
    
    if power_status == 'running' :
        # Get ssh login 
        ipv4_address = status.get_local_ip(proxmox , CONFIG['proxmox']['node'], data[0] )
        url = util.get_login_url(ipv4_address['msg'])
        
        msg = util.string_format(STRINGS['STR_LOGIN'], url)
        bot.send_message(message.chat.id ,msg, parse_mode="MarkdownV2")
    else:
        msg = util.string_format(STRINGS['STR_LOGIN_POWERED_OFF'], '')
        bot.send_message(message.chat.id ,msg, parse_mode="MarkdownV2")

# - command handler for start and help 
@bot.message_handler(func=lambda m: True)
def maintenance(message):

    msg= util.string_format(STRINGS['STR_MAINTENACE'], '')
    bot.send_message(message.chat.id,msg, parse_mode="MarkdownV2" )

# if __name__  == 'main' :
bot.infinity_polling()
   
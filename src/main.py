import telebot
from telebot import types
from telebot import custom_filters

from pveapi import proxmox
from pveapi import power_op
from pveapi import status
from pveapi import vm

from util import CONFIG
from util import util
from util import humanBytes

from res import STRINGS

from db import db_file
from db import helper

import datetime
import logging
import sqlite3

from pprint import pprint

bot = telebot.TeleBot(CONFIG['bot']['token'])
# logger = telebot.logger
# telebot.logger.setLevel(logging.DEBUG)


# - command handler for start and help 
@bot.message_handler(commands=['start', 'help'])
def start(message):
    msg = util.string_format(STRINGS['STR_START'], message.chat.first_name)
    bot.send_message(message.chat.id , msg , parse_mode="MarkdownV2")

@bot.message_handler(commands=['provision'])
def provision(message):
    
    data_machine=None
    data_request=None
    try : 
        conn = helper.create_connection(db_file)
        data_machine = helper.get_user_from_machine(conn, message.chat.id)
        data_request = helper.get_request(conn,message.chat.id )
        conn.close()
    except sqlite3.Error as e :
        print(e)

    if not ( data_machine or data_request):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        itembtn1 = types.KeyboardButton(STRINGS['STR_TERMS_OF_SERVICE_ACCEPT'])
        itembtn2 = types.KeyboardButton(STRINGS['STR_TERMS_OF_SERVICE_REJECT'])
        markup.add(itembtn1 , itembtn2)

        msg= util.string_format(STRINGS['STR_TERMS_OF_SERVICE'], '')
        bot.send_message(message.chat.id, msg, reply_markup=markup ,  parse_mode="MarkdownV2")
        bot.set_state(message.chat.id, 1)

    else :
        if data_request :
            msg = util.string_format(STRINGS['STR_ALREADY_REQUESTED'], '')
            bot.send_message(message.chat.id, msg,  parse_mode="MarkdownV2")
        elif data_machine :
            msg = util.string_format(STRINGS['STR_ALREADY_PROVISIONED'], '')
            bot.send_message(message.chat.id, msg,  parse_mode="MarkdownV2")
            
# TODO Cancel state

@bot.message_handler(state=1)
@bot.message_handler(text=[STRINGS['STR_TERMS_OF_SERVICE_ACCEPT'],STRINGS['STR_PROVISION_CONFIRMATION_NO']])
def os_selection(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2, one_time_keyboard=True)
    [ markup.add(types.KeyboardButton(os['name'])) for os in CONFIG['template_vm']['template_vms']]

    msg = util.string_format(STRINGS['STR_SELECT_OS'], '')
    bot.send_message(message.chat.id, msg,reply_markup=markup ,   parse_mode="MarkdownV2")
    bot.set_state(message.chat.id, 2)

# TODO TERMS OF SERVICE DISAGREE

@bot.message_handler(state=2)
@bot.message_handler(text=[ os['name'] for os in CONFIG['template_vm']['template_vms']])
def confirmation(message):
    selection = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    itembtn1 = types.KeyboardButton(STRINGS['STR_PROVISION_CONFIRMATION_YES'])
    itembtn2 = types.KeyboardButton(STRINGS['STR_PROVISION_CONFIRMATION_NO'])
    markup.add(itembtn1, itembtn2)

    msg = util.string_format(STRINGS['STR_PROVISION_CONFIRMATION'], selection)

    bot.send_message(message.chat.id, msg, reply_markup=markup ,  parse_mode="MarkdownV2")
    bot.set_state(message.chat.id, 3)
    
    with bot.retrieve_data(message.chat.id) as data:
        data['os'] = selection

# TODO Wrong os selection

@bot.message_handler(state=3, text=[STRINGS['STR_PROVISION_CONFIRMATION_NO']])
def back_to_os_selection(message):
    bot.set_state(message.chat.id, 1)

@bot.message_handler(state=3, text=[STRINGS['STR_PROVISION_CONFIRMATION_YES']])
def checkout(message):
   
    # send chekcout message to user
    msg= util.string_format(STRINGS['STR_PROVISION_CHECKOUT'], '')
    bot.send_message(message.chat.id, msg, parse_mode="MarkdownV2" ,reply_markup=types.ReplyKeyboardRemove(True))

    # insert to request db
    insert_request(message)
    # notify admin
    nofify_admin(message)
    # Delete state
    bot.delete_state(message.chat.id)

def insert_request(message):

    info = get_requester_info(message)
    try :
        conn= helper.create_connection(db_file)
        helper.insert_request(conn, info)
        conn.close()
    except sqlite3.Error as e :
        print(e) # print for now

def get_request(requester_id):

    try :
        conn= helper.create_connection(db_file)
        data= helper.get_request(conn, requester_id)
        conn.close()
        return data
    except sqlite3.Error as e :
        print(e) # print for now

def update_request( requester_id , status):
    
    try :
        conn= helper.create_connection(db_file)
        data= helper.update_request(conn, requester_id, status)
        conn.close()
        return data
    except sqlite3.Error as e :
        print(e) # print for now

def insert_machine(data):
    try :
        conn= helper.create_connection(db_file)
        data= helper.insert_machine(conn, data)
        conn.close()
        return data
    except sqlite3.Error as e :
        print(e) # print for now

def get_vm_id():
    try :
        conn= helper.create_connection(db_file)
        data= helper.get_vm_id(conn)
        conn.close()
        return data
    except sqlite3.Error as e :
        print(e) # print for now

def increment_vm_id():
    try :
        conn= helper.create_connection(db_file)
        data= helper.increment_vm_id(conn)
        conn.close()
        return data
    except sqlite3.Error as e :
        print(e) # print for now

def delete_request(requester_id):
    try :
        conn= helper.create_connection(db_file)
        data= helper.delete_request(conn, requester_id)
        conn.close()
    except sqlite3.Error as e :
        print(e) # print for now

def get_requester_info(message):

    info = {}
    info['request_time'] = datetime.datetime.now()
    info['requester_id'] = message.chat.id
    info['requesters_name'] = message.chat.first_name 
    info['requesters_username'] = f'(@{message.chat.username})' if message.chat.username else ''
    with bot.retrieve_data(message.chat.id) as data:
        info['os'] = data['os']
    return info

def nofify_admin(message):

    requester_info = get_requester_info(message)

    callback_data_accept = f"{{'status' : 'accepted', 'requester_id': {requester_info['requester_id']} }}"
    callback_data_deny= f"{{'status' : 'denied', 'requester_id': {requester_info['requester_id']} }}"

    markup = types.InlineKeyboardMarkup()
    itembtn1= types.InlineKeyboardButton(STRINGS['STR_PROVISION_REQUEST_GRANT'], callback_data=callback_data_accept)
    itembtn2= types.InlineKeyboardButton(STRINGS['STR_PROVISION_REQUEST_DENY'], callback_data=callback_data_deny)
    markup.add(itembtn1, itembtn2)
    
    msg = util.string_format(STRINGS['STR_PROVISION_REQUEST'], requester_info['request_time'],requester_info['requester_id'], requester_info['requesters_username'] , "pending", requester_info['requesters_name'] , requester_info['os'])
    
    bot.send_message(CONFIG['bot']['admin_id'], msg, reply_markup=markup, parse_mode="MarkdownV2")


@bot.callback_query_handler(func=lambda call: util.string_to_dict(call.data)['status'] =="accepted")
def request_accepted (call) :

    requester_id = util.string_to_dict(call.data)['requester_id']

    # read request form db
    data= get_request(requester_id)
    print(data)
    
    # clone the vm 
    # TODO on a new thread
    status = clone_vm(data)

    bot.answer_callback_query(call.id, "Request granted")

    if status['success'] == 1:
        
        # update request
        update_request(requester_id, "accepted")
        # insert server
        insert_machine(data)
        # send message to requester
        # congraulations
        msg = util.string_format(STRINGS['STR_PROVISION_ACCEPTED'], data[1])
        bot.send_message(requester_id, msg, parse_mode="MarkdownV2")

        # updated admin message
        msg = call.message.text.replace('pending', 'accepted')
        msg = util.string_format(msg, '')
        bot.edit_message_text (msg, call.message.chat.id, call.message.message_id, parse_mode="MarkdownV2")
    else :
        # Update admin message
        msg = call.message.text.replace('pending', 'ERROR')
        msg += f"\n\n{status['msg']}"
        msg = util.string_format(msg, '')
        bot.edit_message_text (msg, call.message.chat.id, call.message.message_id, parse_mode="MarkdownV2")

        # delete request 
        delete_request(requester_id)
        # notify user that thier request has failed due to server error
        msg = util.string_format(STRINGS['STR_PROVISION_FAILED'],'')
        bot.send_message(requester_id, msg, parse_mode="MarkdownV2")

def clone_vm(data):

    # get current vm id
    vm_id = get_vm_id()
    # increment vm id
    increment_vm_id()

    new_vm ={'newid': vm_id,
            'description':f'{data[1]} vm',
            'full':1,
            'name':f"{data[1]}-los-{data[4].lower().replace(' ', '')}"
            }

    for template_vms in CONFIG['template_vm']['template_vms']:
        if template_vms['name'] == data[4] :
            clone_vm_id = template_vms['vm_id']

    msg = vm.clone_vm(proxmox, CONFIG['proxmox']['node'], clone_vm_id ,new_vm)

    return  msg
    


@bot.callback_query_handler(func=lambda call: util.string_to_dict(call.data)['status'] =="denied")
def request_denied (call) :

    requester_id = util.string_to_dict(call.data)['requester_id']

    # remove request
    delete_request(requester_id)

    # notify user
    msg = util.string_format(STRINGS['STR_PROVISION_REJECTED'], '')
    bot.send_message(requester_id, msg, parse_mode="MarkdownV2")

    # updated the message
    bot.answer_callback_query(call.id, "Request denied")

    msg = call.message.text.replace('pending', 'rejected')
    msg = util.string_format(msg, '')
    bot.edit_message_text (msg, call.message.chat.id, call.message.message_id, parse_mode="MarkdownV2")

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
    except sqlite3.Error as e :
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
    except sqlite3.Error as e :
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

    msg= util.string_format(STRINGS['STR_MAINTENANCE'], '')
    bot.send_message(message.chat.id,msg, parse_mode="MarkdownV2" )

# if __name__  == 'main' :
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.TextMatchFilter())

bot.infinity_polling()
   
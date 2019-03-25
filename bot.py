#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

import sys
import telepot
import time
from telepot.loop import MessageLoop

def handle(msg):
    print('Message: ' + str(msg))
    content_type, chat_type, chat_id = telepot.glance(msg)
    txt = ''
    if 'text' in msg:
        txt = txt + msg['text']
    elif 'caption' in msg:
        txt = txt + msg['caption']

    if msg['chat']['type'] in ['group', 'supergroup'] and len(msg['new_chat_members']) > 0:
        newMembers = msg['new_chat_members']
        foundLeMe = False
        for member in newMembers:
            if member['is_bot'] and member['id'] == BOT_ID:
                foundLeMe = True
        
        if foundLeMe:
            CHATS.append(msg['chat']['id'])
    if msg['chat']['type'] == 'channel' and is_allowed(msg) and txt != '':
        for chat in CHATS:
            bot.forwardMessage(chat, chat_id, msg['message_id'])

def is_allowed(msg):
    if msg['chat']['id'] == SOURCE:
        return True
    return False

def updateChatsList():
    with open('chats.json', 'w') as f:
        f.write(','.join(list(set(CHATS))))

if not os.path.isfile('chats.json'):
    f = open('chats.json', 'w+')

CHATS = []
BOT_ID = os.environ.get('BOT_ID')
TOKEN = os.environ.get('BOT_TOKEN')
PASSWORD = os.environ.get('ADMIN_PASSWORD')

if TOKEN == '' or PASSWORD == '':
    sys.exit('No TOKEN or PASSWORD in environment')

with open('chats.json', 'r') as f:
    CHATS = f.read().split(',')

if os.path.isfile('config.json'):
    with open('config.json', 'r') as f:
        config = json.load(f)
        if config['source'] == '':
            sys.exit('No source channel defined. Define it in a file called config.json.')
        SOURCE = config['source']
else:
    sys.exit('No config.json file found.')

bot = telepot.Bot(TOKEN)

MessageLoop(bot, handle).run_as_thread()
print('Listening ...')
# Keep the program running.
while 1:
    time.sleep(10)

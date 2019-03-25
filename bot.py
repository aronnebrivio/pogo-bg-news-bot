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

    if msg['chat']['type'] in ['group', 'supergroup'] and msg['new_chat_participant']:
        if msg['new_chat_participant']['is_bot'] and msg['new_chat_participant']['id'] == BOT_ID:
            CHATS.append(msg['chat']['id'])
            updateChatsList()
    elif msg['chat']['type'] == 'channel' and is_allowed(msg) and txt != '':
        if CHATS:
            for chat in CHATS:
                bot.forwardMessage(chat, SOURCE, msg['message_id'])

def is_allowed(msg):
    if msg['chat']['id'] == SOURCE:
        return True
    return False

def updateChatsList():
    with open('chats.json', 'w+') as f:
        f.write(','.join(list(set(CHATS))))
        f.close()

CHATS = []
BOT_ID = os.environ.get('BOT_ID')
TOKEN = os.environ.get('BOT_TOKEN')
PASSWORD = os.environ.get('ADMIN_PASSWORD')

if TOKEN == '' or PASSWORD == '' or BOT_ID == '':
    sys.exit('No TOKEN, PASSWORD or BOT_ID in environment')

with open('chats.json', 'r+') as f:
    CHATS = f.read().split(',')
    f.close()

if os.path.isfile('config.json'):
    with open('config.json', 'r') as f:
        config = json.load(f)
        if config['source'] == '':
            sys.exit('No source channel defined. Define it in a file called config.json.')
        SOURCE = config['source']
        f.close()
else:
    sys.exit('No config.json file found.')

bot = telepot.Bot(TOKEN)

MessageLoop(bot, handle).run_as_thread()
print('Listening ...')
# Keep the program running.
while 1:
    time.sleep(10)

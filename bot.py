#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

import sys
import telepot
import time
import redis
from telepot.loop import MessageLoop

BOT_ID = os.environ.get('BOT_ID')
TOKEN = os.environ.get('BOT_TOKEN')
PASSWORD = os.environ.get('ADMIN_PASSWORD')
SOURCE = os.environ.get('SOURCE')
REDIS_URL = os.environ.get('REDIS_URL')

def handle(msg):
    print('Message: ' + str(msg))
    txt = ''
    if 'text' in msg:
        txt = txt + msg['text']
    elif 'caption' in msg:
        txt = txt + msg['caption']

    if msg['chat']['type'] in ['group', 'supergroup'] and msg['new_chat_participant']:
        if str(msg['new_chat_participant']['id']) == BOT_ID:
            CHATS.append(msg['chat']['id'])
            redis.set('chats', ','.join(list(set(CHATS))))
    elif msg['chat']['type'] == 'channel' and is_allowed(msg) and txt != '':
        for chat in CHATS:
            if chat:
                try:
                    bot.forwardMessage(chat, SOURCE, msg['message_id'])
                except:
                    print('Error forwarding message to ', chat)

def is_allowed(msg):
    if str(msg['chat']['id']) == SOURCE:
        return True
    return False

if REDIS_URL != None:
    redis = redis.from_url(REDIS_URL)
else:
    redis = redis.StrictRedis(host='localhost', port=6379, password='', decode_responses=True)

chats = redis.get('chats')
if chats:
    CHATS = str(chats).split(',')
else:
    CHATS = []

if TOKEN == '' or PASSWORD == '' or BOT_ID == '' or SOURCE == '':
    sys.exit('No TOKEN, PASSWORD, SOURCE or BOT_ID in environment')

bot = telepot.Bot(TOKEN)

MessageLoop(bot, handle).run_as_thread()
print('Listening ...')
# Keep the program running.
while 1:
    time.sleep(10)

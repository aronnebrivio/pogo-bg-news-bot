#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

import sys
import telepot
import time
import redis
from telepot.loop import MessageLoop

# Functions
def handle(msg):
    print('Message: ' + str(msg))
    txt = ''
    if 'text' in msg:
        txt = txt + msg['text']
    elif 'caption' in msg:
        txt = txt + msg['caption']

    if msg['chat']['type'] in ['group', 'supergroup'] and msg['new_chat_participant']:
        if str(msg['new_chat_participant']['id']) == BOT_ID:
            if not CHATS[str(msg['chat']['id'])]:
                CHATS[str(msg['chat']['id'])]['name'] = msg['chat']['title']
                CHATS[str(msg['chat']['id'])]['username'] = msg['chat']['username']
                CHATS[str(msg['chat']['id'])]['tags'] = []
                redis.set('chats', json.dumps(CHATS))
    elif msg['chat']['type'] == 'channel' and isAllowed(msg) and txt != '':
        for chatId in CHATS:
            if shouldForward(chatId, txt):
                try:
                    bot.forwardMessage(chatId, SOURCE, msg['message_id'])
                except:
                    print('Error forwarding message to ', chatId)

def isAllowed(msg):
    if str(msg['chat']['id']) == SOURCE:
        return True
    return False

def shouldForward(chatId, text):
    if chatId == SPAM_CHAT_ID:
        return True

    for tag in CHATS[chatId]['tags']:
        if text.find('#' + tag) >= 0:
            return True
    return False

# MAIN
# Load env variables
BOT_ID = os.environ.get('BOT_ID')
TOKEN = os.environ.get('BOT_TOKEN')
PASSWORD = os.environ.get('ADMIN_PASSWORD')
SOURCE = os.environ.get('SOURCE')
MAIN_CHAT_ID = os.environ.get('MAIN_CHAT_ID')
SPAM_CHAT_ID = os.environ.get('SPAM_CHAT_ID')
REDIS_URL = os.environ.get('REDIS_URL')

if TOKEN == '' or PASSWORD == '' or BOT_ID == '' or SOURCE == '':
    sys.exit('No TOKEN, PASSWORD, SOURCE or BOT_ID in environment')

# Load data from Redis
if REDIS_URL != None:
    redis = redis.from_url(REDIS_URL)
else:
    redis = redis.Redis(host='localhost', port=6379, password='', decode_responses=True)

chats = redis.get('chats').decode('utf-8')

if chats:
    CHATS = json.loads(chats)
else:
    CHATS = json.loads('{}')

bot = telepot.Bot(TOKEN)

MessageLoop(bot, handle).run_as_thread()
print(CHATS)
print('Listening ...')
# Keep the program running.
while 1:
    time.sleep(10)

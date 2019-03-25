#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

import sys
import telepot
import time
import redis
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
        if msg['new_chat_participant']['id'] == int(BOT_ID):
            print('here we are')
            CHATS.append(msg['chat']['id'])
            redis.set('chats', ','.join(map(str, list(set(CHATS)))))
    elif msg['chat']['type'] == 'channel' and is_allowed(msg) and txt != '':
        for chat in CHATS:
            print('DEST: ', chat, ' - SOURCE: ', SOURCE)
            if chat != '':
                bot.forwardMessage(chat, SOURCE, msg['message_id'])

def is_allowed(msg):
    if msg['chat']['id'] == SOURCE:
        return True
    return False

BOT_ID = os.environ.get('BOT_ID')
TOKEN = os.environ.get('BOT_TOKEN')
PASSWORD = os.environ.get('ADMIN_PASSWORD')
REDIS_URL = os.environ.get('REDIS_URL')

if REDIS_URL == None:
  redis_url = '127.0.0.1:6379'
  
redis = redis.from_url(REDIS_URL)
chats = redis.get('chats')
if chats:
    CHATS = map(int, chats.split(','))
else:
    CHATS = []

if TOKEN == '' or PASSWORD == '' or BOT_ID == '':
    sys.exit('No TOKEN, PASSWORD or BOT_ID in environment')

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

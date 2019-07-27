#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import telepot
import time
from pony import orm
from telepot.loop import MessageLoop
from dotenv import load_dotenv

# Classes
db = orm.Database()

class Chat(db.Entity):
    _table_ = 'chats'
    id = orm.PrimaryKey(int, auto=True)
    telegram_id = orm.Required(str, unique=True)
    main = orm.Required(int)
    active = orm.Required(int)
    name = orm.Optional(str)
    topics = orm.Set(lambda: Topic, table='topics_for_chats', column='topic_id')

class Topic(db.Entity):
    _table_ = 'topics'
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str)
    tags = orm.Set(lambda: Tag, table='tags_for_topics', column='tag_id')
    chats = orm.Set(lambda: Chat, table='topics_for_chats', column='chat_id')

class Tag(db.Entity):
    _table_ = 'tags'
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str, unique=True)
    topics = orm.Set(lambda: Topic, table='tags_for_topics', column='topic_id')

# Functions
def handle(msg):
    print('Message: ' + str(msg))
    txt = ''

    try:
        if 'text' in msg:
            txt = txt + msg['text']
        elif 'caption' in msg:
            txt = txt + msg['caption']

        if msg['chat']['type'] in ['group', 'supergroup'] and msg['new_chat_participant']:
            if str(msg['new_chat_participant']['id']) == BOT_ID:
                chatId = str(msg['chat']['id'])
                with orm.db_session:
                    chat = Chat.get(telegram_id = chatId)
                    if chat == None:
                        time.sleep(5)
                        chat = Chat(telegram_id = chatId, name = msg['chat']['title'], main = 0, active = 1, topics = availableTopics)
        elif msg['chat']['type'] == 'channel' and isAllowed(msg) and txt != '':
            with orm.db_session:
                chats = Chat.select()[:]
                for chat in chats:
                    if shouldForward(chat, txt):
                        try:
                            bot.forwardMessage(chat.telegram_id, SOURCE, msg['message_id'])
                        except:
                            print('Error forwarding message to ', chat.telegram_id)
    except KeyError:
        print('Whoops! KeyError')

def isAllowed(msg):
    try:
        if str(msg['chat']['id']) == SOURCE:
            return True
    except KeyError:
        print('Whoops! KeyError')
    return False

@orm.db_session
def shouldForward(chat, text):
    if chat.active == 0:
        return False
        
    if chat.main > 0:
        return True

    interestedTags = []
    topics = Chat[chat.id].topics
    for topic in topics:
        interestedTags.extend(list(topic.tags))
    
    for tag in interestedTags:
        if text.find('#' + tag.name) >= 0:
            return True
    return False

@orm.db_session
def loadTopics():
    return Topic.select()

# MAIN
# Load env variables
load_dotenv()
BOT_ID = os.getenv('BOT_ID')
TOKEN = os.getenv('BOT_TOKEN')
PASSWORD = os.getenv('ADMIN_PASSWORD')
SOURCE = os.getenv('SOURCE')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_DATABASE = os.getenv('DB_DATABASE')

# Connect to database
if DB_HOST == '' or DB_USER == '' or DB_PASSWORD == '' or DB_DATABASE == '':
    sys.exit('No DB_HOST, DB_USER, DB_PASSWORD or DB_DATABASE in environment')
db.bind(provider='mysql', host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
db.generate_mapping()

# Load available topics
availableTopics = loadTopics()

# Start the bot
if TOKEN == '' or PASSWORD == '' or BOT_ID == '' or SOURCE == '':
    sys.exit('No TOKEN, PASSWORD, SOURCE or BOT_ID in environment')
bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
print('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)

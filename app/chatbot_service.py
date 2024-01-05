import json
import numpy as np
import huggingface_hub
import torch
from datasets import load_metric
import random
import os
import telebot
import psycopg2



from chatbot import ChatBot
from db_storage import DB_storage
import settings



messageBot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
chatBot = ChatBot(settings.MODEL_NAME, settings.TOKENIZER_NAME, settings.QUANT_BITS)
db_storage = DB_storage(   
            postresql_table_name = settings.POSTGRESQL_TABLE_NAME, 
            postresql_host = settings.POSTGRESQL_HOST,
            postresql_db_name = settings.POSTGRESQL_DB_NAME,
            postresql_user = settings.POSTGRESQL_USER,
            postresql_password = settings.POSTGRESQL_PASSWORD)



@messageBot.message_handler(commands=['clear'])
def clear_history(message):
    db_storage.delete_history()
    


@messageBot.message_handler(func=lambda msg: True)
def echo_all(message):
    
    user_id = message.from_user.id
    user_text = message.json['text']

    history = db_storage.get_user_history(user_id)

    answer = chatBot.generate_answer(user_text, history)
    
    db_storage.push_to_history(user_text, 'USER', user_id)
    db_storage.push_to_history(answer, 'BOT', user_id)

    messageBot.reply_to(message, answer)



print("!!!service started!!!")

messageBot.infinity_polling()









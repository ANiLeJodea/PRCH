# Python default packages
from os import environ

# External packages
import requests
from telebot import TeleBot

# Project packages
from data import AllData

bot = TeleBot(token=environ["BOT_TOKEN"])
all_data = AllData()

environ['LOG_FORUM_ID'], environ['LOG_TOPIC_ID'] = all_data.data['log_entity'].split(" ")

environ['THIS_IP'] = requests.get('https://ipinfo.io/ip').text

bot.send_message(
    chat_id=environ['LOG_FORUM_ID'],
    message_thread_id=environ['LOG_TOPIC_ID'],
    text="Tried to set a webhook with telebot.\nResponse: {}\nRunning on {}\nUsed {} mode to form data_str".format(
        bot.set_webhook(environ['EXTERNAL_URL']),
        environ['THIS_IP'],
        all_data.mode
        # '\n'.join(a for a in all_data['admins'])
    )
)


# Python default packages
from os import environ

# External packages
import requests
from telebot import TeleBot

# Project packages
from data import get_data

bot = TeleBot(token=environ["BOT_TOKEN"])
all_data: dict = get_data()

environ['LOG_FORUM_ID'], environ['LOG_TOPIC_ID'] = all_data['log_entity']

environ['THIS_IP'] = requests.get('https://ipinfo.io/ip').text

bot.send_message(
    chat_id=environ['LOG_FORUM_ID'],
    message_thread_id=environ['LOG_TOPIC_ID'],
    text="Tried to set a webhook with telebot. Response:\n{}\nRunning on {}\nADMINS:\n{}".format(
        bot.set_webhook(environ['EXTERNAL_URL']),
        environ['THIS_IP'],
        '\n'.join(a for a in all_data['admins'])
    )
)


# Python default packages
import time
from os import environ

# External packages
import requests
from telebot import TeleBot
from telebot import types
from telebot import util

# Project packages
from data import AllData

class EncTeleBot(TeleBot):

    def enc_send_message(
            self, chat_id, text: str,
            parse_mode: str = 'html',
            disable_web_page_preview: bool = True,
            reply_to_message_id: int = None,
            timeout: int = None,
            message_thread_id: int = None
    ) -> list[types.Message]:
        for t in util.smart_split(text=text):
            yield self.send_message(
                chat_id=chat_id, text=t, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview,
                reply_to_message_id=reply_to_message_id, timeout=timeout, message_thread_id=message_thread_id
            )
            time.sleep(2)

bot = EncTeleBot(token=environ["BOT_TOKEN"])
all_data = AllData()

environ['LOG_FORUM_ID'], environ['LOG_TOPIC_ID'] = all_data.data['log_entity'].split(" ")
environ['THIS_IP'] = requests.get('https://ipinfo.io/ip').text
environ['TIME_STARTED_INT'] = str(time.time())
environ['TIME_STARTED'] = time.strftime('%H:%M:%S %d/%m/%Y')

bot.send_message(
    chat_id=environ['LOG_FORUM_ID'],
    message_thread_id=environ['LOG_TOPIC_ID'],
    text="Tried to set a webhook with telebot.\nResponse: {}\nRunning on {}\nUsed {} mode to form data_str".format(
        bot.set_webhook(environ['EXTERNAL_URL']),
        environ['THIS_IP'],
        all_data.mode
    )
)


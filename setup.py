# Python default packages
import time
from os import environ
# test ad
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
            message_thread_id: int | str = None,
            delay_between_sending: float = 2
    ) -> list[types.Message]:
        to_return = []
        for t in util.smart_split(text=text):
            to_return.append(self.send_message(
                chat_id=chat_id, text=t, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview,
                reply_to_message_id=reply_to_message_id, timeout=timeout, message_thread_id=message_thread_id
            ))
            time.sleep(delay_between_sending)
        return to_return

    def enc_edit_message_text(
            self, text: str, chat_id, message_id: int = None,
            inline_message_id: str = None,
            parse_mode: str = None, entities: list[types.MessageEntity] = None,
            disable_web_page_preview: bool = None,
            reply_markup: types.InlineKeyboardMarkup = None,
            reply_to_message_id: int = None, timeout: int = None, message_thread_id: int = None,
            delay_between_acting: float = 2
    ) -> list:
        to_return = []
        text_parts = util.smart_split(text=text)

        self.edit_message_text(
            chat_id=chat_id, text=text_parts.pop(0), message_id=message_id, parse_mode=parse_mode,
            inline_message_id=inline_message_id, entities=entities, disable_web_page_preview=disable_web_page_preview,
            reply_markup=reply_markup
        )
        time.sleep(delay_between_acting)
        for t in text_parts:
            to_return.append(self.send_message(
                chat_id=chat_id, text=t, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview,
                reply_to_message_id=reply_to_message_id, timeout=timeout, message_thread_id=message_thread_id
            ))
            time.sleep(delay_between_acting)

        return to_return

bot = EncTeleBot(token=environ["BOT_TOKEN"], skip_pending=True)
all_data = AllData()

environ['LOG_FORUM_ID'], environ['LOG_TOPIC_ID'] = all_data.data['log_entity'].split(" ")
environ['THIS_IP'] = requests.get('https://ipinfo.io/ip').text
environ['TIME_STARTED_INT'] = str(time.time())
environ['TIME_STARTED'] = time.strftime('%H:%M:%S %d-%m-%Y')
external_url = environ["EXTERNAL_URL"]

bot.send_message(
    chat_id=environ['LOG_FORUM_ID'],
    message_thread_id=environ['LOG_TOPIC_ID'],
    text="Tried to set a webhook with telebot.\nResponse: {}\nRunning on {}\nUsed {} mode to form data_str".format(
        bot.set_webhook(external_url),
        environ['THIS_IP'],
        all_data.mode
    )
)


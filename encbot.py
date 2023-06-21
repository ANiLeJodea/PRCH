# Python default packages
import time

# External packages
from telebot import TeleBot, types, util

class EncTeleBot(TeleBot):

    def enc_send_message(
            self, chat_id, text: str,
            parse_mode: str = 'html',
            disable_web_page_preview: bool = True,
            reply_to_message_id = None,
            timeout = None,
            message_thread_id = None,
            delay_between_sending: float = 2
    ) -> list[types.Message]:
        """
        :param message_thread_id: int | str
        :param chat_id: int | str
        :param text: str
        :param parse_mode: str | None
        :param disable_web_page_preview: bool
        :param reply_to_message_id: int
        :param timeout: int
        :param message_thread_id: int | str
        :param delay_between_sending: float | int
        """
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
        messages = []
        text_parts = util.smart_split(text=text)

        self.edit_message_text(
            chat_id=chat_id, text=text_parts.pop(0), message_id=message_id, parse_mode=parse_mode,
            inline_message_id=inline_message_id, entities=entities, disable_web_page_preview=disable_web_page_preview,
            reply_markup=reply_markup
        )
        time.sleep(delay_between_acting)
        for t in text_parts:
            messages.append(self.send_message(
                chat_id=chat_id, text=t, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview,
                reply_to_message_id=reply_to_message_id, timeout=timeout, message_thread_id=message_thread_id
            ))
            time.sleep(delay_between_acting)

        return messages



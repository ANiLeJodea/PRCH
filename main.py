# Python default packages
import os
import threading
import time

# External packages
import telebot
from telebot.types import Message
from flask import Flask, request

# Project packages
from setup import all_data as all_data_now, bot
# verify_proxy_on_ipinfo
from verify import check_proxies_from_document, \
    verify_proxy_on_site_list, verify_proxy_on_ipinfo_w_time_time
from data import AllData
from helpers import exc_to_str

all_data = all_data_now

app = Flask(__name__)

@app.route('/', methods=["POST"])
def handle_request():
    if request.headers.get('content-type') == "application/json":
        update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
        m: Message = update.message
        if str(m.from_user.id) in all_data.data['admins']:
            bot.process_new_updates([update])
    return "OK"


@bot.message_handler(commands=['info'])
def handle_info(m: Message):
    answer_text = all_data.data_str + \
                  f"\n\nTHIS_IP : {os.environ['THIS_IP']}\n\nSTARTED_TIME : {os.environ['STARTED_TIME']}\n\n" \
                  f"Time went from program start : {time.time() - float(os.environ['STARTED_TIME_INT'])}\n\n"
    message_id_to_answer = m.message_id

    try:
        message_id_to_answer = bot.send_document(
            m.chat.id, open(f"{all_data.data['checked_file_name']}.txt", 'rb')).message_id
        answer_text += f"Last {all_data.data['checked_file_name']}:"
    except FileNotFoundError:
        answer_text += "Seems like there is no checked file on server yet. Try to make it"
    bot.enc_send_message(
        chat_id=m.chat.id,
        text=answer_text,
        reply_to_message_id=message_id_to_answer,
        parse_mode=all_data.mode,
        disable_web_page_preview=True
    )


def define_handlers_of_dynamic_commands():

    global all_data

    @bot.message_handler(commands=all_data.data['command_for_update_data'])
    def handle_update_data(m: Message):

        global all_data

        all_data = AllData(mode=m.text[(len(all_data.data['command_for_update_data'])+2):])
        bot.enc_send_message(m.chat.id, f"Using {all_data.mode}. Updating by calling define()...")
        define_handlers_of_dynamic_commands()

    @bot.message_handler(commands=[all_data.data['command_for_ip_info']])
    def handle_ip_info_check(m: Message):
        proxy = m.text[len(all_data.data['command_for_ip_info']) + 2:]
        answer_message_id = bot.enc_send_message(m.chat.id, f"Trying to verify {proxy}...").id
        thread = threading.Thread(
            target=perform_ip_info_check, args=(
                m.chat.id,
                answer_message_id,
                proxy
            )
        )
        thread.start()

    @bot.message_handler(commands=[all_data.data['command_for_site_list']])
    def handle_site_list_check(m: Message):
        answer_message_id = bot.enc_send_message(m.chat.id, "Trying to verify on a site list...").id
        thread = threading.Thread(
            target=perform_site_list_check, args=(
                m.chat.id,
                answer_message_id,
                m.text[len(all_data.data['command_for_site_list']) + 2:]
            )
        )
        thread.start()

def perform_ip_info_check(chat_id, id_of_message_to_change, proxy_data):
    if ':' in proxy_data:
        text = verify_proxy_on_ipinfo_w_time_time(proxy_data)[1]
    else:
        text = "Please, provide something to check in the correct format."

    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=id_of_message_to_change
    )

def perform_site_list_check(chat_id, id_of_message_to_change, args):
    args_list: list = args.split(':')
    args_list_len: int = len(args_list)
    if 1 < args_list_len < 4:
        text = "Results:\n"
        if args_list_len == 2:
            proxy_ip, proxy_port = args_list
            sites_list = all_data.data['default_site_list_to_check']
        elif args_list_len == 3:
            proxy_ip, proxy_port, sites = args_list
            sites_list = [f'https://{s}' for s in sites.split(',')]
        for site_name, result in verify_proxy_on_site_list(proxy_ip, proxy_port, sites_list).items():
            text += f"Site {site_name}::\n{result[1]}\n\n"
    else:
        text = "Please, provide something to check in the correct format."

    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=id_of_message_to_change,
        disable_web_page_preview=True
    )

@bot.message_handler(content_types=['document'])
def handle_check_proxy_list_from_document(m: Message):
    answer_message_id = bot.enc_send_message(
        chat_id=m.chat.id,
        text="Trying to verify all the proxies in this file...",
        reply_to_message_id=m.message_id
    ).id
    raw_file = bot.get_file(m.document.file_id)
    raw_file_type = raw_file.file_path.split('.')[-1]
    if raw_file_type == 'txt':
        arguments = m.caption.split(';')
        filter_condition = None
        if len(arguments) == 2:
            filter_condition = bool(arguments[1])
        if arguments[0].lower() == "no":
            portion = None
        else:
            try:
                portion = int(arguments[0])
            except ValueError:
                bot.edit_message_text(
                    chat_id=m.chat.id, message_id=answer_message_id,
                    text="The caption of this message is not 'no' and I was not able to convert it to an integer.\n"
                         f"Going to use the default value {all_data.data['portion']}"
                )
                portion = all_data.data['portion']
        thread = threading.Thread(
            target=check_proxies_from_document,
            args=(m.chat.id, raw_file.file_path, portion, filter_condition)
        )
        thread.start()
    else:
        bot.edit_message_text(
            chat_id=m.chat.id, message_id=answer_message_id,
            text="Not supported file type. Unable to check. Try again with .txt file"
        )

def check_proxy_list_from_document(
    chat_id: str, telegram_raw_file_path: str, portion: int, condition: bool
):
    raw_file_path = all_data.data['raw_file_name'] + '.txt'
    with open(raw_file_path, 'wb') as f:
        f.write(bot.download_file(telegram_raw_file_path))

    result = check_proxies_from_document(raw_file_path, portion, condition)
    if len(result) == 2:
        bot.enc_send_message(
            chat_id=chat_id,
            text=exc_to_str(result[0], title="An error occurred (Failed to verify all. Going to try to send "
                                             "the broken file):\n\n")
        )
        bot.send_document(
            chat_id=chat_id,
            document=open(all_data.data['checked_file_name'] + ".txt", 'rb'),
            visible_file_name=f"Crashed {result[1]}"
        )
    else:
        bot.send_document(
            chat_id=chat_id,
            document=open(all_data.data['checked_file_name'] + ".txt", 'rb'),
            visible_file_name=result
        )

if __name__ == "__main__":
    define_handlers_of_dynamic_commands()
    app.run("0.0.0.0", port=os.getenv("PORT", 3000))



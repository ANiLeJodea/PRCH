# Python default packages
import os
import threading
import time
# import argparse

# External packages
import telebot
from telebot.types import Message
from flask import Flask, request

# Project packages
from setup import all_data as all_data_now, bot
from verify import check_proxies_from_document, \
    verify_proxy_on_site_list, verify_proxy_on_ipinfo
from data import AllData
from helpers import exc_to_str, form_an_output

all_data = all_data_now

# site_list_command_parser = argparse.ArgumentParser()
# site_list_command_parser.add_argument(all_data.data['site_list_argument'])  # -sites
# parser.add_argument(all_data.data[''])  # -

app = Flask(__name__)

# 1 - silent ; 2 - verbose ; 3 - expressive
modes = {None: all_data.data['mode'], "silent": 1, "verbose": 2, "expressive": 3}

@app.route('/', methods=["POST"])
def handle_request():
    if request.headers.get('content-type') == "application/json":
        update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
        if update.message and str(update.message.from_user.id) in all_data.data['admins']:
            bot.process_new_updates([update])
    return "OK"


@bot.message_handler(commands=['info'])
def handle_info(m: Message):
    answer_text = all_data.data_str + \
                  f"\n\nTHIS_IP : {os.environ['THIS_IP']}\n\nSTARTED_TIME : {os.environ['TIME_STARTED']}\n\n" \
                  "Secs have passed from program start : " \
                  f"{round(time.time() - float(os.environ['TIME_STARTED_INT']), 4)}\n\n"
    message_id_to_answer = m.message_id

    try:
        message_id_to_answer = bot.send_document(
            m.chat.id, open(f"{all_data.data['checked_file_name']}.txt", 'rb')).message_id
        answer_text = f"Last {all_data.data['checked_file_name']} ⏫\n" + answer_text
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
        bot.send_message(m.chat.id, f"Using {all_data.mode}. Updating by calling define()...")
        define_handlers_of_dynamic_commands()

    @bot.message_handler(commands=[all_data.data['command_for_ip_info']])
    def handle_ip_info_check(m: Message):
        proxy = m.text[len(all_data.data['command_for_ip_info']) + 2:]
        answer_message_id = bot.send_message(m.chat.id, "Doing...").message_id
        thread = threading.Thread(
            target=perform_ip_info_check, args=(
                m.chat.id,
                answer_message_id,
                proxy,
                modes[None]
            )
        )
        thread.start()

    @bot.message_handler(commands=[all_data.data['command_for_site_list']])
    def handle_site_list_check(m: Message):
        answer_message_id = bot.send_message(m.chat.id, "Doing on a site list...").message_id
        thread = threading.Thread(
            target=perform_site_list_check, args=(
                m.chat.id,
                answer_message_id,
                m.text[len(all_data.data['command_for_site_list']) + 2:],
                modes[None]
            )
        )
        thread.start()

def perform_ip_info_check(chat_id, id_of_message_to_change, proxy_data, mode: int):
    bot.enc_edit_message_text(
        text=form_an_output(
            verify_proxy_on_ipinfo(proxy_data, timeout=all_data.data['timeout'])[1],
            mode
        ),
        chat_id=chat_id,
        message_id=id_of_message_to_change
    )


def perform_site_list_check(chat_id, id_of_message_to_change, args, mode: int):
    try:
        args_list: list = args.split(' ')
        text = "Results:\n"
        proxy_ip_port = args_list.pop(0)
        parsed_arguments = {a[1:]: args_list[i+1] for i, a in enumerate(args_list[:-1]) if i % 2 == 0 and a[0] == '-'}
        if sites := parsed_arguments.get(all_data.data['site_list_argument']):
            sites_list = [f'https://{s}' for s in sites.split(',')]
        else:
            sites_list = all_data.data['default_site_list_to_check']
        for site_name, result in verify_proxy_on_site_list(
                proxy_ip_port, all_data.data['timeout'],
                sites_list, all_data.data['delay_between']
        ).items():
            text += f"Site {site_name}::\n{form_an_output(result[1], mode)}\n\n"
    except Exception as e:
        text = "{}\n\nPlease, provide something to check in the correct format.".format(
            exc_to_str(e, title='An exception occurred:\n\n')
        )

    bot.enc_edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=id_of_message_to_change,
        disable_web_page_preview=True
    )

@bot.message_handler(content_types=['document'])
def handle_check_proxy_list_from_document(m: Message):
    answer_message_id = bot.send_message(
        chat_id=m.chat.id,
        text="Trying to verify all the proxies in this file...",
        reply_to_message_id=m.message_id
    ).message_id
    raw_file = bot.get_file(m.document.file_id)
    raw_file_type = raw_file.file_path.split('.')[-1]
    if raw_file_type == 'txt':
        filter_condition = mode = None
        portion = all_data.data['portion']
        answer_text = ""
        if m.caption:
            args_list = m.caption.split(' ')
            parsed_arguments = {a[1:]: args_list[i + 1] for i, a in enumerate(args_list[:-1]) if
                                i % 2 == 0 and a[0] == '-'}
            if portion := parsed_arguments.get(all_data.data['portion_argument']):
                try:
                    portion = int(portion)
                except ValueError:
                    answer_text += "Was not able to convert the portion argument to an integer.\n" \
                                   f"Going to use the value : {portion}\n\n"

            if filter_condition := parsed_arguments.get(all_data.data['filter_condition_argument']):
                try:
                    filter_condition = not bool(int(filter_condition))
                except ValueError:
                    answer_text += "Was not able to convert the filter_condition argument to an integer.\n" \
                                   f"Going to use the value : {filter_condition}\n\n"

            mode = parsed_arguments.get(all_data.data['mode_argument'])

        mode = modes[mode] if mode in modes else 1

        bot.edit_message_text(
            chat_id=m.chat.id, message_id=answer_message_id,
            text=answer_text + f"Using those values:\nportion : {portion}\n"
                               f"not_desired : {filter_condition}\nmode: {mode}"
        )
        thread = threading.Thread(
            target=check_proxy_list_from_document,
            args=(m.chat.id, raw_file.file_path, portion, filter_condition, mode)
        )
        thread.start()
    else:
        bot.edit_message_text(
            chat_id=m.chat.id, message_id=answer_message_id,
            text="Not supported file type. Unable to check. Try again with .txt file"
        )

def check_proxy_list_from_document(
    chat_id, telegram_raw_file_path: str, portion: int, not_desired: bool, mode: int
):
    raw_file_path = all_data.data['raw_file_name'] + '.txt'
    with open(raw_file_path, 'wb') as f:
        f.write(bot.download_file(telegram_raw_file_path))
    result = check_proxies_from_document(
        all_data.data['checked_file_name'], raw_file_path, all_data.data['timeout'], mode, portion, not_desired
    )
    if result[0]:
        bot.send_document(
            chat_id=chat_id,
            document=open(all_data.data['checked_file_name'] + ".txt", 'rb'),
            visible_file_name=result[1]
        )
    else:
        bot.send_message(
            chat_id=chat_id,
            text=result[1]
        )

def main():
    define_handlers_of_dynamic_commands()
    app.run("0.0.0.0", port=os.getenv("PORT", 3000))

if __name__ == "__main__":
    main()



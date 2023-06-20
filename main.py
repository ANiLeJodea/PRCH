# Python default packages
import os
import threading
import time
# import argparse

# External packages
import requests
from replit.database import Database
from telebot import types
from flask import Flask, request

# Project packages
from encbot import EncTeleBot
from verify import check_proxies_from_document, \
    verify_proxy_on_site_list, verify_proxy_on_ipinfo
from helpers import exc_to_str, data_to_str, form_an_output

# site_list_command_parser = argparse.ArgumentParser()
# site_list_command_parser.add_argument(all_db['main_data']['site_list_argument'])  # -sites
# parser.add_argument(all_db['main_data'][''])  # -

bot = EncTeleBot(token=os.environ["BOT_TOKEN"], skip_pending=True)
db = Database(os.environ["REPLIT_DB_URL"])
app = Flask(__name__)

# 1 - silent ; 2 - verbose ; 3 - expressive
modes = {None: db['main_data']['mode'], "silent": 1, "verbose": 2, "expressive": 3}

@app.route('/', methods=["POST"])
def handle_request():
    if request.headers.get('content-type') == "application/json":
        update = types.Update.de_json(request.stream.read().decode("utf-8"))
        if update.message and str(update.message.from_user.id) in db['admin_id'].values():
            bot.process_new_updates([update])
    return "OK"


@bot.message_handler(commands=['info'])
def handle_info(m: types.Message):
    answer_text = data_to_str(db['main_data'], mode=db['main_data']['parse_mode']) + \
                  f"\n\nTHIS_IP : {os.environ['THIS_IP']}\n\nSTARTED_TIME : {os.environ['TIME_STARTED']}\n\n" \
                  "Secs have passed from program start : " \
                  f"{round(time.time() - float(os.environ['TIME_STARTED_INT']), 4)}\n\n"
    message_id_to_answer = m.message_id

    try:
        message_id_to_answer = bot.send_document(
            m.chat.id, open(f"{db['main_data']['checked_file_name']}.txt", 'rb')).message_id
        answer_text = f"Last {db['main_data']['checked_file_name']} ⏫\n" + answer_text
    except FileNotFoundError:
        answer_text += "Seems like there is no checked file on server yet. Try to make it"
    bot.enc_send_message(
        chat_id=m.chat.id,
        text=answer_text,
        reply_to_message_id=message_id_to_answer,
        parse_mode=db['main_data']['parse_mode'],
        disable_web_page_preview=True
    )

def define_handlers_of_dynamic_commands():

    @bot.message_handler(commands=[db['main_data']['command_for_update_data']])
    def handle_update_data(m: types.Message):
        modes[None] = db['main_data']['mode']
        bot.send_message(m.chat.id, f"Updating by calling define_handlers_of_dynamic_commands()...")
        define_handlers_of_dynamic_commands()

    @bot.message_handler(commands=[db['main_data']['command_for_ip_info']])
    def handle_ip_info_check(m: types.Message):
        proxy = m.text[len(db['main_data']['command_for_ip_info']) + 2:]
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

    @bot.message_handler(commands=[db['main_data']['command_for_site_list']])
    def handle_site_list_check(m: types.Message):
        answer_message_id = bot.send_message(m.chat.id, "Doing on a site list...").message_id
        thread = threading.Thread(
            target=perform_site_list_check, args=(
                m.chat.id,
                answer_message_id,
                m.text[len(db['main_data']['command_for_site_list']) + 2:],
                modes[None]
            )
        )
        thread.start()

def perform_ip_info_check(chat_id, id_of_message_to_change, proxy_data, mode: int):
    bot.enc_edit_message_text(
        text=form_an_output(
            verify_proxy_on_ipinfo(proxy_data, timeout=db['main_data']['timeout'])[1],
            mode
        ),
        chat_id=chat_id,
        message_id=id_of_message_to_change
    )


def perform_site_list_check(chat_id, id_of_message_to_change, args, mode: int):
    try:
        args_list: list = args.split(' ')
        proxy_ip_port = args_list.pop(0)
        parsed_arguments = {a[1:]: args_list[i+1] for i, a in enumerate(args_list[:-1]) if i % 2 == 0 and a[0] == '-'}
        if sites := parsed_arguments.get(db['main_data']['site_list_argument']):
            sites_list = [f'https://{s}' for s in sites.split(',')]
        else:
            sites_list = db['main_data']['default_site_list_to_check']
        text = "Results:\n" + '\n\n'.join(f"Site {site_name}::\n{form_an_output(result[1], mode)}"
                                          for site_name, result in verify_proxy_on_site_list(
            proxy_ip_port, db['main_data']['timeout'],
            sites_list, db['main_data']['delay_between']
        ).items())
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
def handle_check_proxy_list_from_document(m: types.Message):
    answer_message_id = bot.send_message(
        chat_id=m.chat.id,
        text="Trying to verify all the proxies in this file...",
        reply_to_message_id=m.message_id
    ).message_id
    raw_file = bot.get_file(m.document.file_id)
    raw_file_type = raw_file.file_path.split('.')[-1]
    if raw_file_type == 'txt':
        filter_condition = mode = None
        portion = db['main_data']['portion']
        answer_text = ""
        if m.caption:
            args_list = m.caption.split(' ')
            parsed_arguments = {a[1:]: args_list[i + 1] for i, a in enumerate(args_list[:-1]) if
                                i % 2 == 0 and a[0] == '-'}
            if portion := parsed_arguments.get(db['main_data']['portion_argument']):
                try:
                    portion = int(portion)
                except ValueError:
                    answer_text += "Was not able to convert the portion argument to an integer.\n" \
                                   f"Going to use the value : {portion}\n\n"

            if filter_condition := parsed_arguments.get(db['main_data']['filter_condition_argument']):
                try:
                    filter_condition = not bool(int(filter_condition))
                except ValueError:
                    answer_text += "Was not able to convert the filter_condition argument to an integer.\n" \
                                   f"Going to use the value : {filter_condition}\n\n"

            mode = parsed_arguments.get(db['main_data']['mode_argument'])

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
    raw_file_path = db['main_data']['raw_file_name'] + '.txt'
    with open(raw_file_path, 'wb') as f:
        f.write(bot.download_file(telegram_raw_file_path))
    result = check_proxies_from_document(
        db['main_data']['checked_file_name'], raw_file_path, db['main_data']['timeout'], mode, portion, not_desired
    )
    if result[0]:
        bot.send_document(
            chat_id=chat_id,
            document=open(db['main_data']['checked_file_name'] + ".txt", 'rb'),
            visible_file_name=result[1]
        )
    else:
        bot.send_message(
            chat_id=chat_id,
            text=result[1]
        )

def main():
    os.environ['LOG_FORUM_ID'], os.environ['LOG_TOPIC_ID'] = db['main_data']['log_entity'].split(" ")
    os.environ['THIS_IP'] = requests.get('https://ipinfo.io/ip').text
    os.environ['TIME_STARTED_INT'] = str(time.time())
    os.environ['TIME_STARTED'] = time.strftime('%H:%M:%S %d-%m-%Y')
    bot.send_message(
        chat_id=os.environ['LOG_FORUM_ID'],
        message_thread_id=os.environ['LOG_TOPIC_ID'],
        text="Tried to set a webhook with telebot.\nResponse: {}\nRunning on {}\nUsing {} mode to send info".format(
            bot.set_webhook(os.environ["EXTERNAL_URL"]),
            os.environ['THIS_IP'],
            db['main_data']['parse_mode']
        )
    )
    define_handlers_of_dynamic_commands()
    app.run("0.0.0.0", port=os.getenv("PORT", 3000))

if __name__ == "__main__":
    main()



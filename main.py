# Pre-installed packages
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# External packages
import requests
import telebot
from flask import Flask, request

LOG_FORUM_ID, LOG_TOPIC_ID = os.environ['LOG_ENTITY'].split(' ')
app = Flask(__name__)
bot = telebot.TeleBot(token=os.environ["BOT_TOKEN"])
ADMIN_IDS = [652015662, 1309387740]
command_for_ip_info = "cs"
command_for_site_list = "cms"
default_site_list_to_check = ["https://www.google.com", "https://openai.com", "https://instagram.com"]
gtimeout: int = 6
gportion: int = 100
this_ip = requests.get('https://ipinfo.io/ip').text

@app.route('/', methods=["POST"])
def handle_request():
    if request.headers.get('content-type') == "application/json":
        update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
        m = update.message
        if m.from_user.id in ADMIN_IDS:
            bot.process_new_updates([update])
    return "OK"


@bot.message_handler(commands=['set_timeout'])
def handle_set_timeout(m):
    global gtimeout
    before = f"Timeout before: {gtimeout}"
    gtimeout = int(m.text[len('set_timeout')+2:])
    bot.send_message(m.chat.id, f"{before}\nNow: {gtimeout}")

@bot.message_handler(commands=['set_portion'])
def handle_set_timeout(m):
    global gportion
    before = f"Portion before: {gportion}"
    gportion = int(m.text[len('set_portion')+2:])
    bot.send_message(m.chat.id, f"{before}\nNow: {gportion}")


@bot.message_handler(commands=['start'])
def handle_start(m):
    bot.send_message(m.chat.id, "The bot is ready to perform\n"
                                f"Send command /{command_for_ip_info} followed by the proxy "
                                "(ip, port) you want to check with ipinfo.io/ip"
                                f"Send command /{command_for_site_list} followed by the proxy "
                                f"(ip, port) you want to verify on multiple sites")

@bot.message_handler(commands=[command_for_ip_info])
def handle_ip_info_check(m):
    answer_message_id = bot.send_message(m.chat.id, "Trying to verify...").id
    thread = threading.Thread(
        target=perform_ip_info_check, args=(
            m.chat.id,
            answer_message_id,
            m.text[len(command_for_ip_info) + 2:]
        )
    )
    thread.start()

def perform_ip_info_check(chat_id, id_of_message_to_change, proxy_ip_port):
    # proxy_ip_port_list = proxy_ip_port.split(':')
    if ':' in proxy_ip_port:
        text = verify_proxy_on_ipinfo(proxy_ip_port)[1]
    else:
        text = "Please, provide something to check in the correct format."

    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=id_of_message_to_change
    )

def verify_proxy_on_ipinfo(
        proxy_ip_port: str
) -> tuple[bool, str, str]:
    try:
        t = time.time()
        r = requests.get(
            "https://ipinfo.io/ip", proxies={"http": proxy_ip_port, "https": proxy_ip_port}, timeout=gtimeout
        )
        time_taken = round(time.time() - t, 4)
        if r.status_code == 200:
            if r.text in proxy_ip_port:
                return True, f"The proxy worked.\nr.text: {r.text}\nTime taken: {time_taken}", proxy_ip_port
            return False, f"Seems like IpInfo didnt show the ip of the proxy.\nthis_ip: {this_ip}" \
                          f"\nr.text: {r.text}\nTime taken: {time_taken}", proxy_ip_port
        return False, "Seems like the proxy didnt work.\n" \
                      f"r.status_code: {r.status_code}\nr.text: {r.text}\nTime taken: {time_taken}", proxy_ip_port

    except Exception as e:
        return False, f"Got the exception:\n{e}\n\nException class: {e.__class__}", proxy_ip_port

@bot.message_handler(commands=[command_for_site_list])
def handle_site_list_check(m):
    answer_message_id = bot.send_message(m.chat.id, "Trying to verify on a site list...").id
    thread = threading.Thread(
        target=perform_site_list_check, args=(
            m.chat.id,
            answer_message_id,
            m.text[len(command_for_site_list) + 2:]
        )
    )
    thread.start()

def perform_site_list_check(chat_id, id_of_message_to_change, args):
    args_list: list = args.split(':')
    args_list_len: int = len(args_list)
    if 1 < args_list_len < 4:
        text = "Results:\n"
        if args_list_len == 2:
            proxy_ip, proxy_port = args_list
            sites_list = default_site_list_to_check
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

def verify_proxy_on_site_list(
        proxy_ip: str, proxy_port: str, site_list: list
) -> dict:
    # delay_between: int = 2
    test_results = {}
    proxy_ip_port = f"{proxy_ip}:{proxy_port}"
    for site in site_list:
        try:
            t = time.time()
            r = requests.get(site, proxies={"http": proxy_ip_port, "https": proxy_ip_port}, timeout=gtimeout)
            time_taken = round(time.time() - t, 4)
            if r.status_code == 200:
                test_results[site] = (True, f"The proxy worked.\nTime taken: {time_taken}")
            else:
                test_results[site] = (False, "Seems like the proxy didnt work.\n"
                                             f"r.status_code: {r.status_code}\n"
                                             f"Time taken: {time_taken}")
        except Exception as e:
            test_results[site] = (False, f"Got an exception:\n{e}\n\nException class: {e.__class__}")

        # time.sleep(delay_between)

    return test_results

@bot.message_handler(content_types=['document'])
def handle_check_proxy_list_from_document(m: telebot.types.Message):
    answer_message_id = bot.send_message(
        chat_id=m.chat.id,
        text="Trying to verify all the proxies in this file...",
        reply_to_message_id=m.message_id
    ).id
    raw_file = bot.get_file(m.document.file_id)
    raw_file_type = raw_file.file_path.split('.')[-1]
    if raw_file_type == 'txt':
        try:
            portion = int(m.caption)
        except TypeError:
            bot.edit_message_text(
                chat_id=m.chat.id, message_id=answer_message_id,
                text="Was not able to convert the caption of this message to an integer."
                     f"Going to use the default value {gportion}"
            )
            portion = gportion
        thread = threading.Thread(
            target=check_proxy_list_from_document,
            args=(m.chat.id, raw_file.file_path, portion)
        )
        thread.start()
    else:
        bot.edit_message_text(
            chat_id=m.chat.id, message_id=answer_message_id,
            text="Not supported file type. Unable to check. Try again with .txt file"
        )

def check_proxy_list_from_document(
    chat_id: str, raw_fpath: str, portion: int
):
    try:
        raw_file_name = 'raw.txt'
        checked_file_name = 'checked.txt'
        with open(raw_file_name, 'wb') as f:
            f.write(bot.download_file(raw_fpath))
        with open(raw_file_name, 'r') as fr, \
                open(checked_file_name, 'w') as fw, \
                ThreadPoolExecutor(max_workers=portion) as executor:
            # proxies = fr.read().splitlines()
            fw.write("\n".join(f"{proxy} -> {text}"
                               for bool_result, text, proxy in
                               executor.map(verify_proxy_on_ipinfo, fr.read().splitlines())
                               if bool_result))
        bot.send_document(
            chat_id=chat_id,
            document=open(checked_file_name, 'rb'),
            # visible_file_name=f"CHECKED PROXIES"
        )
    except Exception as e:
        bot.send_message(
            chat_id=chat_id,
            text=f"E:\n{e}\nE class: {e.__class__}",
            disable_web_page_preview=True
        )

if __name__ == "__main__":
    app.run("0.0.0.0", port=os.getenv("PORT", 3000))




# Pre-installed packages
import os
import threading
import time

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

@app.route('/', methods=["POST"])
def handle_request():
    if request.headers.get('content-type') == "application/json":
        update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
        m = update.message
        if m.from_user.id in ADMIN_IDS:
            bot.process_new_updates([update])
    return "OK"


@bot.message_handler(commands=['start'])
def say(m):
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
            m.text[len(command_for_site_list) + 2:]
        )
    )
    thread.start()

def perform_ip_info_check(chat_id, id_of_message_to_change, proxy_ip_port):
    proxy_ip_port_list = proxy_ip_port.split(':')
    if len(proxy_ip_port_list) == 2:
        text = verify_proxy_on_ipinfo(*proxy_ip_port_list)
    else:
        text = "Please, provide something to check in the correct format."

    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=id_of_message_to_change
    )

def verify_proxy_on_ipinfo(
        proxy_ip: str, proxy_port: str, timeout: int = 5
) -> str:
    try:
        proxy_ip_port = f"{proxy_ip}:{proxy_port}"
        t = time.time()
        r = requests.get(
            "https://ipinfo.io/ip", proxies={"http": proxy_ip_port, "https": proxy_ip_port}, timeout=timeout
        )
        time_taken = round(time.time() - t, 4)
        if r.status_code == 200:
            if r.text.strip() == proxy_ip:
                return f"The proxy worked.\nr.text: {r.text}\nTime taken: {time_taken}"
            else:
                return "Seems like IpInfo didnt show the ip of the proxy properly." \
                       f"\nr.text: {r.text}\nTime taken: {time_taken}"

    except Exception as e:
        return f"Got the exception:\n{e}\n\nException class: {e.__class__}"

@bot.message_handler(commands=[command_for_site_list])
def handle_site_list_check(m):
    answer_message_id = bot.send_message(m.chat.id, "Trying to verify on a site list...").id
    thread = threading.Thread(
        target=perform_ip_info_check, args=(
            m.chat.id,
            answer_message_id,
            m.text[len(command_for_site_list) + 2:]
        )
    )
    thread.start()

def perform_site_list_check(chat_id, id_of_message_to_change, args):
    args_list = args.split(':')
    args_list_len: int = len(args_list)
    if args_list_len == 2:
        text = "Results:\n"
        for key, value in verify_proxy_on_site_list(
                args_list[0], args_list[1], default_site_list_to_check).items():
            text += f"Site: {key} -> {value}\n"
    elif args_list_len == 3:
        proxy_ip, proxy_port, sites = args_list
        sites_list = sites.split(',')
        text = verify_proxy_on_site_list(proxy_ip, proxy_port, sites_list)
    else:
        text = "Please, provide something to check in the correct format."

    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=id_of_message_to_change
    )

def verify_proxy_on_site_list(
        proxy_ip: str, proxy_port: str, site_list: list, timeout: int = 5, delay_between: int = 3
) -> dict:
    test_results = {}
    proxy_ip_port = f"{proxy_ip}:{proxy_port}"
    for site in site_list:
        try:
            t = time.time()
            r = requests.get(site, proxies={"http": proxy_ip_port, "https": proxy_ip_port}, timeout=timeout)
            time_taken = round(time.time() - t, 4)
            if r.status_code == 200:
                test_results[site] = (True, time_taken)
        except Exception as e:
            test_results[site] = (False, e)
        time.sleep(delay_between)

    return test_results


if __name__ == "__main__":
    app.run("0.0.0.0", port=os.getenv("PORT", 3000))





import os
import threading
import time

import requests
import telebot
from flask import Flask, request

LOG_FORUM_ID, LOG_TOPIC_ID = os.environ['LOG_ENTITY'].split(' ')
app = Flask(__name__)
bot = telebot.TeleBot(token=os.environ["BOT_TOKEN"])
ADMIN_IDS = [652015662, 1309387740]

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
    bot.send_message(m.chat.id, "The bot is ready to perform\nSend command /c followed by the pr u want to check")

@bot.message_handler(commands=['c'])
def run_and_answer(m):
    msg_id = bot.send_message(m.chat.id, "Trying to verify...").id
    thread = threading.Thread(target=perform, args=(m.chat.id, msg_id, m.text[3:]))
    thread.start()

def perform(chat_id, id_of_message_to_change, pripp):
    pripp_list = pripp.split(':')
    if len(pripp_list) == 2:
        text = verify_pr_on_ipinfo(*pripp_list)
    else:
        text = "Please, provide something to check in the correct format."
    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=id_of_message_to_change
    )

def verify_pr_on_ipinfo(
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
                return f"Time taken: {time_taken}"
            else:
                return "IpInfo did not show the ip of the proxy. " \
                       f"Seems like a proxy is not working.\nTime taken: {time_taken}"

    except Exception as e:
        return f"Got the exception:\n{e}\nClass: {e.__class__}"



if __name__ == "__main__":
    app.run("0.0.0.0", port=3000)





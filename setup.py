# Python default packages
from os import environ

# External packages
import requests

# Project packages
from data import get_data

all_data: dict = get_data()

environ['LOG_FORUM_ID'], environ['LOG_TOPIC_ID'] = all_data['log_entity']

environ['THIS_IP'] = requests.get('https://ipinfo.io/ip').text

requests.get(f"https://api.telegram.org/bot{environ['BOT_TOKEN']}/sendMessage", {
    'chat_id': environ['LOG_FORUM_ID'],
    'message_thread_id': environ['LOG_TOPIC_ID'],
    'text': "Tried to set a webhook. Response:\n" +
            requests.get(f"https://api.telegram.org/bot{environ['BOT_TOKEN']}/setwebhook?url="
                         f"{environ['EXTERNAL_URL']}").json()['description'] +
            "\nRunning on {}\nADMINS:\n{}".format(environ['THIS_IP'], '\n'.join(a for a in all_data['admins']))
})


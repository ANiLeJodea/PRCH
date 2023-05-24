import os

import requests

LOG_FORUM_ID, LOG_TOPIC_ID = os.environ['LOG_ENTITY'].split(' ')

response = requests.get(f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}/sendMessage", {
    'chat_id': LOG_FORUM_ID,
    'top_msg_id': LOG_TOPIC_ID,
    'text': requests.get(f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}/setwebhook?url="
                         f"{os.environ['EXTERNAL_URL']}").text
})


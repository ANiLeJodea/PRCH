import os

import requests

LOG_FORUM_ID, LOG_TOPIC_ID = os.environ['LOG_ENTITY'].split(' ')

requests.get(f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}/sendMessage", {
    'chat_id': LOG_FORUM_ID,
    'message_thread_id': LOG_TOPIC_ID,
    'text': "Tried to set a webhook. Response:\n" +
            requests.get(f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}/setwebhook?url="
                         f"{os.environ['EXTERNAL_URL']}").json()['description']
})

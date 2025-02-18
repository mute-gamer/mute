import time
from googleapiclient.discovery import build
from telegram import Bot
import requests
import re
import schedule
import threading
import random
from flask import Flask
import webbrowser

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def open_browser():
    webbrowser.open_new('http://127.0.0.1:8080/')

if __name__ == "__main__":
    threading.Timer(1.25, open_browser).start()
    threading.Thread(target=run, daemon=True).start()

YOUTUBE_API_KEYS = [
    'AIzaSyDDM8G5jXdlmKKPCi9KpDwa1G3Mo-gi02A',
    'AIzaSyCNH1ZgCuygRYEZsoaJRWEbseNFmVJEb4g',
    'AIzaSyC-CEfWXMY0pXjcmkmOZpOTZKY8NY3dCuI',
    'AIzaSyDtTyueb9qkbtgsrd-FWqPaNYZHkG-wCeU',
    'AIzaSyAYPH6k8xDZMF6P_v9nfgB3E8OKcqOfrzs',
    'AIzaSyAghoEdbd2GCoZZAJ68yVdeJYCptyYeW_k',
    'AIzaSyDZqecQ9YnwfhhokGZDzYDPgb1JiSRXmCI',
    'AIzaSyDLyVINlBMMfBOf5XocAS6vsNYs4NJd9bs',
    'AIzaSyC1lDR0FB40KHkC8syn1ZAIffHPwiz--jU',
    'AIzaSyCFeitrKMbFepY8_quLNL9NLSwVA24LopM',
    'AIzaSyBgPiOu5ZYAglPd9qXWWI46BVYju8ByprI',
    'AIzaSyBxIHbfk0rlLW4U500mPMtkf6d4AAfzOu',
    'AIzaSyAkryqB92GGZPaTiSK0TI4ExScW9UwBNQ0',
    'AIzaSyCOVs0Br_9gjUz5ljMZ0eKm-Ucm5W9ZkyU',
    'AIzaSyBS6BiVCjr7bj5zKPpu4wpZFQFAXxta9Nk',
    'AIzaSyALyWV0kEP8btz2ED_TllFJCvGBAQBCGPc',
    'AIzaSyAZMlTovX4lGSeitWxmZK-hFYj79KUpG3Q',
    'AIzaSyDJENrROHwLY3SxfQMO1NAIrhx--hkLK7w',
    'AIzaSyDD-89hm3BWA6CxIYvOBkuwOGXoRe2NRlE',
    'AIzaSyCE1eqlNzuJJh8mRG7VpP7oe6Vb3CaezFM',
    'AIzaSyBY74ewHLiXFZyorhOFnNOevQmbm0imjrs',
    'AIzaSyDL-HbpXnztN3zacAjodjTauEOwVSmpL2U',
    'AIzaSyAc1Rsf_sP07QJamEwn6_pjlcOxxP4q3Wg',
    'AIzaSyCFoiHqs-wn50V3xWCGJiRlr6sERwEY0fI',
    'AIzaSyDA_qeyoot2lQp4e8LbQRWpjLldFcVGrdg',
    'AIzaSyDV2TWIkh8NJITr25lDWYpPbCwv4Cp_1E0',
    'AIzaSyCw_5iFM_msHaVrejjxwf6as688FI_-FFs',
    'AIzaSyBGzQBvbp1SwAHxcMOLk2SKB1rRu3OQmHg',
    'AIzaSyDGE8UDEO-2BashKurUSGte5GXhXWgCYo0',
    'AIzaSyCBp7Ip0VoOiHZ2aQDcY34SE07Baq_laXE'
]

TELEGRAM_BOT_TOKEN = "7817464511:AAFvpS58HxWAreM6uzhEVC_WHSj-qUdE4zw"
TELEGRAM_CHAT_ID = "-1002282239246"
CHANNEL_ID = "UC4mvivsBEX3Mq7us5U4lb7w"

def get_youtube_service():
    for key in YOUTUBE_API_KEYS:
        try:
            return build("youtube", "v3", developerKey=key)
        except Exception as e:
            print(f"Error with API key {key}: {e}")
    raise Exception("All API keys have been exhausted.")

youtube = get_youtube_service()
bot = Bot(token=TELEGRAM_BOT_TOKEN)

last_post_id = None
last_video_id = None

def get_community_posts():
    global last_post_id
    url = f"https://www.youtube.com/channel/{CHANNEL_ID}/community"
    response = requests.get(url)
    post_id_match = re.search(r'"postId":"(.*?)"', response.text)
    if post_id_match:
        post_id = post_id_match.group(1)
        if post_id != last_post_id:
            last_post_id = post_id
            bot.send_message(TELEGRAM_CHAT_ID, f"🔥 New Community Post! \n👉 https://www.youtube.com/post/{post_id}")

def get_latest_video():
    global last_video_id
    request = youtube.search().list(part="snippet", channelId=CHANNEL_ID, maxResults=1, order="date", type="video")
    response = request.execute()
    if response["items"]:
        video_id = response["items"][0]["id"]["videoId"]
        if video_id != last_video_id:
            last_video_id = video_id
            bot.send_message(TELEGRAM_CHAT_ID, f"🎥 New Video! \n🚀 https://www.youtube.com/watch?v={video_id}")

def send_promotion():
    messages = [
        "🚨 Don't miss out! Subscribe now! 🛎️",
        "🔥 Join the adventure! Subscribe! 💥",
        "🎯 Enjoy the content? Support us by subscribing! 🚀",
    ]
    bot.send_message(TELEGRAM_CHAT_ID, f"{random.choice(messages)}\n👉 https://www.youtube.com/channel/{CHANNEL_ID}")

schedule.every(1).hours.do(send_promotion)

def schedule_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    threading.Thread(target=schedule_loop, daemon=True).start()
    while True:
        get_community_posts()
        get_latest_video()
        time.sleep(30)

if __name__ == "__main__":
    main()

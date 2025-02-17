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
    'AIzaSyCBp7Ip0VoOiHZ2aQDcY34SE07Baq_laXE',
    'AIzaSyBZMCFhHHDdR41rbCr9kJRuHI83VNIYxcs',
    'AIzaSyBFuBg-I2OeqiA-2Vy5CG1rtC2tnpHlcgo',
    'AIzaSyCZ9DTi4y6EtFpDIVblJGMwclW_kkxcgK4',
    'AIzaSyA7hwxgJQUJcBQMiqPF5xGanYr_JpBbf1w',
    'AIzaSyB5Kf3xfSH_VYMt8eDu2Y_Ju0Z8xDc7xuw',
    'AIzaSyAYRrzOXD4ggJFCzD0VNdBQ_hO_vGB_TR4',
    'AIzaSyDkAW17vi-mbXSfH_rn6bsbLvWmUyYBAmI',
    'AIzaSyCEbkxInSUYIlGCfmOhbpgqt_VA17ifMCk',
    'AIzaSyB1m4Gu3pCjn6xxphAbpg8mx04SGIfK6ys',
    'AIzaSyBgXOxh0_eYoawKffgjaZZ4otxPh6DKx40'
    # ...
]

TELEGRAM_BOT_TOKEN = "7817464511:AAFvpS58HxWAreM6uzhEVC_WHSj-qUdE4zw"
TELEGRAM_CHAT_ID = "-1002282239246"
CHANNEL_ID = "UC4mvivsBEX3Mq7us5U4lb7w"

current_api_index = 0

def get_youtube_service():
    global current_api_index
    while current_api_index < len(YOUTUBE_API_KEYS):
        try:
            return build("youtube", "v3", developerKey=YOUTUBE_API_KEYS[current_api_index])
        except Exception as e:
            print(f"Error with API key {YOUTUBE_API_KEYS[current_api_index]}: {e}")
            current_api_index += 1
    raise Exception("All API keys have been exhausted.")

youtube = get_youtube_service()
bot = Bot(token=TELEGRAM_BOT_TOKEN)

last_post_id = None
last_video_id = None

def get_community_posts():
    global last_post_id
    url = f"https://www.youtube.com/channel/{CHANNEL_ID}/community"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Page fetched successfully.")

        # جستجوی آی‌دی پست
        post_id_match = re.search(r'"postId":"(.*?)"', response.text)

        if post_id_match:
            post_id = post_id_match.group(1)
            post_url = f"https://www.youtube.com/post/{post_id}"

            if post_id != last_post_id:
                last_post_id = post_id
                bot.send_message(TELEGRAM_CHAT_ID, f"🔥 New Community Post!\n\n👉 <a href='{post_url}'>Check it out on YouTube</a>", parse_mode="HTML")
            else:
                print("No new post found.")
        else:
            print("No post ID found.")
    else:
        print(f"Failed to fetch page. Status code: {response.status_code}")



def get_latest_video():
    global last_video_id, youtube
    try:
        request = youtube.search().list(part="snippet", channelId=CHANNEL_ID, maxResults=1, order="date", type="video")
        response = request.execute()

        if response["items"]:
            video = response["items"][0]
            video_id = video["id"]["videoId"]
            url = f"https://www.youtube.com/watch?v={video_id}"

            if video_id != last_video_id:
                last_video_id = video_id
                bot.send_message(
                    TELEGRAM_CHAT_ID,
                    f"🎥 New Video Uploaded!\n\n🚀 <a href='{url}'>Watch on YouTube</a>",
                    parse_mode="HTML"
                )
    except Exception as e:
        print(f"Error fetching latest video: {e}")
        youtube = get_youtube_service()

def send_promotion():
    messages = [
        "🚨 Don't miss out! Subscribe now and stay updated with the latest content! 🛎️🔥",
        "🔥 Join the adventure! Hit that subscribe button and become part of the family! 💥❤️",
        "🎯 Enjoy the content? Support us by subscribing! Every sub counts! 🚀✨",
        "⚡ Stay connected! Subscribe and never miss an update! 📰🔔",
        "🎉 Stay connected! Subscribe and stay ahead with all the newest videos! 🌟",
        "⚡ Like what you see? Hit that subscribe button for more exciting updates! 💫",
        "🔥 Don’t wait! Subscribe now and join the fun journey! 🚀💖",
        "📣 Loving the content? Make sure to subscribe and never miss a beat! 🎧✨",
        "✨ New videos await! Subscribe and enjoy exclusive updates! 💥",
        "🚀 Get ready for the best! Subscribe now and be part of our adventure! 🎉",
        "💡 Want more awesome content? Subscribe today and stay in the loop! 🔔",
        "🔥 Excited for more? Subscribe and keep up with all the latest content! ❤️",
        "🎯 It’s just one click away! Subscribe and join the journey with us! 🚀",
        "🎉 Don’t miss a moment! Subscribe now and stay updated! 🌟✨",
        "💥 Join the fun! Hit that subscribe button for more adventures! ❤️",
        "🚨 Stay connected! Subscribe now for exclusive updates and new videos! 🛎️",
        "⚡ Ready for more? Subscribe and get all the latest updates! 🎉",
        "🔥 The fun is just getting started! Subscribe and don’t miss out! 🚀",
        "🌟 Want more exciting content? Subscribe and stay ahead! 🎯",
        "✨ Join our growing community! Subscribe for more amazing content! 🎉",
        "📢 Like what you see? Subscribe today and become part of the family! 🚀",
    ]
    bot.send_message(
        TELEGRAM_CHAT_ID,
        f"{random.choice(messages)}\n👉 <a href='https://www.youtube.com/channel/{CHANNEL_ID}'>Subscribe Here</a>",
        parse_mode="HTML"
    )

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
        print("Bot is running...")
        time.sleep(30)

if __name__ == "__main__":
    main()

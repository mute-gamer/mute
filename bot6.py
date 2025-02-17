import time
from googleapiclient.discovery import build
from telegram import Bot
import requests
import re
import threading
import random
from flask import Flask
import asyncio

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

youtube_api_keys = [
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
]

tg_bot_token = "7817464511:AAFvpS58HxWAreM6uzhEVC_WHSj-qUdE4zw"
tg_chat_id = "-1002282239246"
channel_id = "UC4mvivsBEX3Mq7us5U4lb7w"

bot = Bot(token=tg_bot_token)
current_api_index = 0

# دریافت API یوتیوب
def get_youtube_service():
    global current_api_index
    while current_api_index < len(youtube_api_keys):
        try:
            print(f"[INFO] Trying API Key {current_api_index + 1}...")
            return build("youtube", "v3", developerKey=youtube_api_keys[current_api_index])
        except Exception as e:
            print(f"[ERROR] API Key {current_api_index + 1} failed: {e}")
            current_api_index += 1
    raise Exception("All API keys have been exhausted.")

youtube = get_youtube_service()
last_post_id = None
last_video_id = None

# دریافت و ارسال پست‌های Community
async def get_community_posts():
    global last_post_id
    url = f"https://www.youtube.com/channel/{channel_id}/community"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        post_id_match = re.search(r'"postId":"(.*?)"', response.text)
        if post_id_match:
            post_id = post_id_match.group(1)
            post_url = f"https://www.youtube.com/post/{post_id}"

            if post_id != last_post_id:
                last_post_id = post_id
                print(f"[INFO] New Community Post: {post_url}")
                await bot.send_message(tg_chat_id, f"🔥 New Community Post!\n\n👉 <a href='{post_url}'>Check it out on YouTube</a>", parse_mode="HTML")

# دریافت و ارسال ویدیوی جدید
async def get_latest_video():
    global last_video_id, youtube
    try:
        print("[INFO] Fetching latest video...")
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=1,
            order="date",
            type="video"
        )
        response = request.execute()
        print("[INFO] API Response:", response)  # اضافه کردن پرینت برای نمایش پاسخ API

        if "items" in response and len(response["items"]) > 0:
            video = response["items"][0]
            video_id = video["id"].get("videoId")

            if not video_id:
                print("[ERROR] videoId not found in API response.")
                return

            url = f"https://www.youtube.com/watch?v={video_id}"

            if video_id != last_video_id:
                last_video_id = video_id
                print(f"[INFO] New Video Found: {url}")
                await bot.send_message(tg_chat_id, f"🎥 New Video Uploaded!\n\n🚀 <a href='{url}'>Watch on YouTube</a>", parse_mode="HTML")
            else:
                print("[INFO] No new video, same as last one.")
        else:
            print("[INFO] No video items in response.")

    except Exception as e:
        print(f"[ERROR] YouTube API Error: {e}")
        youtube = get_youtube_service()

# اجرای توابع در یک حلقه بی‌نهایت
async def main_loop():
    while True:
        await get_community_posts()
        await get_latest_video()
        await asyncio.sleep(30)

# راه‌اندازی و اجرای برنامه
def start_bot():
    asyncio.run(main_loop())

if __name__ == "__main__":
    threading.Thread(target=run, daemon=True).start()
    start_bot()

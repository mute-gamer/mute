import time
from googleapiclient.discovery import build
from telegram import Bot
import requests
import re
import schedule
import threading
import random

YOUTUBE_API_KEYS = [
    'AIzaSyDDM8G5jXdlmKKPCi9KpDwa1G3Mo-gi02A',
    'AIzaSyCNH1ZgCuygRYEZsoaJRWEbseNFmVJEb4g',
    'AIzaSyC-CEfWXMY0pXjcmkmOZpOTZKY8NY3dCuI',
]

TELEGRAM_BOT_TOKEN = "7817464511:AAFvpS58HxWAreM6uzhEVC_WHSj-qUdE4zw"
TELEGRAM_CHAT_ID = "-1002282239246"
CHANNEL_ID = "UC4mvivsBEX3Mq7us5U4lb7w"

current_api_index = 0

def get_youtube_service():
    global current_api_index
    while current_api_index < len(YOUTUBE_API_KEYS):
        try:
            print(f"Trying API key {current_api_index + 1}")
            return build("youtube", "v3", developerKey=YOUTUBE_API_KEYS[current_api_index])
        except Exception as e:
            print(f"Error with API key {current_api_index + 1}: {e}")
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
        post_id_match = re.search(r'"postId":"(.*?)"', response.text)

        if post_id_match:
            post_id = post_id_match.group(1)
            post_url = f"https://www.youtube.com/post/{post_id}"

            if post_id != last_post_id:
                last_post_id = post_id
                bot.send_message(TELEGRAM_CHAT_ID, f"🔥 New Community Post!\n\n👉 <a href='{post_url}'>Check it out on YouTube</a>", parse_mode="HTML")
                print("New community post sent.")
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
                print("New video sent.")
    except Exception as e:
        print(f"Error fetching latest video: {e}")
        youtube = get_youtube_service()

def send_promotion():
    messages = [
        "🚨 Don't miss out! Subscribe now and stay updated with the latest content! 🛎️🔥",
        "🔥 Join the adventure! Hit that subscribe button and become part of the family! 💥❤️",
        "🎯 Enjoy the content? Support us by subscribing! Every sub counts! 🚀✨",
    ]
    bot.send_message(
        TELEGRAM_CHAT_ID,
        f"{random.choice(messages)}\n👉 <a href='https://www.youtube.com/channel/{CHANNEL_ID}'>Subscribe Here</a>",
        parse_mode="HTML"
    )
    print("Promotion message sent.")

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

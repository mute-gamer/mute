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
    'AIzaSyDtTyueb9qkbtgsrd-FWqPaNYZHkG-wCeU'
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

last_video_id = None

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
        get_latest_video()
        print("Bot is running...")
        time.sleep(30)

if __name__ == "__main__":
    main()

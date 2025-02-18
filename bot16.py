import time
import asyncio
import random
import requests
import re
import schedule
import threading
from googleapiclient.discovery import build
from telegram import Bot

TELEGRAM_BOT_TOKEN = "7817464511:AAFvpS58HxWAreM6uzhEVC_WHSj-qUdE4zw"
TELEGRAM_CHAT_ID = "-1002282239246"
CHANNEL_ID = "UC4mvivsBEX3Mq7us5U4lb7w"

YOUTUBE_API_KEYS = [
    "AIzaSyDDM8G5jXdlmKKPCi9KpDwa1G3Mo-gi02A",
    "AIzaSyCNH1ZgCuygRYEZsoaJRWEbseNFmVJEb4g",
    "AIzaSyC-CEfWXMY0pXjcmkmOZpOTZKY8NY3dCuI",
]

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

async def send_telegram_message(text):
    await bot.send_message(TELEGRAM_CHAT_ID, text, parse_mode="HTML")

async def get_community_posts():
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
                await send_telegram_message(f"\ud83d\udd25 New Community Post!\n\n\ud83d\udc49 <a href='{post_url}'>Check it out on YouTube</a>")
    else:
        print(f"Failed to fetch page. Status code: {response.status_code}")

async def get_latest_video():
    global last_video_id, youtube, current_api_index
    while current_api_index < len(YOUTUBE_API_KEYS):
        try:
            request = youtube.search().list(part="snippet", channelId=CHANNEL_ID, maxResults=1, order="date", type="video")
            response = request.execute()
            if response["items"]:
                video = response["items"][0]
                video_id = video["id"]["videoId"]
                url = f"https://www.youtube.com/watch?v={video_id}"
                if video_id != last_video_id:
                    last_video_id = video_id
                    await send_telegram_message(f"\ud83c\udfa5 New Video Uploaded!\n\n\ud83d\ude80 <a href='{url}'>Watch on YouTube</a>")
            return
        except Exception as e:
            print(f"Error fetching latest video with API key {YOUTUBE_API_KEYS[current_api_index]}: {e}")
            current_api_index += 1
            if current_api_index < len(YOUTUBE_API_KEYS):
                youtube = get_youtube_service()
            else:
                print("All API keys have been exhausted.")
                break

async def send_promotion():
    messages = [
        "\ud83d\udea8 Don't miss out! Subscribe now and stay updated with the latest content! \ud83d\udee7\ufe0f\ud83d\udd25",
        "\ud83d\udd25 Join the adventure! Hit that subscribe button and become part of the family! \ud83d\udca5\u2764\ufe0f",
        "\ud83c\udfaf Enjoy the content? Support us by subscribing! Every sub counts! \ud83d\ude80\u2728",
    ]
    await send_telegram_message(f"{random.choice(messages)}\n\ud83d\udc49 <a href='https://www.youtube.com/channel/{CHANNEL_ID}'>Subscribe Here</a>")

async def main():
    while True:
        await get_community_posts()
        await get_latest_video()
        print("Bot is running...")
        await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())

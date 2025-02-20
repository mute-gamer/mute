import time
import asyncio
import random
import requests
import re
import threading
import schedule
from telegram import Bot
from flask import Flask
import os
import tweepy

port = int(os.environ.get("PORT", 10000))  

# Bot Config
TELEGRAM_BOT_TOKEN = "7817464511:AAFvpS58HxWAreM6uzhEVC_WHSj-qUdE4zw"
TELEGRAM_CHAT_ID = "-1002310803321"
CHANNEL_ID = "UC4mvivsBEX3Mq7us5U4lb7w"

# Twitter API Config
TWITTER_API_KEY = "Ap2Ci84eE6vZUZKaAOiVelTBR"
TWITTER_API_SECRET = "C1cvyO6aGpMeUTl7ZhfqMS2E5aeOdNXQ3Z4bRBxexX068AY7aF"
TWITTER_ACCESS_TOKEN = "1892531779556294656-2RPN8Lzu1Y24ghsPMI4PrOkpG1Pfy5"
TWITTER_ACCESS_SECRET = "J1vjckTu1cLXVk07OtmNXDxQx65r7gI6ONCK3XKYRsRWk"

auth = tweepy.OAuth1UserHandler(
    TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
)
twitter_api = tweepy.API(auth)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
last_post_id = None
last_video_id = None
last_x_promotion_time = 0

async def send_telegram_message(text, link=None):
    try:
        if link:
            text += f'\n\n<a href="{link}">Watch on YouTube</a>'
        await bot.send_message(TELEGRAM_CHAT_ID, text, parse_mode="HTML")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def send_twitter_post(text):
    try:
        twitter_api.update_status(text)
    except Exception as e:
        print(f"Error sending Twitter post: {e}")

async def send_promotion():
    global last_x_promotion_time
    
    messages = [
        "Don't miss out! Subscribe now and stay updated with the latest content!",
        "Join the adventure! Hit that subscribe button and become part of the family!",
        "Enjoy the content? Support us by subscribing! Every sub counts!",
        "Stay connected! Subscribe and never miss an update!",
        "New videos await! Subscribe and enjoy exclusive updates!",
    ]
    promo_message = random.choice(messages)
    promo_link = f"https://www.youtube.com/channel/{CHANNEL_ID}"
    
    await send_telegram_message(promo_message, promo_link)
    
    current_time = time.time()
    if current_time - last_x_promotion_time >= 86400:
        send_twitter_post(f"{promo_message}\n\n👉 {promo_link}")
        last_x_promotion_time = current_time

async def get_community_posts():
    global last_post_id
    url = f"https://www.youtube.com/channel/{CHANNEL_ID}/community"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        post_id_match = re.search(r'"postId":"(.*?)"', response.text)
        if post_id_match:
            post_id = post_id_match.group(1)
            post_url = f"https://www.youtube.com/post/{post_id}"
            if post_id != last_post_id:
                last_post_id = post_id
                await send_telegram_message("New Community Post!", post_url)
                send_twitter_post(f"New Community Post!\n\n📰 {post_url}")

async def get_latest_video():
    global last_video_id
    url = f"https://www.youtube.com/channel/{CHANNEL_ID}/videos"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        video_id_match = re.search(r'"videoId":"(.*?)"', response.text)
        if video_id_match:
            video_id = video_id_match.group(1)
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            if video_id != last_video_id:
                last_video_id = video_id
                await send_telegram_message("New Video Uploaded!", video_url)
                send_twitter_post(f"New Video Uploaded!\n\n🚀 {video_url}")

async def check_updates():
    while True:
        await get_latest_video()
        await get_community_posts()
        await asyncio.sleep(30)

def schedule_promotion():
    schedule.every(1).hours.do(lambda: asyncio.create_task(send_promotion()))

async def schedule_loop():
    schedule_promotion()
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

async def main():
    asyncio.create_task(check_updates())
    await schedule_loop()

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())

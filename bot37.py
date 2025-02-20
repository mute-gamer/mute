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

port = int(os.environ.get("PORT", 10000))  

# Bot Config
TELEGRAM_BOT_TOKEN = "7817464511:AAFvpS58HxWAreM6uzhEVC_WHSj-qUdE4zw"
TELEGRAM_CHAT_ID = "-1002310803321"
CHANNEL_ID = "UC4mvivsBEX3Mq7us5U4lb7w"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
last_post_id = None
last_video_id = None
last_promotion_message_id = None  # Store last promotion message ID

async def send_telegram_message(text):
    try:
        message = await bot.send_message(TELEGRAM_CHAT_ID, text, parse_mode="HTML")
        return message.message_id
    except Exception as e:
        print(f"⚠️ Error sending Telegram message: {e}")
        return None

async def delete_last_promotion():
    global last_promotion_message_id
    if last_promotion_message_id:
        try:
            await bot.delete_message(TELEGRAM_CHAT_ID, last_promotion_message_id)
        except Exception as e:
            print(f"⚠️ Error deleting Telegram message: {e}")

async def send_promotion():
    global last_promotion_message_id
    await delete_last_promotion()  # Delete previous promotion message
    
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
    last_promotion_message_id = await send_telegram_message(f"{random.choice(messages)}\n\n👉 <a href='https://www.youtube.com/channel/{CHANNEL_ID}'>Subscribe Here</a>")

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
                await send_telegram_message(f"🔥 New Community Post!\n\n📰 <a href='{post_url}'>Check it out</a>")

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
                await send_telegram_message(f"🎥 New Video Uploaded!\n\n🚀 <a href='{video_url}'>Watch Now</a>")

async def check_updates():
    while True:
        await get_latest_video()
        await get_community_posts()
        await asyncio.sleep(30)  # Check every 30 seconds

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
    asyncio.run(main())  # Runs only once

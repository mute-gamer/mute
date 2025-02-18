import os
import logging
import requests
from flask import Flask
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__)

# List of API keys for redundancy
API_KEYS = [
    'AIzaSyDDM8G5jXdlmKKPCi9KpDwa1G3Mo-gi02A',
    'AIzaSyCNH1ZgCuygRYEZsoaJRWEbseNFmVJEb4g',
    'AIzaSyC-CEfWXMY0pXjcmkmOZpOTZKY8NY3dCuI',
]
current_api_index = 0

# Telegram Bot Info
TELEGRAM_BOT_TOKEN = "7817464511:AAFvpS58HxWAreM6uzhEVC_WHSj-qUdE4zw"
TELEGRAM_CHAT_ID = "-1002282239246"

def get_youtube_service():
    global current_api_index
    logging.info(f"Trying API key {current_api_index + 1}")
    return build("youtube", "v3", developerKey=API_KEYS[current_api_index], cache_discovery=False)

def get_latest_video():
    global current_api_index
    service = get_youtube_service()
    try:
        request = service.search().list(
            part="snippet",
            channelId="UC4mvivsBEX3Mq7us5U4lb7w",
            maxResults=1,
            order="date",
            type="video"
        )
        response = request.execute()
        video_id = response["items"][0]["id"]["videoId"]
        logging.info(f"Latest video ID: {video_id}")
        return video_id
    except HttpError as e:
        error_message = e.content.decode("utf-8")
        if "quotaExceeded" in error_message:
            logging.warning("Quota exceeded for current API key. Switching to the next key...")
            current_api_index = (current_api_index + 1) % len(API_KEYS)
            return get_latest_video()  # Retry with the next key
        logging.error(f"Error fetching latest video: {e}")
        return None

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        logging.info("Message sent successfully.")
    else:
        logging.error(f"Failed to send message: {response.text}")

@app.route('/')
def home():
    public_url = os.getenv('RENDER_EXTERNAL_URL', 'Public URL not found')
    logging.info(f"Public URL: {public_url}")
    return f"Bot is running! <br> Public URL: <a href='{public_url}'>{public_url}</a>"

def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Bot is running...")
    video_id = get_latest_video()
    if video_id:
        send_telegram_message(f"New Video: https://www.youtube.com/watch?v={video_id}")
    run()

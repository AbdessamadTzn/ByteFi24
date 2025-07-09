from telethon.sync import TelegramClient
import os
from dotenv import load_dotenv

load_dotenv()


api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
channel_username = os.getenv('CHANNEL_USERNAME')


with TelegramClient('session_name', api_id, api_hash) as client:
    for message in client.iter_messages(channel_username, limit=20):  
        print(f"{message.date}")
        print(f"{message.text}")
        print("-" * 40)

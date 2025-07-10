from telethon.sync import TelegramClient
import os
from dotenv import load_dotenv
from datetime import datetime
from db.setup_db import insert_message
import re

load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
channel_username = os.getenv('CHANNEL_USERNAME')

def parse_message_content(text):
    """Parse message text to extract title and URL"""
    if not text:
        return None, None, text
    
    lines = text.strip().split('\n')
    
    # Find URL (usually at the end)
    url = None
    url_pattern = r'https?://[^\s]+'
    url_match = re.search(url_pattern, text)
    if url_match:
        url = url_match.group()
    
    # Extract title (usually the first line, excluding the URL)
    title = None
    if lines:
        first_line = lines[0].strip()
        # Remove URL from first line if present
        if url and url in first_line:
            title = first_line.replace(url, '').strip()
        else:
            title = first_line
    
    return title, url

def scrape_and_store_messages():
    with TelegramClient('session_name', api_id, api_hash) as client:
        for message in client.iter_messages(channel_username, limit=20):
            if message.text:  # Only process messages with text
                title, url = parse_message_content(message.text)
                
                # Create message object
                message_data = {
                    "telegram_id": message.id,
                    "title": title,
                    "url": url,
                    "published_at": message.date
                }
                
                try:
                    insert_message(message_data)
                except Exception as e:
                    print(f"Failed to insert message {message.id}: {e}")
                
                print("-" * 50)

if __name__ == "__main__":
    scrape_and_store_messages()
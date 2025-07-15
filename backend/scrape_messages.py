from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os
from dotenv import load_dotenv
from datetime import datetime
from db.setup_db import insert_message
import re
import asyncio

load_dotenv()

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
    # Get environment variables
    api_id = os.getenv('API_ID')
    api_hash = os.getenv('API_HASH')
    channel_username = os.getenv('CHANNEL_USERNAME')
    session_string = os.getenv('SESSION_STRING')
    
    
    # Validate environment variables
    if not api_id:
        raise ValueError("API_ID is missing or empty")
    if not api_hash:
        raise ValueError("API_HASH is missing or empty")
    if not channel_username:
        raise ValueError("CHANNEL_USERNAME is missing or empty")
    if not session_string:
        raise ValueError("SESSION_STRING is missing. Please generate it using generate_session.py")
    
    # Convert API_ID to integer
    try:
        api_id = int(api_id)
    except ValueError:
        raise ValueError(f"API_ID must be a number, got: {api_id}")
    
    try:

        # Create client with pre-generated session string
        client = TelegramClient(StringSession(session_string), api_id, api_hash)
        
        with client:

            # Verify accessing the channel
            try:
                entity = client.get_entity(channel_username)
            except Exception as e:
                print(f"Error getting channel entity: {e}")
                # Try with @ prefix if not already there
                if not channel_username.startswith('@'):
                    channel_username = '@' + channel_username
                    print(f"Trying with @ prefix: {channel_username}")
                    entity = client.get_entity(channel_username)
                    print(f"Found channel: {entity.title}")
                else:
                    raise
            
            message_count = 0
            for message in client.iter_messages(channel_username, limit=20):
                if message.text:  # Only process messages with text
                    message_count += 1
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
                        print(f"Successfully inserted message {message.id}: {title}")
                    except Exception as e:
                        print(f"Failed to insert message {message.id}: {e}")
                   
                    print("-" * 50)
    
    except Exception as e:
        print(f"Error in scrape_and_store_messages: {e}")
        print(f"Error type: {type(e).__name__}")
        raise

if __name__ == "__main__":
    scrape_and_store_messages()
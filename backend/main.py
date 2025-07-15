import asyncio
import threading
import sys
from flask import Flask, jsonify
import os

# Patch asyncio to handle missing event loops
original_get_event_loop = asyncio.get_event_loop

def patched_get_event_loop():
    try:
        return original_get_event_loop()
    except RuntimeError:
        # Create a new event loop if none exists
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

# Apply the patch
asyncio.get_event_loop = patched_get_event_loop

# Now import telethon after patching
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv
from db.setup_db import insert_message
import re

load_dotenv()

app = Flask(__name__)

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

async def scrape_messages_async():
    """Async version of scrape_and_store_messages"""
    # Get environment variables
    api_id = os.getenv('API_ID')
    api_hash = os.getenv('API_HASH')
    channel_username = os.getenv('CHANNEL_USERNAME')
    session_string = os.getenv('SESSION_STRING')
    
    print(f"API_ID: {api_id}")
    print(f"API_HASH: {api_hash[:10] + '...' if api_hash else 'None'}")
    print(f"CHANNEL_USERNAME: {channel_username}")
    print(f"SESSION_STRING: {'Present' if session_string else 'Missing'}")
    
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
        print(f"Creating async Telegram client...")
        
        # Create async client with session string
        client = TelegramClient(StringSession(session_string), api_id, api_hash)
        
        await client.start()
        print("Successfully connected to Telegram!")
        
        # Verify we can access the channel
        try:
            entity = await client.get_entity(channel_username)
            print(f"Found channel: {entity.title}")
        except Exception as e:
            print(f"Error getting channel entity: {e}")
            # Try with @ prefix if not already there
            if not channel_username.startswith('@'):
                channel_username = '@' + channel_username
                print(f"Trying with @ prefix: {channel_username}")
                entity = await client.get_entity(channel_username)
                print(f"Found channel: {entity.title}")
            else:
                raise
        
        message_count = 0
        async for message in client.iter_messages(channel_username, limit=20):
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
        
        print(f"Successfully processed {message_count} messages")
        
        await client.disconnect()
        
    except Exception as e:
        print(f"Error in scrape_messages_async: {e}")
        print(f"Error type: {type(e).__name__}")
        raise

def run_scraper_sync():
    """Synchronous wrapper that creates its own event loop"""
    def run_in_thread():
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(scrape_messages_async())
        finally:
            loop.close()
    
    # Run in a separate thread to avoid conflicts
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_in_thread)
        return future.result(timeout=300)

@app.route("/", methods=["POST"])
def run_scraper():
    try:
        run_scraper_sync()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
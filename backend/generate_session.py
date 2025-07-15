from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os
from dotenv import load_dotenv

load_dotenv()

def generate_session_string():
    """Generate a session string by authenticating locally"""
    api_id = int(os.getenv('API_ID'))
    api_hash = os.getenv('API_HASH')
    
    print("Generating session string...")
    print("You'll need to provide your phone number and verification code.")
    
    # Use StringSession
    with TelegramClient(StringSession(), api_id, api_hash) as client:
        print("Connected successfully!")
        
        # Test access to your channel
        channel_username = os.getenv('CHANNEL_USERNAME')
        try:
            entity = client.get_entity(channel_username)
            print(f"Successfully accessed channel: {entity.title}")
            
            # Get a few messages to test
            messages = client.get_messages(channel_username, limit=3)
            print(f"Successfully fetched {len(messages)} messages")
            
        except Exception as e:
            print(f"Error accessing channel: {e}")
            return None
        
        # Get the session string
        session_string = client.session.save()
        print("\n" + "="*50)
        print("SESSION STRING (save this securely):")
        print("="*50)
        print(session_string)
        print("="*50)
        print("\nAdd this to your environment variables as SESSION_STRING")
        
        return session_string

if __name__ == "__main__":
    generate_session_string()
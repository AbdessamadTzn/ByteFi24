import logging
from .connection import get_connection
from .schema.techfi24 import create_techfi24_schema, create_techfi24_index

def execute_query(query, params=None):
    """Helper function to execute queries with proper connection handling"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        if not conn:
            raise Exception("Failed to get database connection")
        
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        logging.info("Query executed successfully")
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Query execution failed: {e}")
        print(f"Connection type: {type(conn)}")
        print(f"Connection value: {conn}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def set_up_db():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Create schema and index
        create_techfi24_schema(cursor)
        logging.info("TechFi24 schema created successfully.")
        
        create_techfi24_index(cursor)
        logging.info("TechFi24 index created successfully.")
        
        # Commit the schema changes
        conn.commit()

        
    except Exception as e:
        conn.rollback()
        logging.error(f"An error occurred while setting up the database: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def insert_message(message):
    """Insert a single message into the database"""
    conn = None
    cursor = None
    try:
        # Debug: Print the message data
        print(f"DEBUG: Inserting message data: {message}")
        
        conn = get_connection()
        if not conn:
            raise Exception("Failed to get database connection")
            
        cursor = conn.cursor()
        
        query = """
        INSERT INTO techfi24 (telegram_id, title, url, published_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (telegram_id) DO NOTHING;
        """
        params = (
            message["telegram_id"],
            message.get("title"),
            message.get("url"),
            message["published_at"],
        )
        
        # Debug: Print the params
        print(f"DEBUG: Query params: {params}")
        
        cursor.execute(query, params)
        conn.commit()
        logging.info(f"Message {message['telegram_id']} inserted successfully")
        
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Query failed {e}")
        print(f"ERROR DETAILS: {e}")
        print(f"Message data: {message}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
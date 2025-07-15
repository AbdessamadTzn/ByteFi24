def create_techfi24_schema(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS techfi24(
                   id SERIAL PRIMARY KEY,
                   telegram_id BIGINT UNIQUE,
                   title TEXT,
                   url TEXT,
                   published_at TIMESTAMP,
                   scraped_at TIMESTAMP DEFAULT NOW()
                   );
                   """)

def create_techfi24_index(cursor):
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_techfi24_published_at ON techfi24(published_at DESC);
        """)
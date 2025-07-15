from flask import Flask, render_template, request, jsonify, redirect, url_for
from db.setup_db import get_connection
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_articles(page=1, per_page=20, search_query=None):
    """Get articles from database with pagination and search"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        if not conn:
            raise Exception("Failed to get database connection")
        
        cursor = conn.cursor()
        
        # Calculate offset for pagination
        offset = (page - 1) * per_page
        
        # Base query
        base_query = """
        SELECT telegram_id, title, url, published_at
        FROM techfi24
        """
        
        count_query = "SELECT COUNT(*) FROM techfi24"
        
        # Add search filter if provided
        if search_query:
            search_filter = " WHERE title ILIKE %s OR url ILIKE %s"
            base_query += search_filter
            count_query += search_filter
            search_params = (f'%{search_query}%', f'%{search_query}%')
        else:
            search_params = None
        
        # Add ordering and pagination
        base_query += " ORDER BY published_at DESC LIMIT %s OFFSET %s"
        
        # Get total count
        if search_params:
            cursor.execute(count_query, search_params)
        else:
            cursor.execute(count_query)
        total_count = cursor.fetchone()[0]
        
        # Get articles
        if search_params:
            cursor.execute(base_query, search_params + (per_page, offset))
        else:
            cursor.execute(base_query, (per_page, offset))
        
        articles = cursor.fetchall()
        
        # Convert to dictionary format
        articles_list = []
        for article in articles:
            articles_list.append({
                'telegram_id': article[0],
                'title': article[1] or 'No Title',
                'url': article[2],
                'published_at': article[3]
            })
        
        return articles_list, total_count
        
    except Exception as e:
        logging.error(f"Error fetching articles: {e}")
        return [], 0
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/')
def index():
    """Main page showing articles"""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    per_page = 20
    
    articles, total_count = get_articles(page, per_page, search_query if search_query else None)
    
    # Calculate pagination info
    total_pages = (total_count + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return render_template('index.html', 
                         articles=articles,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         search_query=search_query,
                         total_count=total_count)

@app.route('/api/articles')
def api_articles():
    """API endpoint for articles"""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    per_page = request.args.get('per_page', 20, type=int)
    
    articles, total_count = get_articles(page, per_page, search_query if search_query else None)
    
    return jsonify({
        'articles': articles,
        'total_count': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_count + per_page - 1) // per_page
    })

@app.route('/scrape', methods=['POST'])
def trigger_scrape():
    """Trigger the scraping process"""
    try:
        # Import and run your existing scraper
        from scrape_messages import scrape_and_store_messages
        scrape_and_store_messages()
        return jsonify({"status": "success", "message": "Scraping completed successfully"})
    except Exception as e:
        logging.error(f"Scraping failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
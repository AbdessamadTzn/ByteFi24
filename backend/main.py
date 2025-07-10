# main.py
from flask import Flask, jsonify
from scrape_messages import scrape_and_store_messages

app = Flask(__name__)

@app.route("/", methods=["POST"])
def run_scraper():
    try:
        scrape_and_store_messages()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

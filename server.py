from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS (Cross-Origin Resource Sharing)
from crawler.parser import fetch_articles_threads  # Import the function to fetch articles

app = Flask(__name__)  # Create a Flask application instance
CORS(app)  # Enable CORS for the app

@app.route('/')
def get_news():
    """Endpoint that returns a welcome message for the news API"""
    return jsonify({"message": "This is the news API"})

@app.route('/category/<category_name>')
def category(category_name):
    """Returns news data for a specific category (no HTML rendering)"""
    news_data = fetch_articles_threads()  # Fetch the articles
    filtered_news = [news for news in news_data if news['category'] == category_name]  # Filter news by category
    return jsonify({"category": category_name, "news": filtered_news})  # Return filtered news in JSON format

@app.route('/search')
def search():
    """Returns search results in JSON format"""
    query = request.args.get('q', '').lower()  # Get search query from URL parameters
    news_data = fetch_articles_threads()  # Fetch the articles
    search_results = [news for news in news_data if query in news['title'].lower()]  # Filter news by search query
    return jsonify({"query": query, "results": search_results})  # Return search results in JSON format

if __name__ == '__main__':
    app.run(debug=True,use_reloader=False)  # Run the app in debug mode

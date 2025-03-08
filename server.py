from flask import Flask, jsonify, request  # Import Flask framework components
from flask_cors import CORS  # Import CORS (Cross-Origin Resource Sharing) to allow requests from different origins
from crawler.parser import fetch_articles_threads  # Import the function to fetch articles
import os
from dotenv import load_dotenv  # Import dotenv to load environment variables from a .env file

app = Flask(__name__)  # Create a Flask application instance
CORS(app)  # Enable CORS for handling cross-origin requests

# Load environment variables from the .env file
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Set the secret key from environment variables


@app.route('/')
def get_news():
    """API root endpoint returning a welcome message."""
    return jsonify({"message": "This is the news API"})


@app.route('/category/<category_name>')
def category(category_name):
    """
    Endpoint to return news articles filtered by category.

    Args:
        category_name (str): The category name used for filtering news articles.

    Returns:
        JSON: A dictionary containing the category name and the filtered list of news articles.
    """
    news_data = fetch_articles_threads()  # Fetch all news articles
    filtered_news = [news for news in news_data if news['category'] == category_name]  # Filter articles by category
    return jsonify({"category": category_name, "news": filtered_news})  # Return filtered articles in JSON format


@app.route('/search')
def search():
    """
    Endpoint to return search results based on a query.

    Query Parameters:
        q (str): The search keyword to match article titles.

    Returns:
        JSON: A dictionary containing the search query and matching news articles.
    """
    query = request.args.get('q', '').lower()  # Retrieve the search query from URL parameters and convert to lowercase
    news_data = fetch_articles_threads()  # Fetch all news articles
    search_results = [news for news in news_data if query in news['title'].lower()]  # Filter articles by search query
    return jsonify({"query": query, "results": search_results})  # Return search results in JSON format


if __name__ == '__main__':
    app.run(debug=True,
            use_reloader=False)  # Run the Flask app in debug mode (without reloader to prevent duplicate execution)

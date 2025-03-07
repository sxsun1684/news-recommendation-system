from flask import Flask, jsonify, request
from crawler.parser import fetch_articles_threads

app = Flask(__name__)

@app.route('/')
def get_news():
    return jsonify({"message": "This is the news API"})

@app.route('/category/<category_name>')
def category(category_name):
    """返回某个分类的新闻数据（不再渲染 HTML）"""
    news_data = fetch_articles_threads()
    filtered_news = [news for news in news_data if news['category'] == category_name]
    return jsonify({"category": category_name, "news": filtered_news})

@app.route('/search')
def search():
    """返回搜索结果 JSON"""
    query = request.args.get('q', '').lower()
    news_data = fetch_articles_threads()
    search_results = [news for news in news_data if query in news['title'].lower()]
    return jsonify({"query": query, "results": search_results})

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)


@app.route('/')
def get_news():
    return jsonify({"message": "This is the news API"})

# @app.route('/business')
@app.route('/category/<category_name>')
def category(category_name):
    """显示某一分类的新闻"""
    filtered_news = [news for news in news_data if news['category'] == category_name]
    return render_template('index.html', news=filtered_news, category=category_name)

@app.route('/search')
def search():
    """搜索功能"""
    query = request.args.get('q', '').lower()
    # search_results = [news for news in news_data if query in news['title'].lower()]
    # return render_template('search.html', results=search_results, query=query)

if __name__ == '__main__':
    app.run(debug=True)

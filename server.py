from flask import Flask, render_template, jsonify

app = Flask(__name__)


@app.route('/')
def get_news():
    return jsonify({"message": "This is the news API"})

# @app.route('/business')

if __name__ == '__main__':
    app.run(debug=True)

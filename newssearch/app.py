from flask import Flask
from flask.json import jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)

mongo_user = "<user>"
mongo_password = "<password>"
mongo_db_name = "<db name>"
mongo_connect_uri = "<connect uri>"
app.config["MONGO_URI"] = mongo_connect_uri.format(username=mongo_user, password=mongo_password, database=mongo_db_name)
mongo = PyMongo(app)


@app.route("/")
def fetch_all():
    news_article = mongo.db.bbc_news.find(filter={}, projection={'_id': False})
    return_data = list(news_article)
    return jsonify(return_data)


@app.route("/searchfield/<field>/<path:keyword>")
def search_field(field, keyword):
    print({field: keyword})
    news_article = mongo.db.bbc_news.find(filter={field: keyword}, projection={'_id': False})
    return_data = list(news_article)
    return jsonify(return_data)


@app.route("/searchtext/keywords/<path:keyword>")
def search_text(keyword):
    print(keyword)
    news_article = mongo.db.bbc_news.find(filter={"$text": {"$search": keyword}}, projection={'_id': False})
    return_data = list(news_article)
    return jsonify(return_data)


@app.route("/searchtext/phrase/<path:phrase>")
def search_phrase(phrase):
    keyword = "\"{}\"".format(phrase)
    print({"$text": {"$search": keyword}})
    news_article = mongo.db.bbc_news.find(filter={"$text": {"$search": keyword}}, projection={'_id': False})
    return_data = list(news_article)
    return jsonify(return_data)


@app.route("/searcharticle/publish_date/<comparison_op>/<path:date>")
def search_date(comparison_op, date):
    comparison_tuple = ("gt", "gte", "lt", "lte")
    if comparison_op in comparison_tuple:
        print({"publish_time": {"$" + comparison_op: date}})
        news_article = mongo.db.bbc_news.find(filter={"publish_time": {"$" + comparison_op: date}}, projection={'_id': False})
        return_data = list(news_article)
        return jsonify(return_data)
    else:
        return {"Error": "Not a valid operator"}


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

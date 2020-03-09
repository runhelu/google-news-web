import os
import flask
from flask import Flask, jsonify
from newsapi import NewsApiClient
import json
import re

app = Flask(__name__)
newsapi = NewsApiClient(api_key='ce142f81906948979b2f05ecf6e12c31')
top30words = dict()
stopWords = set()
with open("stopwords_en.txt", "r") as f:
    for line in f.readlines():
        word = line.strip()
        stopWords.add(word)
f.close()

@app.route('/getSources', methods = ["GET", "POST"])
def getSources():
    if flask.request.method == "GET" or flask.request.method == "POST":
        category = flask.request.json["category"]
        category = category.lower()
        if(category == "all"):
            sources = newsapi.get_sources(language = "en", country = "us")
        else:
            sources = newsapi.get_sources(category = category, language = "en", country = "us")
        response = jsonify(sources)
        return response

@app.route('/renderCa', methods = ["GET"])
def renderCa():
    dict2 = {}
    try:
        dict2 = newsapi.get_top_headlines(language='en', page = 1)
    except Exception as e:
        return jsonify(str(e))
    response = {}
    response["articles"] = []
    for article in dict2["articles"]:
        if article["author"] and article["description"] and article["title"] and article["url"] and article["source"] and article["urlToImage"] and article["publishedAt"]:
            if len(response["articles"]) < 5:
                response["articles"].append(article)
            else:
                break
    response = jsonify(response)
    return response

@app.route('/searchNews', methods = ["GET", "POST"])
def searchNews():
    if flask.request.method == "GET" or flask.request.method == "POST":
        data = flask.request.json
        keyword = data["keyWord"]
        from_date = data["from_date"]
        to_date = data["to_date"]
        source = data["source"]
        everything = {}
        if(source != "all"):
            try:
                everything = newsapi.get_everything(q=keyword, sources=source, from_param=from_date, to=to_date, language='en', page_size=30,sort_by='publishedAt', page=1)
            except Exception as e:
                
                return jsonify(str(e))
        else:
            try:
                everything = newsapi.get_everything(q=keyword, from_param=from_date, to=to_date, language='en', page_size=30,sort_by='publishedAt', page=1)
            except Exception as e:
                
                return jsonify(str(e))

        response = {}
        response["articles"]=[]
        for article in everything["articles"]:
            if article["author"] and article["description"] and article["title"] and article["url"] and article["source"] and article["urlToImage"] and article["publishedAt"]:
                response["articles"].append(article)
        response = jsonify(response)
        return response    

@app.route('/indexRender', methods=["GET"])
def indexRender():
    top_headlines = {}
    try:
        top_headlines = newsapi.get_top_headlines(language='en', page = 1)
    except Exception as e:
        return jsonify(str(e))
    response = {}
    punctuation = '!,;:?".'
    response["articles"] = []
    for article in top_headlines["articles"]:
        if article["author"] and article["description"] and article["title"] and article["url"] and article["source"] and article["urlToImage"] and article["publishedAt"]:
            if len(response["articles"]) < 5:
                response["articles"].append(article)
                title = article["title"]
                for word in title.strip().split(" "):
                    word = word.lower()
                    word = re.sub(r'[{}]+'.format(punctuation),'', word)
                    if word not in stopWords and word.isalpha():
                        if word not in top30words:
                            top30words[word] = 1
                        else:
                            top30words[word] += 1
            else:
                break
    cnn_headlines = newsapi.get_top_headlines(language='en', sources = 'cnn', page = 1)
    response["cnn"] = []
    for article in cnn_headlines["articles"]:
        if article["author"] and article["description"] and article["title"] and article["url"] and article["source"] and article["urlToImage"] and article["publishedAt"]:
            if len(response["cnn"]) < 4:
                response["cnn"].append(article)
                title = article["title"]
                for word in title.strip().split(" "):
                    word = word.lower()
                    word = re.sub(r'[{}]+'.format(punctuation),'', word)
                    if word not in stopWords and word.isalpha():
                        if word not in top30words:
                            top30words[word] = 1
                        else:
                            top30words[word] += 1
            else:
                break
    fox_headlines = newsapi.get_top_headlines(language='en', sources = 'fox-news', page = 1)
    response["fox-news"] = []
    for article in fox_headlines["articles"]:
        if article["author"] and article["description"] and article["title"] and article["url"] and article["source"] and article["urlToImage"] and article["publishedAt"]:
            if len(response["fox-news"]) < 4:
                response["fox-news"].append(article)
                title = article["title"]
                for word in title.strip().split(" "):
                    word = word.lower()
                    word = re.sub(r'[{}]+'.format(punctuation),'', word)
                    if word not in stopWords and word.isalpha():
                        if word not in top30words:
                            top30words[word] = 1
                        else:
                            top30words[word] += 1
            else:
                break
    
    words = sorted(top30words.items(), key=lambda x:x[1], reverse=True)
    response["words"] = []
    for i in range(0, 30):
        key = words[i][0]
        response["words"].append({"word": key, "size": 30-i})
    response = jsonify(response)
    
    return response

@app.route('/index', methods=["GET"])
@app.route('/', methods=["GET"])
def hello():
    """Return a friendly HTTP greeting."""
    
    return app.send_static_file("index.html")
    
@app.after_request
def after_request(resp):
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["Pragma"] = "no-cache"
    return resp

if __name__ == '__main__':
    #app.run(host='localhost', port=8080, debug=True)
    app.run(host='0.0.0.0', port=8080, debug=True)

# coding: utf-8
from flask import Flask, jsonify, render_template, request
from flask import render_template
from pymongo import MongoClient
import json
from bson import json_util
from bson.json_util import dumps
import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

api_key = '1IdtVsA6OBmWwL5yfotkiLqtK'
api_secret = 'zhpd4FlxfbnXYOZjAMlPSL1pnrZbP67z9FPQiEKB8jrbMYG8nk'
access_token = '1373799294-IqqfE80zf11QqxyFYkQYQzqgHrX24RUj3j0vBzw'
access_token_secret = 'IoMM0KcnC2l5L29weGcrgN2yvqnPJXszuIbpYvxZ7fECJ'

class TweetListener(StreamListener):
    # A listener handles tweets are the received from the stream.
    #This is a basic listener that just prints received tweets to standard output

    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status

auth = tweepy.OAuthHandler(api_key, api_secret) 
auth.set_access_token(access_token, access_token_secret) 
api = tweepy.API(auth)

app = Flask(__name__)


MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'TwitterData'
COLLECTION_NAME = 'Tweets'
FIELDS1 = {'text': True,'created_at': True,'origin': True,'rebloggedBy': True,'i': True, '_id': False}
FIELDS2 = {'name': True,'group': True, '_id': False, 'amountoftweets': True, 'position': True}
FIELDS3 = {'source': True,'target': True, 'value': True, '_id': True}
connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
collection = connection[DBS_NAME]["LessTweets"]
tweets = [x for x in collection.find()]

@app.route('/_getuserdeets')
def add_numbers():
    a = request.args.get('a')

    twitterStream = Stream(auth,TweetListener())
    user = api.get_user(a)
    name = user.name
    handle = user.screen_name
    handlestring = "Handle: "
    desc = user.description
    url = user.url
    createdDate = user.created_at
    location = user.location
    return jsonify(name = name, handle = handle, desc = desc, url = url, createdDate = createdDate, location = location)

@app.route("/")
def index():
	
	return render_template('index.html', tweets=tweets)

@app.errorhandler(404)
def parameter(e):
	return render_template('index.html', tweets=tweets), 404


@app.route("/TwitterData/LessTweets")
def twitterdata_lesstweets():
	connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
	collection = connection[DBS_NAME]["LessTweets"]
	tweets = collection.find(projection=FIELDS1)
	json_tweets = []
	for tweet in tweets:
		json_tweets.append(tweet)
	json_tweets = json.dumps(json_tweets, default=json_util.default)
	connection.close()
	return json_tweets

@app.route("/TwitterData/nodes")
def twitterdata_nodes():
	connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
	collection = connection[DBS_NAME]["nodes"]
	nodes = collection.find(projection=FIELDS2)
	json_nodes = []
	for node in nodes:
		json_nodes.append(node)
	json_nodes = json.dumps(json_nodes, default=json_util.default)
	connection.close()
	return json_nodes

@app.route("/TwitterData/links")
def twitterdata_links():
	connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
	collection = connection[DBS_NAME]["links"]
	links = collection.find(projection=FIELDS3)
	json_links = []
	for link in links:
		json_links.append(link)
	json_links = json.dumps(json_links, default=json_util.default)
	connection.close()
	return json_links






if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True, threaded=True)
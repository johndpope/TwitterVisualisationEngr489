import pymongo
from pymongo import MongoClient
import tweepy
import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import time

api_key = '1IdtVsA6OBmWwL5yfotkiLqtK'
api_secret = 'zhpd4FlxfbnXYOZjAMlPSL1pnrZbP67z9FPQiEKB8jrbMYG8nk'
access_token = '1373799294-IqqfE80zf11QqxyFYkQYQzqgHrX24RUj3j0vBzw'
access_token_secret = 'IoMM0KcnC2l5L29weGcrgN2yvqnPJXszuIbpYvxZ7fECJ'

auth = tweepy.OAuthHandler(api_key, api_secret) 
auth.set_access_token(access_token, access_token_secret) 
# The api object gives you access to all of the http calls that Twitter accepts 
api = tweepy.API(auth)

client = MongoClient()
client = MongoClient('localhost', 27017)
db = client['TwitterData']
Tweetscollection = db['TweetsAndHashtags']

class CustomStreamListener(tweepy.StreamListener):
	def __init__(self, api):
		self.api = api
		super(tweepy.StreamListener, self).__init__()

		self.db = pymongo.MongoClient().TwitterData

	def on_data(self, tweet):
		self.db.Tweets.insert(json.loads(tweet))

	def on_error(self, status_code):
		return True # Don't kill the stream

	def on_timeout(self):
		return True # Don't kill the stream


sapi = tweepy.streaming.Stream(auth, CustomStreamListener(api))
sapi.filter(track=['paralympics'])

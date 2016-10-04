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
Followeescollection = db['TwitterUsers']
Followerscollection = db['UsersAndFollowers']

user=api.get_user('jarpad')
key={'_id':user.screen_name}
data={'handle':user.screen_name,'name':user.name}
Followeescollection.update(key, data, upsert = True)
def fib(n, user):
	if n>0:
		time.sleep(15)
		users = api.followers(user.screen_name)
		i = 0
		for follower in users:
			i=i+1
			key={'_id':follower.screen_name}
			data={'handle':follower.screen_name,'name':follower.name}
			Followeescollection.update(key, data, upsert = True)
			nameinteration = user.screen_name + "." + str(i)
			key2={'_id':nameinteration}
			data2={'followeeHandle':user.screen_name, 'followeeName':user.name, 'followerHandle':follower.screen_name,'followerName':follower.name}
			Followerscollection.update(key2, data2, upsert = True)
			fib(n-1,follower)
n=2
fib(n,user)

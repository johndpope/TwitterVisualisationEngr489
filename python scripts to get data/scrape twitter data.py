import pymongo
from pymongo import MongoClient
import tweepy
import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import time
import random
from random import randint

api_key = '1IdtVsA6OBmWwL5yfotkiLqtK'
api_secret = 'zhpd4FlxfbnXYOZjAMlPSL1pnrZbP67z9FPQiEKB8jrbMYG8nk'
access_token = '1373799294-IqqfE80zf11QqxyFYkQYQzqgHrX24RUj3j0vBzw'
access_token_secret = 'IoMM0KcnC2l5L29weGcrgN2yvqnPJXszuIbpYvxZ7fECJ'

auth = tweepy.OAuthHandler(api_key, api_secret) 
auth.set_access_token(access_token, access_token_secret) 
# The api object gives you access to all of the http calls that Twitter accepts 
api = tweepy.API(auth)
#api = tweepy.API([auth], wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

client = MongoClient()
client = MongoClient('localhost', 27017)
db = client['TwitterData']
#Collection1 = db['tweets']
Collections2 = db['nodes']
Collections3 = db['links']
FolloweePosition = 0;

#list of user screen names who have made tweets stored in Tweets collection
tweets = db.LessTweets.find();
position = 0
print("at the start of code position is: "+ str(position))
#go through all the users who have made tweets stored in Tweets
for tweet in tweets:
	handleFromTweetsCollection = tweet['origin']
	#print(handleFromTweetsCollection + " is currently being looked at")

	#get a list of handles currently stored in nodes collection 
	nodes = db.nodes.find();
	listofnodes =  []
	
	#make a list of strings of the handles in the nodes collection
	for node in nodes:
		nameinnodes = node['name']
		listofnodes.append(nameinnodes)

	#for name in listofnodes:
		#print("    " + name + "is within nodes collection")
	alreadyTweeted=False
	#check if handle from tweets collection is in the list of handles saved in nodes
	if(handleFromTweetsCollection in listofnodes):
		print("found same handle in tweets and nodes")
		alreadyTweeted = True
		#increment the amount of tweets under that user
		db.nodes.update({'name': handleFromTweetsCollection}, {'$inc': {'amountoftweets': 1}})

	if not alreadyTweeted:
		#add tweeter to list of handles in nodes collection
		key = {'_id':handleFromTweetsCollection}
		data={'name':handleFromTweetsCollection,'group':1, 'amountoftweets':1, 'position':position}
		FolloweePosition = position;
		print(handleFromTweetsCollection+" has just been added to nodes collection. Its position is: "+ str(position))
		position = position + 1;
		print("position is now"+ str(position))
		Collections2.update(key, data, upsert = True)
		randomAmount = randint(1,30)
		#get a list of the tweeters followers
		followers = api.followers(handleFromTweetsCollection)
		j = 0
		while j < min(randomAmount,len(followers)):
			alreadyAdded = False
			follower = followers[j].screen_name
			#check that follower is not already in the nodes collection
			if(follower in listofnodes):
				alreadyAdded = True
				#add link from tweeter to follower
				followerPosition = ""
				cur =  db.nodes.find({'name': follower}, {'position':True, '_id': False})
				for doc in cur:
					split1 = str(doc).split(":")
					split2 = split1[1].split()
					split3 = split2[0].split("}")
					followerPosition = split3[0]
				key3={'_id':handleFromTweetsCollection+follower}
				data3 = {'source': FolloweePosition, 'target':followerPosition, 'value':1}
				Collections3.update(key3, data3, upsert = True)
				print(handleFromTweetsCollection + " to " + follower + "if follower already added")
			if not alreadyAdded:
				#add follower as a node in nodes collection
				key ={'_id':follower}
				data={'name':follower,'group':1, 'amountoftweets':0, 'position':position}
				Collections2.update(key, data, upsert = True)
				print(follower + "has just been added to nodes collection. Its position is: "+ str(position))
				#add link from tweeter to follower
				key2 = {'_id':handleFromTweetsCollection+follower}
				data2 = {'source':FolloweePosition, 'target':position, 'value':1}
				Collections3.update(key2, data2, upsert = True)
				print("position is now "+ str(position))
				print(handleFromTweetsCollection + " to " + follower+ "if follower not already added")
				position = position + 1
			j = j+1



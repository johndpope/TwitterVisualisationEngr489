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
api = tweepy.API([auth], wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

client = MongoClient()
client = MongoClient('localhost', 27017)
db = client['TwitterData']
#Collection1 = db['tweets']
Collections2 = db['nodes']
Collections3 = db['links']
FolloweePosition = 0;



cursor = db.LessTweets.find();
i = 0;
#go through all users that have tweeted
for tweet in cursor:
	tweeter = tweet['origin']
	cursor2 = db.nodes.find();
	listofnodes =  []
	alreadyTweeted = False
	for document in cursor2:
		nameinnodes = document['name']
		listofnodes.append(nameinnodes)
		if(tweeter in listofnodes):
			print("here")
			alreadyTweeted = True
			db.nodes.update({'name': tweeter}, {'$inc': {'amountoftweets': 1}})

			#only do this if not already in nodes collection
			if not alreadyTweeted:
				print(tweeter + " is not already in collection")
				key ={'_id':tweeter}
				data={'name':tweeter,'group':1, 'amountoftweets':1, 'position':i}
				FolloweePosition = i;
				#increase position for next node to be added
				i = i+1;
				#add this user to nodes collection
				Collections2.update(key, data, upsert = True)
				#random number to get a random amount of followers of this user
				randomAmount = randint(1,30)
				#get a list of followers of the tweeter
				followers = api.followers(api.get_user(tweeter).screen_name)

				j = 1
				#only do for the amount of randomly selected followers
				while j < randomAmount:
					alreadyAdded = False
					#get handle of follower
					follower = followers[j].screen_name
					#go through all users already saved in nodes collection
					for document in cursor2:
						nameinnodes = document['name']
						#if name in nodes matches the name of follower
						if follower == nameinnodes:
							print("here")
							alreadyAdded = True
							#get position of follower in nodes collection
							followerPosition = ""
							cur =  db.nodes.find({'name': follower}, {'position':True, '_id': False})
							for doc in cur:
								split1 = str(doc).split(":")
								split2 = split1[1].split()
								split3 = split2[0].split("}")
								followerPosition = split3[0]
							#add followee to follower link in collection
							#key3 = {'_id':tweeter}
							data3 = {'source': FolloweePosition, 'target':followerPosition, 'value':1}
							Collections3.insert(data3)

					#if follower not already in collection
					if not alreadyAdded:
						#add the follower to collection
						key ={'_id':follower}
						data={'name':follower,'group':1, 'amountoftweets':0, 'position':i}
						#add this user to nodes collection
						Collections2.update(key, data, upsert = True)
						#add followee to follower link in collection
						#key2 = {'_id':tweeter}
						data2 = {'source':FolloweePosition, 'target':i, 'value':1}
						Collections3.insert(data2)
						#increase position for next node to be added
						i = i+1;
						j = j+1


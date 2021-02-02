import tweepy
import json

## set up auth
with open('auth.json') as authJSONFile:
    authKeys = json.load(authJSONFile)

auth = tweepy.OAuthHandler(authKeys['consumer_key'],authKeys['consumer_secret'])
auth.set_access_token(authKeys['access_token'],authKeys['access_secret'])

api = tweepy.API(auth)

authedUser = api.me().screen_name
print(authedUser)

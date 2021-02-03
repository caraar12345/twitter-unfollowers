import tweepy
import json
from google.cloud import bigquery
import os
import datetime

## location of BigQuery service account creds
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/aaroncarson/src/github.com/caraar12345/twitter-unfollowers/googleauth.json'
## sets up BQ access
bqClient = bigquery.Client()
bqFollowersTable = "twitter_analysis.followers"


## set up Twitter auth
with open('auth.json') as authJSONFile:
    authKeys = json.load(authJSONFile)

auth = tweepy.OAuthHandler(authKeys['consumer_key'],authKeys['consumer_secret'])
auth.set_access_token(authKeys['access_token'],authKeys['access_secret'])
api = tweepy.API(auth)
authedUser = api.me().screen_name
#print(authedUser)

currentFollowerList = api.followers_ids(authedUser)

newUnfollowers = []
newFollowers = []

currentFollowers = [{
        "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "account_ids": str(currentFollowerList),
        "length": len(currentFollowerList),
        "unfollowers": str(newUnfollowers),
        "new_followers": str(newFollowers)
        }]

#print(currentFollowers)

bqJSON = [currentFollowers]

bqClient.insert_rows_json(bqFollowersTable, currentFollowers)

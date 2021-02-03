import tweepy
import json
from google.cloud import bigquery
import os
import datetime
import requests

## location of BigQuery service account creds
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/aaroncarson/src/github.com/caraar12345/twitter-unfollowers/googleauth.json'
## sets up BQ access
bqClient = bigquery.Client()

bqFollowersTable = "twitter_analysis.followers"
bqUnfollowersTable = "twitter_analysis.unfollowers"
bqNewFollowersTable = "twitter_analysis.new_followers"

## set up Twitter auth
with open('auth.json') as authJSONFile:
    authKeys = json.load(authJSONFile)

auth = tweepy.OAuthHandler(authKeys['consumer_key'],authKeys['consumer_secret'])
auth.set_access_token(authKeys['access_token'],authKeys['access_secret'])
api = tweepy.API(auth)
authedUser = api.me().screen_name
#print(authedUser)

currentFollowerList = api.followers_ids(authedUser)



## retrieve last row

bqPrevFolQuery = """SELECT account_ids as previousFollowers
                    FROM `aaroncarsondata.twitter_analysis.followers`
                    ORDER BY timestamp DESC
                    LIMIT 1"""

bqPrevFolQueryJob = bqClient.query(bqPrevFolQuery)

previousFollowerList = []

for row in bqPrevFolQueryJob:
    temp = row[0].split(",")
    for usrID in temp:
        previousFollowerList.append(int(usrID.strip('[ ]')))

newFollowers = set(currentFollowerList) - set(previousFollowerList)
newUnfollowers = set(previousFollowerList) - set(currentFollowerList)

if str(newFollowers) == "set()":
    newFollowers = []
if str(newUnfollowers) == "set()":
    newUnfollowers = []

currentFollowers = [{
        "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "account_ids": str(currentFollowerList),
        "length": len(currentFollowerList),
        "unfollowers": str(newUnfollowers),
        "new_followers": str(newFollowers)
        }]

#print(currentFollowers,"\n\n")
#print(previousFollowerList)

## upload the current follower list
bqJSON = [currentFollowers]
bqClient.insert_rows_json(bqFollowersTable, currentFollowers)

## convert new (un)followers to @username

def lookupUser(userIDList,bqTable):
    lookupData = api.lookup_users(user_ids=list(userIDList))
    for user in lookupData:
        userDetails = [{
            "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user.id,
            "user_name": user.name,
            "user_screen_name": user.screen_name
            }]
        bqClient.insert_rows_json(bqTable,userDetails)
        if bqTable == bqUnfollowersTable:
            payload = {'value1':user.screen_name,'value2':user.profile_image_url_https}
            webhook = requests.post(authKeys['ifttt_webhook'], data=payload) 

if newFollowers != []:
    lookupUser(newFollowers,bqNewFollowersTable)

if newUnfollowers != []:
    lookupUser(newUnfollowers,bqUnfollowersTable)

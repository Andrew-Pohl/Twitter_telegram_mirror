from twitter_scraper import get_tweets
import os.path
import configparser
import requests

debugPrints = False

config = configparser.ConfigParser()
config.optionxform=str
config.read("settings.ini")

teleBotSettings = dict(config.items('BOT'))

#don't send tweets on the first run
publish = False

#if we have sent tweets before check where we got to
if os.path.exists('lastPublished.txt'):
    f = open("lastPublished.txt", "r")
    tweetID = (f.read())
    publish = True

#load all recent tweets into a list
tweets = []
for tweet in get_tweets(teleBotSettings["TWITTER_HANDLE"], pages=1):
    tweets.append(tweet)

#grab the ID of the latest tweet
latestID = tweets[0]['tweetId']

if publish:
    #loop across the tweets until we are upto date
    for tweet in tweets:
        if tweet['tweetId'] == tweetID:
            break

        isRetweet = tweet['isRetweet']
        if not (teleBotSettings["ALLOW_RETWEETS"] != 'yes' and isRetweet):
            tweetOrRetweet = "Tweet"
            if isRetweet:
                tweetOrRetweet = "Retweet"

            messageToSendToBot="New " + tweetOrRetweet + " from " + teleBotSettings["TWITTER_HANDLE"] +" " + str(tweet['time']) + "%0A" \
                               "Tweet URL: www.twitter.com" + tweet['tweetUrl'] + "%0A" \
                               + tweet['text']

            botMessage = 'https://api.telegram.org/bot' + teleBotSettings["BOT_KEY"] + '/sendMessage?chat_id=' + teleBotSettings["CHAT_ID"] + '&text=' + messageToSendToBot

            response = requests.get(botMessage)
            jsonResponse = response.json()

            if jsonResponse['ok'] != True:
                print("FAILED TO SEND TWEETID = " + tweet['tweetId'])

            if(debugPrints):
                print("Tweet ID: " + tweet['tweetId'] + "\nbody: " + tweet['text'] + "\ntweetURL: www.twitter.com" + tweet['tweetUrl'] + '\n')
else:
    messageToSendToBot = "Hello I'm the twitter bot for www.twitter.com/" + teleBotSettings["TWITTER_HANDLE"] + " I will keep this channel updated with all their latest tweets"
    botMessage = 'https://api.telegram.org/bot' + teleBotSettings["BOT_KEY"] + '/sendMessage?chat_id=' + teleBotSettings["CHAT_ID"] + '&text=' + messageToSendToBot
    response = requests.get(botMessage)
    jsonResponse = response.json()

    if jsonResponse['ok'] != True:
        print("FAILED TO WELCOME MESSAGE")

#update the file with the new postion
f = open("lastPublished.txt", "w")
f.write(latestID)
f.close()
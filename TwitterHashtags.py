from datetime import date
from unicodedata import normalize
import tweetpony

class TwitterHashtags(object):
    api = None

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.api = tweetpony.API(consumer_key, consumer_secret, access_token, access_token_secret)

    def get_hashtags (self, screen_name, hashtags_filter = [], max_tweets_count = 500, tweets_by_request = 200):
        hashtags = {}
        tweets_count = 0
        last_tweet_date = None
        max_id = None
        hashtags_filter = [self.clean_string(hashtag) for hashtag in hashtags_filter]
        user = self.get_user(screen_name)

        while tweets_count < max_tweets_count:
            tweets_to_request = self.get_nb_tweets_to_request(tweets_count, tweets_by_request, max_tweets_count)
            tweets = self.get_tweets(screen_name, tweets_to_request, max_id)
            if not tweets:
                break
            self.add_tweets_hashtags(tweets, hashtags, hashtags_filter)
            tweets_count += len(tweets)
            max_id = self.get_max_id(tweets)
            last_tweet_date = self.get_last_tweet_date(tweets)

        return {
            'screen_name' : screen_name,
            'followers_count' : user['followers_count'],
            'tweets_count' : user['statuses_count'],
            'current_date' : date.today(),
            'nb_tweets_read' : tweets_count,
            'oldest_tweet_read' : last_tweet_date,
            'hashtags' : hashtags
        }

    def get_user (self, screen_name):
        return self.api.get_user(screen_name = screen_name)

    def get_nb_tweets_to_request (self, tweets_count, tweets_by_request, max_tweets_count):
        if tweets_count + tweets_by_request > max_tweets_count:
          return max_tweets_count - tweets_count
        else :
          return tweets_by_request;

    def get_tweets (self, screen_name, count = None, max_id = None):
        return self.api.user_timeline(screen_name = screen_name, max_id = max_id,
        count = count, trim_user = True, exclude_replies = False,
        contributor_details = False)

    def add_tweets_hashtags (self, tweets, hashtags, hashtags_filter = []):
        for tweet in tweets:
            tweet_hashtags = tweet['entities']['hashtags']
            if not tweet_hashtags:
                continue
            for tweet_hashtag in tweet_hashtags:
                text = tweet_hashtag['text']
                clean_text = self.clean_string(text)
                if hashtags_filter and clean_text not in hashtags_filter:
                    continue
                if text not in hashtags:
                    hashtags[text] = 0
                hashtags[text] += 1

    def get_max_id (self, tweets):
        last_id = int(tweets[-1]['id'])
        return last_id - 1

    def get_last_tweet_date (self, tweets):
        return tweets[-1]['created_at']

    def clean_string (self, text):
        if isinstance(text, str):
            text = text.decode('utf-8')
        text = text.lower()
        return normalize('NFKD', text).encode('ASCII', 'ignore')

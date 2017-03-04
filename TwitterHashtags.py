"""
A Pyton tool based on TweetPony used to retrieve, filter and count
the hashtags used by a Twitter user.

license: MIT
author: Thibault Goehringer
email: tgoehringer@gmail.com
"""

from datetime import date
from unicodedata import normalize
import tweetpony

class TwitterHashtags(object):
    """ The TwitterHashtags class, where the magic happens. """

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.api = tweetpony.API(consumer_key, consumer_secret, access_token, access_token_secret)

    def get_hashtags (self, screen_name, hashtags_filter = [], max_tweets_count = 500, tweets_by_request = 200):
        """
        Return a list of counted hashtags
        ----------
        Parameters:
          screen_name - The user's screen name, without @
          hashtag_filter - An list of hashtags your want to filter, without the #
          max_tweets_count - The maximum number of tweets that must be retrieved
          nb_tweets_by_request - The number of tweets that must be retrieved with each request to the Twitter's servers
        """
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
        """
        Return a user's infos
        ----------
        Parameters:
          screen_name - The user's screen name, without @
        """
        try:
            user = self.api.get_user(screen_name = screen_name)
        except tweetpony.APIError as err:
            print "Error retrieving the user. Twitter returned error #%i and said: %s" % (err.code, err.description)
            quit()
        else :
            return user

    def get_nb_tweets_to_request (self, tweets_count, tweets_by_request, max_tweets_count):
        """
        Return the number of tweets that must be retrieved in the next request
        ----------
        Parameters:
          tweets_count - The number of tweets that have already been retrieved
          nb_tweets_by_request - The number of tweets that must be retrieved with each request to the Twitter's servers
          max_tweets_count - The maximum number of tweets that must be retrieved
        """
        if tweets_count + tweets_by_request > max_tweets_count:
          return max_tweets_count - tweets_count
        else :
          return tweets_by_request;

    def get_tweets (self, screen_name, count = None, max_id = None):
        """
        Return the user's tweets
        ----------
        Parameters:
          screen_name - The user's screen name, without @
          count - The number of tweets that must be retrieved
          max_id - The heighest id that must be retrieved
        """
        try:
            tweets = self.api.user_timeline(screen_name = screen_name, max_id = max_id,
            count = count, trim_user = True, exclude_replies = False,
            contributor_details = False)
        except tweetpony.APIError as err:
            print "Error retrieving the user's tweets. Twitter returned error #%i and said: %s" % (err.code, err.description)
            quit()
        else:
            return tweets

    def add_tweets_hashtags (self, tweets, hashtags, hashtags_filter = []):
        """
        Take an array of tweets, extracts the hashtags and add them to an array of hashtags
        ----------
        Parameters:
          tweets - A dictionary of tweets
          hashtags - A list of hashtags
          hashtag_filter - A list of hashtags your want to filter, without the #
        """
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
        """
        Return the new madIx
        ----------
        Parameters:
          tweets - A dictionary of tweets
        """
        last_id = int(tweets[-1]['id'])
        return last_id - 1

    def get_last_tweet_date (self, tweets):
        """
        Return the last tweet's date
        ----------
        Parameters:
          tweets - A dictionary of tweets
        """
        return tweets[-1]['created_at']

    def clean_string (self, text):
        """
        Remove the accents from a string and put in in lowercase
        ----------
        Parameters:
          text - A string
        """
        if isinstance(text, str):
            text = text.decode('utf-8')
        text = text.lower()
        return normalize('NFKD', text).encode('ASCII', 'ignore')

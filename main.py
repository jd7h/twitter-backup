#!/usr/bin/env python3
# coding: utf-8
import tweepy
from loguru import logger

from local_files import *
from secrets import *

api = None

def setup_api():
    global api
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_SECRET)
    logger.info('Authenticating with OAuth + Twitter API')
    api = tweepy.API(auth)


def get_statuses(twitter_api_method, old_ids, limit=None):
    """
    get all favorites from Twitter API
    """
    if twitter_api_method not in ['tweets','likes']:
        raise ValueError

    if twitter_api_method == 'tweets':
        cursor = tweepy.Cursor(api.user_timeline, screen_name=TARGET_USER, count=200, tweet_mode="extended").items(limit=limit)
    elif twitter_api_method == 'likes':
        cursor = tweepy.Cursor(api.get_favorites, screen_name=TARGET_USER, count=200, include_entities=True, tweet_mode="extended").items(limit=limit)

    # first pass over the obtained statuses
    found_statuses = []
    for status in cursor:
        # skip the ones we already know
        if status.id in old_ids:
            continue
        found_statuses.append(status)

        # is it a quote-RT?
        if status.is_quote_status and hasattr(status, "quoted_status"):  # sometimes the quoted tweet has disappeared
            # then add quoted status to the processing list
            found_statuses.append(status.quoted_status)
    return found_statuses
    
def scrape_and_save(TARGET_FILE, twitter_api_method, limit=None):
    # load the ids of tweets we already have
    if TARGET_FILE.exists():
        logger.info("Loading earlier data from " + str(TARGET_FILE))
        old_cache = load_data(TARGET_FILE)
    else:
        old_cache = []

    old_ids = [tweet["id"] for tweet in old_cache]

    logger.info("Requesting tweets using " + str(twitter_api_method))
    new_cache = get_statuses(twitter_api_method, old_ids, limit=limit)
    new_cache_json = [status._json for status in new_cache] # statuses from tweepy are not json serializable
    logger.info("Scraped " + str(len(new_cache_json)) + " new statuses from Twitter")
    all_cache = new_cache_json + old_cache
    save_json_to_file(all_cache, TARGET_FILE)


def main():
    limit = 5000
    
    logger.info("Start.")
    setup_api()    

    scrape_and_save(TWEETS_CACHE, 'tweets', limit=limit)
    scrape_and_save(LIKES_CACHE, 'likes', limit=limit)


    



if __name__ == '__main__':
    main()

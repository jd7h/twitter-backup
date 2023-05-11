#!/usr/bin/env python3
# coding: utf-8

import json
import logging
import os
import sys
from datetime import datetime
from urllib.parse import urlparse, urlunparse

import tweepy

from reporting import generate_reporting
from secrets import *

try:
    TARGET_USER = sys.argv[1]
except Exception as e:
    TARGET_USER = None

api = None


def get_old_likes():
    with open(f"data/likes_{TARGET_USER}.json", "r", encoding="utf-8") as f:
        try:
            return json.loads(f.read())
        except Exception as e:
            print("Error: " + str(e))
            return []


def save_likes(likes):
    if not os.path.isdir("data"):
        os.mkdir("data")

    with open(f"data/likes_{TARGET_USER}.json", "w", encoding="utf-8") as f:
        json.dump(likes, f, indent=2)


def get_new_likes(old_likes_ids):
    """
    get all favorites from Twitter API
    """
    # first pass over the obtained statuses
    liked_statuses = []
    for status in tweepy.Cursor(api.get_favorites,
                                TARGET_USER,
                                count=200,
                                include_entities=True
                                ).items():
        # skip the ones we already know
        if status.id in old_likes_ids:
            continue
        liked_statuses.append(status)

        # is it a quote-RT?
        if status.is_quote_status and hasattr(status, "quoted_status"):  # sometimes the quoted tweet has disappeared
            # then add quoted status to the processing list
            liked_statuses.append(status.quoted_status)

    # now we have all new liked statuses, process them
    likes = []
    for status in liked_statuses:
        like = {}
        likes.append(like)

        # twitter appends unecessary stuff at the end of the text of the tweet, so we just select what is proper text
        text = status.full_text[status.display_text_range[0]:status.display_text_range[1]]
        text = text.replace("\n", "<br />\n")
        # convert minified URLs found in text with the original URL value and add hyperlink
        if "urls" in status.entities:
            for url in status.entities['urls']:
                link = f'<a href="{url["expanded_url"]}">{url["display_url"]}</a>'
                text = text.replace(url['url'], link)
        like["text"] = text

        # handle pictures, videos and GIFs
        if hasattr(status, 'extended_entities'):
            if "media" in status.extended_entities:
                like["medias"] = []
                for media in status.extended_entities['media']:
                    # images go to medias key
                    if media["type"] in ("photo", "animated_gif", "video"):
                        like["medias"].append(media["media_url_https"])
                    # moving things go to videos key
                    if media["type"] in ("animated_gif", "video"):
                        if 'videos' not in like.keys():
                            like['videos'] = []
                        video_variants = { v.get('bitrate') : v.get('url') for v in media["video_info"].get('variants') if "video/" in v.get('content_type') }
                        url_of_biggest_bitrate = video_variants[max(video_variants.keys())]
                        clean_video_url = urlunparse(urlparse(url_of_biggest_bitrate)._replace(query='',params='',fragment=''))
                        like["videos"].append(clean_video_url)

        like["profile_image_url_https"] = status.user.profile_image_url_https
        like["screen_name"] = status.user.screen_name
        like["name"] = status.user.name
        like["id"] = status.id
        like["created_at"] = status.created_at.isoformat()

    return likes


def sample_liked_tweets():
    global api

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    print(str(datetime.now()) + " Start")

    # This handles Twitter authentication and the connection to Twitter Search API
    # we don't use the streaming API for this script
    # old authentication method
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_SECRET)
    print('Authenticating with OAuth + Twitter API')
    api = tweepy.API(auth)  
    
    return tweepy.Cursor(api.get_favorites, TARGET_USER, count=10, include_entities=True).items()
  


def main():
    global api

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    print(str(datetime.now()) + " Start")

    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_SECRET)
    print('Authenticating with OAuth + Twitter API')
    api = tweepy.API(auth) 

    # we have a cache of the already known liked tweets, so we don't re-fetch them and we keep them if they're deleted
    # or unliked!
    try:
        old_likes = get_old_likes()
    except:
        # surely means it's the first run, we don't have the cache built yet
        old_likes = []

    # get all new likes from API
    old_likes_ids = [tweet["id"] for tweet in old_likes]  # API returns all so we skip already known
    new_likes = get_new_likes(old_likes_ids)

    # prepend new liked tweets to the cache content
    all_likes = new_likes + old_likes

    # save new cache content
    save_likes(all_likes)

    # generate HTML reporting page based on all liked tweets
    generate_reporting(TARGET_USER, all_likes)

    print(str(datetime.now()) + " Bye!")


if __name__ == '__main__':
    main()

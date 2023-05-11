import datetime
import json
import os


from pathlib import Path
from urllib.request import urlretrieve

from loguru import logger

from local_files import *

   
def download_image(url, local_filename):
  if not local_filename.exists():
      try:
        urlretrieve(url, local_filename)
        return True
      except Exception as e:
        logger.error(e)
        return False
  return False
  
def download_video(url, local_filename):
    return download_image(url, local_filename) # does this work? 
  
def save_avatar(tweet):
    avatar_url = tweet.get('profile_image_url_https')
    avatar_url_extension = os.path.splitext(avatar_url)[1]
    avatar_filename = tweet.get('screen_name') + avatar_url_extension
    avatar_path = AVATAR_DIR / avatar_filename

    if not Path(avatar_path).exists():
        logger.info(f"Saving file in {avatar_path}")
        download_image(avatar_url, avatar_path)
    
    if not tweet.get('profile_image_url_local') or not str(avatar_path) in tweet.get('profile_image_url_local'):
        # we already have the file, just update the datapoint
        tweet["profile_image_url_local"] = str(avatar_path)

def save_media(tweet, media_url):
    tweet_date = datetime.datetime.fromisoformat(tweet['created_at'])
    media_filename = tweet_date.strftime("%Y_%m_") + Path(media_url).name
    media_path = MEDIA_DIR / media_filename
    
    if not Path(media_path).exists():
        logger.info(f"Saving file in {media_path}")
        download_image(media_url, media_path)
    
    if not tweet.get('medias_local') or str(media_path) not in tweet.get('medias_local'):
        if "medias_local" not in tweet.keys():
            tweet['medias_local'] = []
        tweet['medias_local'].append(str(media_path))      


def save_video(tweet, media_url):
    tweet_date = datetime.datetime.fromisoformat(tweet['created_at'])
    media_filename = tweet_date.strftime("%Y_%m_") + Path(media_url).name
    media_path = VIDEO_DIR / media_filename

    if not Path(media_path).exists():
        logger.info(f"Saving file in {media_path}")
        download_video(media_url, media_path)

    if not tweet.get('videos_local') or str(media_path) not in tweet.get('videos_local'):
        if "videos_local" not in tweet.keys():
            tweet['videos_local'] = []
        tweet['videos_local'].append(str(media_path))
        
def download_media_and_update_cache(cache_file):
    logger.info("Downloading media for cache file " + str(cache_file))
    status_cache = load_data(cache_file)

    # loop over tweets
    for tweet in status_cache:
        # download avatar if it does not exist yet
        save_avatar(tweet)
        if tweet.get('medias'):
            for media_url in tweet.get('medias'):
                save_media(tweet, media_url)
        if tweet.get('videos'):
            for media_url in tweet.get('videos'):
                save_video(tweet, media_url)

    # save json with updated media paths
    backup_file(cache_file)
    with open(cache_file,'w') as outfile:
        outfile.write(json.dumps(status_cache, indent=2))
        
def main():
    if not LIKES_FILE.exists() and not TWEETS_FILE.exists():
        logger.error("Both the likes cache and the tweets cache could not be found. Terminating...")
        return     
        
    # make dirs for media if necessary
    init_media_dirs()

    download_media_and_update_cache(LIKES_FILE)
    download_media_and_update_cache(TWEETS_FILE)


if __name__ == '__main__':
    main()



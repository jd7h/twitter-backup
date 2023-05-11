import datetime
import json
import os
import shutil

from pathlib import Path
from urllib.request import urlretrieve

from loguru import logger

try:
    TARGET_USER = sys.argv[1]
except Exception as e:
    TARGET_USER = None

LIKED_TWEETS = ROOT_DIR / f"likes_{TARGET_USER}.json"
ROOT_DIR = Path("data")
AVATAR_DIR = ROOT_DIR / "avatars"
MEDIA_DIR = ROOT_DIR / "images"
VIDEO_DIR = ROOT_DIR / "videos"

def make_directory_if_needed(directory_path):
    if not directory_path.exists():
        directory_path.mkdir()

def backup_file(file_path):
    backup_file_path = file_path.parent / (file_path.name + '.bak')
    shutil.copy(file_path, backup_file_path)
    
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
    if not tweet.get('profile_image_url_local') or str(avatar_path) not in tweet.get('profile_image_url_local') or not Path(avatar_path).exists():
        logger.info(f"Saving file in {avatar_path}")
        download_image(avatar_url, avatar_path)
        tweet["profile_image_url_local"] = str(avatar_path)

def save_media(tweet, media_url):
    tweet_date = datetime.datetime.fromisoformat(tweet['created_at'])
    media_filename = tweet_date.strftime("%Y_%m_") + Path(media_url).name
    media_path = MEDIA_DIR / media_filename
    if not tweet.get('medias_local') or str(media_path) not in tweet.get('medias_local') or not Path(media_path).exists():
        logger.info(f"Saving file in {media_path}")
        download_image(media_url, media_path)
        if "medias_local" not in tweet.keys():
            tweet['medias_local'] = []
        tweet['medias_local'].append(str(media_path))      

def save_video(tweet, media_url):
    tweet_date = datetime.datetime.fromisoformat(tweet['created_at'])
    media_filename = tweet_date.strftime("%Y_%m_") + Path(media_url).name
    media_path = VIDEO_DIR / media_filename
    if not tweet.get('videos_local') or str(media_path) not in tweet.get('videos_local') or not Path(media_path).exists():
        logger.info(f"Saving file in {media_path}")
        download_video(media_url, media_path)
        if "videos_local" not in tweet.keys():
            tweet['videos_local'] = []
        tweet['videos_local'].append(str(media_path))
        
def main():
    
    # load json
    with open(LIKED_TWEETS,'r') as likes_file:
        liked_tweets = json.loads(likes_file.read())

    # make dirs for media
    make_directory_if_needed(AVATAR_DIR)
    make_directory_if_needed(MEDIA_DIR)
    make_directory_if_needed(VIDEO_DIR)

    # loop over tweets
    for tweet in liked_tweets:
        # download avatar if it does not exist yet
        save_avatar(tweet)
        if tweet.get('medias'):
            for media_url in tweet.get('medias'):
                save_media(tweet, media_url)
        if tweet.get('videos'):
            for media_url in tweet.get('videos'):
                save_video(tweet, media_url)

    # save json with updated paths
    backup_file(LIKED_TWEETS)
    with open(LIKED_TWEETS,'w') as likes_file:
        likes_file.write(json.dumps(liked_tweets, indent=2))


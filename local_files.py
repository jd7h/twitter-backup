import sys
import json
import shutil
from pathlib import Path

try:
    TARGET_USER = sys.argv[1]
except Exception as e:
    TARGET_USER = None

DATA_ROOT = Path("data/")
USER_DIR = DATA_ROOT / TARGET_USER

LIKES_FILE = USER_DIR / "likes.json" # clean data
LIKES_CACHE = USER_DIR / "likes_cache.json" # full data
LIKES_HTML = USER_DIR / "likes.html"

TWEETS_FILE = USER_DIR / "tweets.json" # clean data
TWEETS_CACHE = USER_DIR / "tweets_cache.json" # full data
TWEETS_HTML = USER_DIR / "tweets.html"

AVATAR_DIR = USER_DIR / "avatars"
MEDIA_DIR = USER_DIR / "images"
VIDEO_DIR = USER_DIR / "videos"

def init_dirs():
    if not DATA_ROOT.is_dir():
        DATA_ROOT.mkdir()
    if not USER_DIR.is_dir():
        USER_DIR.mkdir()
        
def init_media_dirs():
    for d in [AVATAR_DIR, MEDIA_DIR, VIDEO_DIR]:
        if not d.is_dir():
            d.mkdir()

def load_data(some_file):
    with open(some_file, "r", encoding="utf-8") as f:
        try:
            return json.loads(f.read())
        except Exception as e:
            logger.error("Error: " + str(e))
            return []

def save_json_to_file(data, path):
    init_dirs()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
def backup_file(file_path):
    backup_file_path = file_path.parent / (file_path.name + '.bak')
    shutil.copy(file_path, backup_file_path)

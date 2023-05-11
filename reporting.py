import datetime
import json
import os
import shutil
import sys

from jinja2 import Template

from local_files import *

def generate_reporting(target_html_page, tweets):
    # if we don't already have the output folder then create it
    # (otherwise we only re-create the HTML page)

    # load template
    with open("index_template.html", "r", encoding="utf-8") as f:
        index_tpl = Template(f.read())
    # process template with likes data
    index_data = index_tpl.render(user_dir=str(USER_DIR), tweets=tweets)
    # write HTML output
    with open(target_html_page, "w", encoding="utf-8") as f:
        f.write(index_data)


if __name__ == '__main__':
    likes = load_data(LIKES_FILE)
    tweets = load_data(TWEETS_FILE)
    
    for like in likes:
        like['created_at_formatted'] = datetime.datetime.fromisoformat(like['created_at']).strftime("%Y-%m-%d %H:%M")
        
    for tweet in tweets:
        tweet['created_at_formatted'] = datetime.datetime.fromisoformat(tweet['created_at']).strftime("%Y-%m-%d %H:%M")
    
    generate_reporting(LIKES_HTML, likes)
    generate_reporting(TWEETS_HTML, tweets)

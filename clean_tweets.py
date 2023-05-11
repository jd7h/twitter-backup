from tweepy.models import Status
from urllib.parse import urlparse, urlunparse

from loguru import logger

from local_files import *
from reporting import generate_reporting

def clean_statuses(statuses):
    # now we have all new statuses, process them
    results = []
    
    for status in statuses:
        status = Status.parse(api=None, json=status)
        datapoint = {}

        try:
            # twitter appends unnecessary stuff at the end of the text of the tweet, so we just select what is proper text
            try:
                text = status.full_text[status.display_text_range[0]:status.display_text_range[1]]
            except Exception as e:
                logger.error(f"Tweet with id {status.id} has error " + str(e))
                logger.debug("Trying text attribute instead...")
                logger.debug(f"{status.text}")
                text = status.text
            text = text.replace("\n", "<br />\n")

            # convert minified URLs found in text with the original URL value and add hyperlink
            if "urls" in status.entities:
                for url in status.entities['urls']:
                    link = f'<a href="{url["expanded_url"]}">{url["display_url"]}</a>'
                    text = text.replace(url['url'], link)
            datapoint["text"] = text

            # handle pictures, videos and GIFs
            if hasattr(status, 'extended_entities'):
                if "media" in status.extended_entities:
                    datapoint["medias"] = []
                    for media in status.extended_entities['media']:
                        # images go to medias key
                        if media["type"] in ("photo", "animated_gif", "video"):
                            datapoint["medias"].append(media["media_url_https"])
                        # moving things go to videos key
                        if media["type"] in ("animated_gif", "video"):
                            if 'videos' not in datapoint.keys():
                                datapoint['videos'] = []
                            video_variants = { v.get('bitrate') : v.get('url') for v in media["video_info"].get('variants') if "video/" in v.get('content_type') }
                            url_of_biggest_bitrate = video_variants[max(video_variants.keys())]
                            clean_video_url = urlunparse(urlparse(url_of_biggest_bitrate)._replace(query='',params='',fragment=''))
                            datapoint["videos"].append(clean_video_url)

            datapoint["profile_image_url_https"] = status.user.profile_image_url_https
            datapoint["screen_name"] = status.user.screen_name
            datapoint["name"] = status.user.name
            datapoint["id"] = status.id
            datapoint["created_at"] = status.created_at.isoformat()
        except Exception as e:
            logger.error(f"Tweet with id {status.id} has error " + str(e))
            print(status)

        results.append(datapoint)

    return results
    
def clean_cache(cache_file, target_file, overwrite):
    if not cache_file.exists():
        logger.error(f"Cache {cache_file} does not exist. Terminating...")
        return

    if target_file.exists() and not overwrite:
        logger.error(f"Target file {target_file} does already exist but overwrite is set to False. Terminating...")
        return
    
    tweet_cache = load_data(cache_file)
    logger.info(f"Loaded {len(tweet_cache)} statuses from cache file {cache_file}")
    cleaned_data = clean_statuses(tweet_cache)
    
    save_json_to_file(cleaned_data, target_file)

def main():
    overwrite = False

    clean_cache(LIKES_CACHE, LIKES_FILE, overwrite=overwrite)
    clean_cache(TWEETS_CACHE, TWEETS_FILE, overwrite=overwrite)

    # generate HTML reporting page based on all liked tweets
    # generate_reporting(TARGET_USER, all_likes)

    logger.info("Finished.")
        
if __name__ == '__main__':
    main()

import configparser
import json
import re
import sqlite3
import time
import youtube_dl
import requests
from helpers import fix_urls
from transformers.base_transformer import BaseTransformer, TransformerResultBundle

target_sites = ["https://twitter.com"]

config = configparser.RawConfigParser()
config.read("config.conf")
BearerToken = config["twitter"]["BearerToken"]

con = sqlite3.connect('tweet_cache.db', check_same_thread=False)

command = 'create table if not exists single_tweets (tweet_id text, data text)'

cur = con.cursor()
cur.execute(command)
con.commit()
con.close()

class TwitterTransformer(BaseTransformer):
    def __init__(self, response_data):
        super(TwitterTransformer, self).__init__(response_data)
        self.target_sites = self.target_sites + target_sites

    def transform_one(self, bundle: TransformerResultBundle):
        tweet_path = bundle.link.attrs["href"]
        tweet_id = tweet_path.split("/")[-1].split("?")[0]
        result = self.render_tweet_by_id(tweet_id, frame=not (len(bundle.tree)==len(bundle.link)))
        bundle.content_object.delete_card()
        return result

    def create_twitter_header(self, bearer_token):
        headers = {"Authorization": "Bearer {}".format(bearer_token)}
        return headers

    def get(self, path):
        return requests.get(path, headers = self.create_twitter_header(BearerToken)).text

    def check_cache_for_tweet(self, id):
        con = sqlite3.connect('tweet_cache.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("select data from single_tweets where tweet_id = (?)", (id,))
        results = cur.fetchall()
        con.close()
        if results:
            return json.loads(results[0][0])
        return False

    def get_tweets_by_ids(self, id_list):
        id_string = ",".join(id_list)
        result = self.get("https://api.twitter.com/2/tweets?ids={}&tweet.fields=author_id,conversation_id,created_at,in_reply_to_user_id,referenced_tweets&expansions=attachments.media_keys,author_id,in_reply_to_user_id,referenced_tweets.id&media.fields=height,media_key,url,width&user.fields=name,username".format(id_string))
        time.sleep(1*len(id_list)) #rate limiter
        return json.loads(result)

    def render_tweet_by_id(self, id, allow_qt=True, frame=False):
        template = open("templates/tweet_template.html").read()
        result = self.check_cache_for_tweet(id)
        if not result:
            result =  self.get_tweets_by_ids([id])
            con = sqlite3.connect('tweet_cache.db', check_same_thread=False)
            cur = con.cursor()
            cur.execute("insert into single_tweets values (?,?)", (id,json.dumps(result)))
            con.commit()
            con.close()
        print(id)
        print("RESULT", result)
        user_id = result["data"][0]["author_id"]
        human_name = [u["name"] for u in result["includes"]["users"] if u["id"] == user_id][0]
        user_name = [u["username"] for u in result["includes"]["users"] if u["id"] == user_id][0]
        content = result["data"][0]["text"]
        referenced_tweets = result["data"][0].get("referenced_tweets",None)
        quote_tweet = ""
        #import ipdb; ipdb.set_trace()
        if referenced_tweets:
            parent_id = [r["id"] for r in referenced_tweets if r["type"] == "replied_to"]    
            if allow_qt:
                qt = [r["id"] for r in referenced_tweets if r["type"] == "quoted"]
                if qt:
                    quote_tweet =  self.render_tweet_by_id(qt[0], allow_qt=False, frame=True)

        avatar = '<img src="https://unavatar.io/twitter/{}" width="100%" height="100%" />'.format(user_name)
        photos = []
        media_count = len(result["includes"].get("media", []))
        for p in result["includes"].get("media", []):
            print(result["includes"].get("media", []))
            if p["type"] in ["video", "animated_gif"]:
                ydl_opts = {'outtmpl': '{}.mp4'.format(id)}
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    #ydl.download(["https://twitter.com/{}/status/{}".format(user_name, id)])
                    #TODO: come up with a sensible way to handle video
                    pass
            else:
                photo_template = open("templates/twitter_photo.html").read()
                photos.append(photo_template.format(url=p["url"],width=((93/media_count)-(media_count)/2)))
        print(photos)
        photo_string = "".join([p for p in photos])
        result = template.format(avatar=avatar, content=fix_urls(content+" "), human_name=human_name, user_name=user_name, photos=photo_string, quote_tweet=quote_tweet)
        if frame:
            result = '<div style="border-color: #000000; padding:5px; border-style: solid;" >' + result +  '</div>'
        return result


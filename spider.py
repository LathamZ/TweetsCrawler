#!/usr/bin/env python
import tweepy
import sys, os
import csv
import logging
import traceback, signal
import time, random
import json
from tweepy.error import TweepError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
from tweets_crawler import db as DB


class TweepySpider():
    auths = []
    proxies = []
    credentials_path = "credentials.csv"
    proxy_path = "proxies"
    task_type = "tweet"
    target_name = None
    run = True
    db = None

    def init_assets(self):
        with open(self.credentials_path) as f:
            creds_reader = csv.reader(f)
            for row in creds_reader:
                consumer_key = row[0].strip()
                consumer_secret = row[1].strip()
                access_token = row[2].strip()
                access_token_secret = row[3].strip()
                auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
                auth.set_access_token(access_token, access_token_secret)
                self.auths.append(auth)
        with open(self.proxy_path) as f:
            for line in f:
                if line.strip() != "":
                    self.proxies.append(line.strip())
        self.db = DB.DB()

    def getNextApi(self, category, resource_url):
        try_count = 0
        while self.run:
            logging.warning("start to get api for %s" % resource_url)
            if try_count / len(self.auths) >= 0.9:
                logging.warning("2/3 auth's limit for %s have been reached...relax for some time" % resource_url)
                raise IOError("reach api limit...put this task back and try again later")

            try:
                cur_auth = self.auths[random.randint(0, len(self.auths) - 1)]
                cur_proxy = self.proxies[random.randint(0, len(self.proxies) - 1)]
                api = tweepy.API(cur_auth, proxy = cur_proxy)
                # api = tweepy.API(cur_auth)
                rate_limit = api.rate_limit_status()

                if "code" in rate_limit and rate_limit["code"] == 32:
                    self.auths.remove(cur_auth)
                    logging.warning("invalid auth info..remove it  %d left" % len(self.auths))
                    continue

                limits = rate_limit["resources"][category][resource_url]
                if limits["remaining"] > 0:
                    logging.warning("get api successfully with remaining count %d" % limits["remaining"])
                    return api
                else:
                    logging.warning("auth reaches limits...skip")

                try_count += 1
            except KeyboardInterrupt:
                logging.warning("KeyboardInterrupt detected exit program")
                self.run = False
            except tweepy.RateLimitError as e:
                logging.warning("2/3 auth's limit for %s have been reached...relax for some time" % resource_url)
                time.sleep(60 * random.randint(5, 15))
                continue
            except TweepError as e:
                if e.api_code == 32:
                    self.auths.remove(cur_auth)
                    logging.warning("invalid auth info..remove it  %d left" % len(self.auths))
                else:
                    traceback.print_exc()
            except:
                traceback.print_exc()
                continue

    def __init__(self, target_name):
        self.init_assets()
        self.target_name = target_name
        logging.warning("auths count: %d  proxy count: %d" % (len(self.auths), len(self.proxies)))

    def usingCursor(self, acc, category, resource_url, resource_request_method, resources_extract_method, *args, **kargs):
        cursor = tweepy.Cursor(self.getCallAddr(category, resource_url, resource_request_method)
            , *args, **kargs).items()

        while self.run:
            try:
                resource_item = cursor.next()
            except KeyboardInterrupt:
                logging.warning("KeyboardInterrupt detected exit program")
                self.run = False
            except tweepy.RateLimitError:
                logging.warning("RateLimitError when iterating resources...changing auth")
                cursor.page_iterator.method = self.getCallAddr(category, resource_url, resource_request_method)
                continue
            except tweepy.TweepError as te:
                if "429" in te.message:
                    logging.warning("%s when iterating resources...changing auth" % te.message)
                    cursor.page_iterator.method = self.getCallAddr(category, resource_url, resource_request_method)
                elif "401" in te.message or "Not authorized" in te.message or "User has been suspended" in te.message:
                    logging.warning("%s is protected....skip" % acc.screen_name)
                    self.storeProtectedAccount(acc.screen_name)
                    break
                elif "404" in te.message:
                    logging.warning("%s is not found....skip" % acc.screen_name)
                    self.storeProtectedAccount(acc.screen_name)
                    break
                else:
                    logging.error("Unexpected Api Error When cursoring: %s" % te.message)

                continue
            except StopIteration:
                logging.warning("no more %s to iterate for %s...out" % (resource_url, acc.screen_name))
                break

            resources_extract_method(acc, resource_item)


    def getCallAddr(self, category, resource_url, resource_request_method):
        return getattr(self.getNextApi(category, resource_url), resource_request_method)

    def doScrapy(self):
        batch_count = 0
        while self.run:
	    time.sleep(5)
            username =  self.target_name
            task_type = "tweet"

            try:
                acc = self.getNextApi("users", "/users/show/:id").get_user(username)
                logging.warning("start crawl %s's tweet" %  username)
                self.exploreTweets(acc)
                logging.warning("finish task for %s" % username)
            except KeyboardInterrupt:
                logging.warning("KeyboardInterrupt detected exit program")
                self.run = False
            except tweepy.TweepError as e:
                if "User not found" in str(e.message):
                    logging.warning("invalid username %s..delete related task %s" % (username, task))
                elif "User has been suspended" in str(e.message):
                    logging.warning("%s is suspended....skip" % username)
                else:
                    traceback.print_exc()
                    logging.error("Unexpected TweepErrory error:", sys.exc_info()[0])
            except IOError as e:
                logging.warning("reach api limit...put back task")
            except:
                traceback.print_exc()
                logging.error("Unexpected error:", sys.exc_info()[0])

    def extractStatus(self, acc, status):
        tweet = self.extractTweet(status)
        self.export_item(tweet)


    def exploreTweets(self, acc):
        self.usingCursor(acc
            , "statuses", "/statuses/user_timeline", "user_timeline"
            , self.extractStatus, tweet_mode="extended"
            , id = acc.screen_name, include_rts = True)

    def extractTweet(self, status):
        tweet = {}
        tweet["tweet_id"] = status.id_str
        tweet["tweetee"] = status.author.screen_name
        tweet["tweetee_id"] = status.author.id_str
        tweet["tweetee_name"] = status.author.name
        tweet["date"] = str(int(time.mktime(status.created_at.timetuple())))
        tweet["forward_count"] = str(status.retweet_count)
        tweet["upvote_count"] = str(status.favorite_count)
        tweet["content"] = status.full_text

        if "hashtags" in status.entities:
            tags = []
            for t in status.entities["hashtags"]:
                tags.append(t["text"])

            tweet["tags"] = ",".join(tags)

        if "media" in status.entities:
            videos = []
            pics = []
            for m in status.entities["media"]:
                if m["type"] == "photo":
                    pics.append(m["media_url"])
                else:
                    videos.append(m["media_url"])

            tweet["pics"] = ",".join(pics)
            tweet["videos"] = ",".join(videos)

        tweet["lang"] = status.lang

        if hasattr(status, "source"):
            tweet["source"] = status.source

        return tweet

    def export_item(self, item):
        key = item["tweetee"] + "$" + item["date"]
        value = json.dumps(item)
        self.db.set(key, value)

def doWork(name):
    try:
        spider = TweepySpider(name)
        logging.warning("start spider for " + name)
        spider.doScrapy()
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex)
    except:
        traceback.print_exc()
        logging.error("Unexpected error:", sys.exc_info()[0])

if __name__ == "__main__":
    name = sys.argv[1]
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename = 'logs/' + name + '_out.log',level=logging.WARNING, format = log_format)
    doWork(name)

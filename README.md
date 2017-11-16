# tweets_crawler
Crawl tweets from twitter of certain person by account name

## Dependencies

- tweepy
- redis (along with redis itself)

## Usage

make sure you have *credentials.csv* filled with valid credentials.

the format of *credentials.csv* is:

| consumer_key | consumer_secret | access_token | access_token_secret |
| ------------ | --------------- | ------------ | ------------------- |
|              |                 |              |                     |

if you need a proxy to get access to twitter.com, put the proxy into *proxies* file one proxy per line.

`start-all.sh` to start

`stop-all.sh` to stop

`restart-all.sh` to restart

`do-scrape.sh` to start a crawl of all then stop all after 30 min and then do the summary

`do-rotate.sh` will crawl the candidates one by one




import os

import tweepy

auth = tweepy.OAuthHandler(
    os.getenv("TWITTER_API_KEY"),
    os.getenv("TWITTER_API_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_SECRET"),
)

api = tweepy.API(auth)


def get_user_tweets(username: str, num_tweets: int = 5):
    tweets = api.user_timeline(screen_name=username, count=num_tweets)
    processed_tweets = []
    for tweet in tweets:
        if "RT @" not in tweet.text and not tweet.text.startswith("@"):
            processed_tweets.append(
                {"text": tweet.text, "url": f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"}
            )
    return processed_tweets

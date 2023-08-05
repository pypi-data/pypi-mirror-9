"""
Script to generate keyword statistics for smapp twitter mongo collections.

Usage: python gen_keyword_stats.py -h

or, if module is installed: python -m smapp_collection_stats.gen_keyword_stats -h

@jonathanronen 2015/1
"""

import argparse
from collections import defaultdict
from datetime import datetime, timedelta
from smappPy.tweet_filter import within_geobox
from smapp_toolkit.twitter import MongoTweetCollection

def get_tweets_iter(toolkit_collection, since, until, cap):
    """
    Returns a pymongo cursor to iterate over a maximum of `cap` tweets,
    between `since` and `until`. Uses sampling if there are really more
    tweets than `cap` in that period.
    """
    tweets = toolkit_collection.since(since).until(until)
    count = tweets.count()
    sample_rate = cap/count if count > cap else None

    if sample_rate:
        tweets = tweets.sample(sample_rate)

    return tweets

def contains_keyword(tweet, word):
    return word.lower() in tweet['text'].lower()

def tweeted_by(tweet, id_str):
    return tweet['user']['id_str'] == id_str

def retweet_of(tweet, id_str):
    if 'retweeted_status' not in tweet:
        return False
    return tweet['retweeted_status']['user']['id_str'] == id_str

def reply_to(tweet, id_str):
    return tweet['in_reply_to_user_id_str'] == id_str

def calculate_and_save(server, port, database, username, password, since, until, cap):
    toolkit_collection = MongoTweetCollection(
        address=server,
        port=port,
        dbname=database,
        username=username,
        password=password
        )

    tweets = get_tweets_iter(
        toolkit_collection,
        since,
        until,
        cap
        )

    filter_criteria = list(toolkit_collection._mongo_database[toolkit_collection.collection_metadata['filter_criteria_collection']].find())

    keywordstats_collection = toolkit_collection._mongo_database[toolkit_collection.collection_metadata.get('keywordstats_collection', 'tweets_keywordstats')]

    stats = {
            "start_time": since,
            "end_time": until,
            "stat-type": "filter-criteria-hits",
            "stats": []
        }

    fc_counts = defaultdict(lambda: 0)
    for tweet in tweets:
        for fc in filter_criteria:
            if fc['filter_type'] == 'track': # filter criterion is a keyword
                if contains_keyword(tweet, fc['value']):
                    fc_counts[fc['_id']] += 1
            elif fc['filter_type'] == 'follow': # filter criterion is a twitter id to follow
                if tweeted_by(tweet, fc['value']) or retweet_of(tweet, fc['value']) or reply_to(tweet, fc['value']):
                    fc_counts[fc['_id']] += 1
            elif fc['filter_type'] == 'geo': # filter criterion is geobox
                if within_geobox(tweet, *fc['value']):
                    fc_counts[fc['_id']] += 1

    stats['stats'] = [{'fc_id': key, 'value': value} for key,value in fc_counts.items()]
    keywordstats_collection.save(stats)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", default="smapp-data.bio.nyu.edu", help="MongoDB host. [smapp-data.bio.nyu.edu]")
    parser.add_argument("-p", "--port", type=int, default=27011, help="MongoDB port. [27011]")
    parser.add_argument("-u", "--username", default="smapp_readWrite", help="username for MongoDB. [smapp_readWrite]")
    parser.add_argument("-w", "--password", default=None, help="password for MongoDB. [None]")
    parser.add_argument("-d", "--database", required=True , help="MongoDB database name")

    parser.add_argument("-t", "--time-back", type=int, default=60, help="Length of time slice (in minutes) to generate statistics for. [60]")
    parser.add_argument("-c", "--cap", type=float, default=10000.0, help="Cap of how many tweets to consider. If there are more, sample to reduce. [10,000]")

    args = parser.parse_args()

    until = datetime.utcnow()
    since = until - timedelta(minutes=args.time_back)

    calculate_and_save(args.server, args.port, args.database, args.username, args.password, since, until, args.cap)

if __name__ == '__main__':
    main()